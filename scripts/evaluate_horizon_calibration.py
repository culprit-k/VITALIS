#!/usr/bin/env python3
"""Evaluate calibrated future-Challenge-label forecasts without Set-B tuning.

For each horizon and seed, Set A eligible patients are split into train,
calibration, and untouched operating-point holdout partitions. The base model
is fitted on train; Platt recalibration is fitted on calibration only. A fixed
threshold grid is reported on the untouched Set-A partition and Set B. Set B
is evaluation-only and never influences fitting or threshold selection.
"""
from __future__ import annotations

import argparse
import gc
import json
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from vitalis.horizon import build_future_challenge_targets, evaluate_horizon_alerts
from vitalis.calibration_uncertainty import (
    patient_cluster_bootstrap_calibration_metrics,
    patient_cluster_bootstrap_paired_model_metrics,
)
from vitalis.utility import (
    evaluate_utility_operating_points,
    patient_cluster_bootstrap_utility_uncertainty,
)

BASE = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2",
    "BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN",
    "Alkalinephos", "Calcium", "Chloride", "Creatinine", "Bilirubin_direct",
    "Glucose", "Lactate", "Magnesium", "Phosphate", "Potassium",
    "Bilirubin_total", "TroponinI", "Hct", "Hgb", "PTT", "WBC",
    "Fibrinogen", "Platelets", "Age", "Gender", "Unit1", "Unit2",
    "HospAdmTime", "ICULOS",
]
EXPECTED = {
    "A": {"patients": 20336, "rows": 790215, "positive_labels": 17136},
    "B": {"patients": 20000, "rows": 761995, "positive_labels": 10780},
}
# Predeclared research grid; these are not clinical cutoffs and no threshold is selected.
THRESHOLDS = (0.001, 0.005, 0.01, 0.05, 0.5)
CALIBRATION_BINS = (0.0, 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 0.5, 1.0)


def load_cache(cache_dir: Path, cohort: str):
    meta = json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))
    X = np.load(cache_dir / "X.npy", mmap_mode="r")
    y = np.load(cache_dir / "y.npy", mmap_mode="r")
    groups = np.load(cache_dir / "g.npy", mmap_mode="r")
    if X.ndim != 2 or y.ndim != 1 or groups.ndim != 1:
        raise ValueError(f"Set {cohort} cache arrays have invalid dimensions")
    if X.shape[0] != meta.get("row_count") or len(y) != len(X) or len(groups) != len(X):
        raise ValueError(f"Set {cohort} cache row counts do not match metadata")
    if X.shape[1] != len(meta.get("columns", [])):
        raise ValueError(f"Set {cohort} feature count does not match metadata")
    if len(np.unique(groups)) != meta.get("patient_count") or not np.isin(y, [0, 1]).all():
        raise ValueError(f"Set {cohort} patient groups or binary labels are invalid")
    return meta, X, y, groups


def validate_official_cohort(meta, y, groups, cohort: str) -> None:
    expected = EXPECTED[cohort]
    actual = {"patients": int(len(np.unique(groups))), "rows": int(len(y)), "positive_labels": int(np.asarray(y).sum())}
    if actual != expected or meta.get("patient_count") != expected["patients"] or meta.get("row_count") != expected["rows"]:
        raise ValueError(f"Set {cohort} official cohort integrity mismatch: expected {expected}, got {actual}")


def patient_disjoint_three_way_split(labels: np.ndarray, patient_ids: np.ndarray, seed: int):
    """Split eligible target rows into patient-disjoint 60/20/20 train/calibration/holdout."""
    y, groups = np.asarray(labels), np.asarray(patient_ids)
    if y.ndim != 1 or groups.ndim != 1 or len(y) != len(groups) or len(groups) < 3 or len(np.unique(groups)) < 3:
        raise ValueError("aligned labels and at least three eligible patients are required")
    first = GroupShuffleSplit(n_splits=1, test_size=0.4, random_state=seed)
    train_idx, rest_idx = next(first.split(np.zeros(len(groups)), y, groups))
    second = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed + 1)
    cal_local, hold_local = next(second.split(np.zeros(len(rest_idx)), y[rest_idx], groups[rest_idx]))
    cal_idx, hold_idx = rest_idx[cal_local], rest_idx[hold_local]
    sets = [set(np.unique(groups[idx]).tolist()) for idx in (train_idx, cal_idx, hold_idx)]
    if any(not idx.size for idx in (train_idx, cal_idx, hold_idx)) or any(
        sets[i] & sets[j] for i in range(3) for j in range(i + 1, 3)
    ):
        raise RuntimeError("three-way patient split is empty or has patient overlap")
    return train_idx, cal_idx, hold_idx


def fit_platt_recalibrator(labels: np.ndarray, probabilities: np.ndarray) -> LogisticRegression:
    y, p = np.asarray(labels, dtype=np.int8), np.asarray(probabilities, dtype=np.float64)
    if y.ndim != 1 or p.ndim != 1 or len(y) == 0 or len(y) != len(p):
        raise ValueError("calibration labels and probabilities must be nonempty aligned vectors")
    if not np.isin(y, [0, 1]).all() or len(np.unique(y)) < 2:
        raise ValueError("calibration labels must contain both classes")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("calibration probabilities must be finite and in [0, 1]")
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    logits = np.log(pc / (1 - pc)).reshape(-1, 1)
    return LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000).fit(logits, y)


def apply_platt_recalibrator(model: LogisticRegression, probabilities: np.ndarray) -> np.ndarray:
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 1 or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be a finite vector in [0, 1]")
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    logits = np.log(pc / (1 - pc)).reshape(-1, 1)
    return np.clip(model.predict_proba(logits)[:, 1], 1e-6, 1 - 1e-6)


def probability_metrics(labels: np.ndarray, probabilities: np.ndarray) -> dict[str, object]:
    y, p = np.asarray(labels, dtype=np.int8), np.asarray(probabilities, dtype=np.float64)
    if y.ndim != 1 or p.ndim != 1 or len(y) == 0 or len(y) != len(p):
        raise ValueError("labels and probabilities must be nonempty aligned vectors")
    if not np.isin(y, [0, 1]).all() or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("labels or probabilities are invalid")
    prevalence = float(y.mean())
    p_clip = np.clip(p, 1e-12, 1 - 1e-12)
    edges = np.asarray(CALIBRATION_BINS)
    bins = []
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        mask = (p >= lo) & ((p < hi) if i < len(edges) - 2 else (p <= hi))
        if mask.any():
            bins.append({"lower": float(lo), "upper": float(hi), "rows": int(mask.sum()),
                         "mean_predicted": float(p[mask].mean()), "observed_prevalence": float(y[mask].mean())})
    ece = sum(b["rows"] / len(y) * abs(b["mean_predicted"] - b["observed_prevalence"]) for b in bins)
    return {
        "rows": int(len(y)), "positive_rows": int(y.sum()), "prevalence": prevalence,
        "mean_predicted_probability": float(p.mean()),
        "brier_score": float(brier_score_loss(y, p)),
        "constant_prevalence_brier_reference": float(prevalence * (1 - prevalence)),
        "log_loss": float(log_loss(y, p_clip, labels=[0, 1])),
        "auroc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "auprc": float(average_precision_score(y, p)),
        "fixed_bin_expected_calibration_error": float(ece),
        "calibration_bins": bins,
    }


def threshold_metrics(labels: np.ndarray, probabilities: np.ndarray, threshold: float) -> dict[str, object]:
    y, p = np.asarray(labels, dtype=np.int8), np.asarray(probabilities, dtype=np.float64)
    pred = p >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"threshold": float(threshold), "predicted_positive_rows": int(pred.sum()),
            "sensitivity": float(tp / (tp + fn)) if tp + fn else None,
            "specificity": float(tn / (tn + fp)) if tn + fp else None,
            "ppv": float(tp / (tp + fp)) if tp + fp else None,
            "npv": float(tn / (tn + fn)) if tn + fn else None,
            "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}}


def _predict(model, X, row_indices, feature_indices, chunk_rows):
    result = np.empty(len(row_indices), dtype=np.float64)
    for start in range(0, len(row_indices), chunk_rows):
        end = min(start + chunk_rows, len(row_indices))
        result[start:end] = model.predict_proba(X[np.ix_(row_indices[start:end], feature_indices)])[:, 1]
    return result


def evaluate_one(meta_a, Xa, ya, ga, meta_b, Xb, yb, gb, *, horizon: int, seed: int, chunk_rows: int, refractory_hours: int, bootstrap_replicates: int, missed_window_costs: list[float] = (1.0, 10.0, 100.0, 500.0, 1000.0), alert_cost: float = 1.0):
    target_a = build_future_challenge_targets(ya, ga, horizon)
    target_b = build_future_challenge_targets(yb, gb, horizon)
    columns = meta_a["columns"]
    if columns != meta_b["columns"]:
        raise ValueError("Set A and Set B feature schemas differ")
    col = {name: i for i, name in enumerate(columns)}
    static = np.asarray([col[name] for name in BASE if name in col], dtype=np.int64)
    if not len(static):
        raise ValueError("no baseline features found")
    train_idx, cal_idx, hold_idx = patient_disjoint_three_way_split(target_a.targets, target_a.patient_ids, seed)
    if len(np.unique(target_a.targets[train_idx])) < 2:
        raise ValueError("Set A training partition has one class")
    results = {"horizon_hours": horizon, "seed": seed,
               "split": "patient-disjoint 60% train / 20% calibration / 20% untouched Set-A operating-point holdout",
               "patient_counts": {"set_a_train": int(len(np.unique(target_a.patient_ids[train_idx]))),
                                  "set_a_calibration": int(len(np.unique(target_a.patient_ids[cal_idx]))),
                                  "set_a_untouched_holdout": int(len(np.unique(target_a.patient_ids[hold_idx]))),
                                  "set_b_evaluation": int(len(np.unique(target_b.patient_ids)))},
               "row_counts": {"set_a_train": int(len(train_idx)), "set_a_calibration": int(len(cal_idx)),
                              "set_a_untouched_holdout": int(len(hold_idx)), "set_b_evaluation": int(len(target_b.targets))},
               "positive_target_rows": {"set_a_train": int(target_a.targets[train_idx].sum()),
                                        "set_a_calibration": int(target_a.targets[cal_idx].sum()),
                                        "set_a_untouched_holdout": int(target_a.targets[hold_idx].sum()),
                                        "set_b_evaluation": int(target_b.targets.sum())},
               "set_b_used_for_fit_or_threshold_selection": False, "models": {}}
    feature_sets = {"static": static, "temporal": np.arange(len(columns), dtype=np.int64)}
    set_b_calibrated_scores = {}
    for name, feature_indices in feature_sets.items():
        model = make_pipeline(SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
                              StandardScaler(), LogisticRegression(max_iter=100, tol=1e-2, class_weight="balanced", solver="lbfgs", random_state=seed))
        train_rows = target_a.row_indices[train_idx]
        print(f"horizon={horizon} seed={seed} model={name} fitting base model", flush=True)
        fit_started = time.time()
        train_X = Xa[np.ix_(train_rows, feature_indices)]
        train_y = target_a.targets[train_idx]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.fit(train_X, train_y)
        del train_X, train_y
        gc.collect()
        print(f"horizon={horizon} seed={seed} model={name} base fit {time.time()-fit_started:.1f}s", flush=True)
        cal_started = time.time()
        raw_cal = _predict(model, Xa, target_a.row_indices[cal_idx], feature_indices, chunk_rows)
        calibrator = fit_platt_recalibrator(target_a.targets[cal_idx], raw_cal)
        print(f"horizon={horizon} seed={seed} model={name} calibration fit {time.time()-cal_started:.1f}s", flush=True)
        cohorts = {}
        for cohort_name, X, target, idx in (
            ("set_a_untouched_holdout", Xa, target_a, hold_idx),
            ("set_b_final_evaluation", Xb, target_b, np.arange(len(target_b.targets))),
        ):
            if cohort_name == "set_a_untouched_holdout":
                row_indices = target.row_indices[idx]
                labels = target.targets[idx]
                patients = target.patient_ids[idx]
                times = target.patient_time_indices[idx]
            else:
                row_indices = target.row_indices
                labels = target.targets
                patients = target.patient_ids
                times = target.patient_time_indices
            pred_started = time.time()
            raw = _predict(model, X, row_indices, feature_indices, chunk_rows)
            calibrated = apply_platt_recalibrator(calibrator, raw)
            print(f"horizon={horizon} seed={seed} model={name} cohort={cohort_name} predictions {time.time()-pred_started:.1f}s", flush=True)
            variants = {}
            for variant, scores in (("raw", raw), ("platt_calibrated", calibrated)):
                variants[variant] = {"probability_metrics": probability_metrics(labels, scores), "threshold_grid": [
                    threshold_metrics(labels, scores, threshold) for threshold in THRESHOLDS
                ]}
            if cohort_name == "set_a_untouched_holdout":
                variants["platt_calibrated"]["utility_cost_sensitivity"] = evaluate_utility_operating_points(
                    labels, calibrated, patients, times, thresholds=THRESHOLDS,
                    missed_window_costs=missed_window_costs, alert_cost=alert_cost,
                    refractory_hours=refractory_hours,
                )
                variants["platt_calibrated"]["utility_cost_sensitivity_bootstrap_95ci"] = patient_cluster_bootstrap_utility_uncertainty(
                    labels, calibrated, patients, times, thresholds=THRESHOLDS,
                    missed_window_costs=missed_window_costs, alert_cost=alert_cost,
                    refractory_hours=refractory_hours, n_bootstrap=utility_bootstrap_replicates,
                    seed=seed + horizon * 100 + (0 if name == "static" else 1),
                )
            # Keep patient-level alert computation tractable while preserving a
            # predeclared calibrated Set-B operating-point slice. No threshold is selected.
            if cohort_name == "set_b_final_evaluation":
                set_b_calibrated_scores[name] = calibrated.copy()
                variants["platt_calibrated"]["patient_alert_metrics_predeclared_subset"] = {
                    str(threshold): evaluate_horizon_alerts(
                        labels, calibrated, patients, times, threshold=threshold,
                        refractory_hours=refractory_hours)
                    for threshold in (0.005, 0.01)
                }
                variants["platt_calibrated"]["patient_cluster_bootstrap_95ci"] = patient_cluster_bootstrap_calibration_metrics(
                    labels, calibrated, patients, comparison_probabilities=raw,
                    n_bootstrap=bootstrap_replicates, seed=seed,
                )
            cohorts[cohort_name] = variants
        results["models"][name] = {"feature_count": int(len(feature_indices)),
                                   "fit_warnings": [str(w.message) for w in caught],
                                   "calibration_method": "Platt logistic recalibration fitted only on Set-A calibration patients",
                                   "calibration_rows": int(len(cal_idx)),
                                   "calibration_positive_rows": int(target_a.targets[cal_idx].sum()),
                                   "cohorts": cohorts}
        del model, raw_cal, calibrator, raw, calibrated, variants, cohorts
        gc.collect()
        print(f"horizon={horizon} seed={seed} model={name} completed", flush=True)
    results["set_b_paired_static_vs_temporal_bootstrap_95ci"] = patient_cluster_bootstrap_paired_model_metrics(
        target_b.targets, set_b_calibrated_scores["static"], set_b_calibrated_scores["temporal"],
        target_b.patient_ids, n_bootstrap=bootstrap_replicates, seed=seed,
    )
    print(f"horizon={horizon} seed={seed} paired model bootstrap completed", flush=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--set-b-cache", type=Path, required=True)
    parser.add_argument("--horizons", type=int, nargs="+", default=[1, 3, 6])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--predict-chunk-rows", type=int, default=50000)
    parser.add_argument("--refractory-hours", type=int, default=6)
    parser.add_argument("--bootstrap-replicates", type=int, default=200)
    parser.add_argument("--missed-window-costs", type=float, nargs="+", default=[1.0, 10.0, 100.0, 500.0, 1000.0],
                        help="Set-A development cost scenarios, relative to the cost of one alert; defaults are illustrative")
    parser.add_argument("--alert-cost", type=float, default=1.0,
                        help="Cost unit assigned to one alert; defaults to 1.0 for relative comparisons")
    parser.add_argument("--utility-bootstrap-replicates", type=int, default=200,
                        help="Patient-cluster replicates for Set-A utility uncertainty (>=20)")
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    args = parser.parse_args()
    if not args.horizons or any(h < 1 for h in args.horizons) or len(set(args.horizons)) != len(args.horizons):
        parser.error("--horizons must contain unique positive integers")
    if not args.seeds or len(set(args.seeds)) != len(args.seeds) or args.predict_chunk_rows < 1 or args.refractory_hours < 1 or args.bootstrap_replicates < 20:
        parser.error("seeds must be unique; chunk rows and refractory hours must be positive; bootstrap replicates must be >=20")
    if not args.missed_window_costs or any(not np.isfinite(c) or c <= 0 for c in args.missed_window_costs) or len(set(args.missed_window_costs)) != len(args.missed_window_costs) or not np.isfinite(args.alert_cost) or args.alert_cost <= 0:
        parser.error("missed-window costs must be unique positive values and alert cost must be positive")
    if args.utility_bootstrap_replicates < 20:
        parser.error("--utility-bootstrap-replicates must be >=20")
    ma, Xa, ya, ga = load_cache(args.set_a_cache, "A")
    mb, Xb, yb, gb = load_cache(args.set_b_cache, "B")
    validate_official_cohort(ma, ya, ga, "A")
    validate_official_cohort(mb, yb, gb, "B")
    if ma["columns"] != mb["columns"]:
        parser.error("Set A and Set B feature schemas differ")
    started = time.time()
    runs = [evaluate_one(ma, Xa, ya, ga, mb, Xb, yb, gb, horizon=h, seed=s,
                         chunk_rows=args.predict_chunk_rows, refractory_hours=args.refractory_hours,
                         bootstrap_replicates=args.bootstrap_replicates,
                         missed_window_costs=args.missed_window_costs, alert_cost=args.alert_cost)
            for s in args.seeds for h in args.horizons]
    summary = {"project": "VITALIS", "run_type": "set_a_only_calibration_horizon_operating_point_analysis",
               "cohorts": {"set_a": {"patients": int(ma["patient_count"]), "rows": int(ma["row_count"]), "positive_labels": int(ya.sum())},
                           "set_b": {"patients": int(mb["patient_count"]), "rows": int(mb["row_count"]), "positive_labels": int(yb.sum())}},
               "protocol": {"horizons_hours": args.horizons, "seeds": args.seeds,
                            "base_model": "median imputation with missingness indicators, standard scaling, class-weighted logistic regression (lbfgs, max_iter=100, tol=0.01)",
                            "set_a_split": "patient-disjoint 60% model training / 20% Platt calibration / 20% untouched operating-point holdout",
                            "threshold_grid": list(THRESHOLDS), "thresholds_selected": False,
                            "utility_cost_analysis": {"missed_window_costs_relative_to_one_alert": args.missed_window_costs,
                                                      "alert_cost": args.alert_cost,
                                                      "computed_on": "patient-disjoint untouched Set-A operating-point holdout only",
                                                      "candidate_thresholds_are_clinical": False,
                                                      "patient_cluster_bootstrap_replicates": args.utility_bootstrap_replicates,
                                                      "uncertainty_outputs": ["metric percentile intervals", "cost-ranked threshold selection frequencies"]},
                            "patient_alert_metrics_thresholds": [0.005, 0.01],
                            "patient_cluster_bootstrap_replicates": args.bootstrap_replicates,
                            "bootstrap_unit": "whole patient; calibration uncertainty and paired static-versus-temporal calibrated-score differences on aligned Set-B rows",
                            "paired_model_metrics": ["AUROC", "AUPRC", "Brier score", "log loss"],
                            "set_b": "final evaluation only; never used for fitting, calibration, or threshold selection",
                            "refractory_hours": args.refractory_hours,
                            "raw_data_or_row_level_predictions_exported": False},
               "runs": runs, "elapsed_seconds": round(time.time() - started, 3),
               "limitations": ["Threshold grid is predeclared descriptive analysis, not a clinically selected alarm policy.",
                               "Set B is a separate Challenge training cohort, not prospective external clinical validation.",
                               "The Challenge label uses a six-hour lead convention; targets forecast label-window entry, not independent onset.",
                               "Patient-level alerts outside forecast-positive windows are not verified clinical false alarms.",
                               "Class weighting can distort probabilities; calibration is fitted on Set A calibration patients only.",
                               "VITALIS is research-only and not clinically validated."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "runs": len(runs), "elapsed_seconds": summary["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
