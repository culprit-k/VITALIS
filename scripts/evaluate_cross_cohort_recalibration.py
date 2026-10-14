#!/usr/bin/env python3
"""Train on set A, fit Platt recalibration on a disjoint set-A validation cohort, test on set B.

Input feature caches are local derived data. Output contains aggregate metrics only.
Set B labels are used exclusively for final evaluation, never for model/recalibrator fitting.
"""
from __future__ import annotations

import argparse
import json
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, log_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2",
    "BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN",
    "Alkalinephos", "Calcium", "Chloride", "Creatinine", "Bilirubin_direct",
    "Glucose", "Lactate", "Magnesium", "Phosphate", "Potassium",
    "Bilirubin_total", "TroponinI", "Hct", "Hgb", "PTT", "WBC",
    "Fibrinogen", "Platelets", "Age", "Gender", "Unit1", "Unit2",
    "HospAdmTime", "ICULOS",
]


def fit_platt_recalibrator(validation_labels: np.ndarray, validation_probabilities: np.ndarray) -> LogisticRegression:
    """Fit a one-dimensional logistic recalibrator using validation data only."""
    y = np.asarray(validation_labels, dtype=np.int8)
    p = np.asarray(validation_probabilities, dtype=np.float64)
    if y.ndim != 1 or p.ndim != 1 or len(y) != len(p) or len(y) == 0:
        raise ValueError("validation labels and probabilities must be non-empty aligned vectors")
    if not np.isin(y, [0, 1]).all() or len(np.unique(y)) < 2:
        raise ValueError("validation labels must contain both binary classes")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("validation probabilities must be finite and in [0, 1]")
    p = np.clip(p, 1e-6, 1 - 1e-6)
    logits = np.log(p / (1 - p)).reshape(-1, 1)
    return LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000).fit(logits, y)


def apply_platt_recalibrator(recalibrator: LogisticRegression, probabilities: np.ndarray) -> np.ndarray:
    p = np.asarray(probabilities, dtype=np.float64)
    if p.ndim != 1 or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be a finite vector in [0, 1]")
    pc = np.clip(p, 1e-6, 1 - 1e-6)
    logits = np.log(pc / (1 - pc)).reshape(-1, 1)
    return np.clip(recalibrator.predict_proba(logits)[:, 1], 1e-6, 1 - 1e-6)


def probability_metrics(y: np.ndarray, p: np.ndarray) -> dict:
    y = np.asarray(y, dtype=np.int8)
    p = np.clip(np.asarray(p, dtype=np.float64), 1e-6, 1 - 1e-6)
    return {
        "rows": int(len(y)),
        "positive_label_rows": int(y.sum()),
        "prevalence": float(np.mean(y)),
        "mean_predicted_probability": float(np.mean(p)),
        "auroc": float(roc_auc_score(y, p)),
        "auprc": float(average_precision_score(y, p)),
        "brier_score": float(brier_score_loss(y, p)),
        "log_loss": float(log_loss(y, p, labels=[0, 1])),
    }


def patient_disjoint_three_way_split(y: np.ndarray, groups: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return 60/20/20 train/validation/unused row indices with patient isolation."""
    first = GroupShuffleSplit(n_splits=1, test_size=0.4, random_state=seed)
    train_idx, hold_idx = next(first.split(np.zeros(len(y)), y, groups))
    second = GroupShuffleSplit(n_splits=1, test_size=0.5, random_state=seed + 1)
    val_local, unused_local = next(second.split(np.zeros(len(hold_idx)), y[hold_idx], groups[hold_idx]))
    val_idx, unused_idx = hold_idx[val_local], hold_idx[unused_local]
    sets = [set(np.unique(groups[ix]).tolist()) for ix in (train_idx, val_idx, unused_idx)]
    if sets[0] & sets[1] or sets[0] & sets[2] or sets[1] & sets[2]:
        raise RuntimeError("patient overlap in set-A train/validation/unused partitions")
    return train_idx, val_idx, unused_idx


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--set-a-cache", type=Path, required=True)
    ap.add_argument("--set-b-cache", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--predict-chunk-rows", type=int, default=50000)
    args = ap.parse_args()
    if args.predict_chunk_rows < 1:
        ap.error("--predict-chunk-rows must be positive")

    ma = json.loads((args.set_a_cache / "meta.json").read_text())
    mb = json.loads((args.set_b_cache / "meta.json").read_text())
    if ma["columns"] != mb["columns"]:
        ap.error("set A and set B feature schemas differ")
    Xa = np.load(args.set_a_cache / "X.npy", mmap_mode="r")
    ya = np.load(args.set_a_cache / "y.npy", mmap_mode="r")
    ga = np.load(args.set_a_cache / "g.npy", mmap_mode="r")
    Xb = np.load(args.set_b_cache / "X.npy", mmap_mode="r")
    yb = np.load(args.set_b_cache / "y.npy", mmap_mode="r")
    gb = np.load(args.set_b_cache / "g.npy", mmap_mode="r")
    for X, y, g, meta, label in ((Xa, ya, ga, ma, "A"), (Xb, yb, gb, mb, "B")):
        if X.shape[0] != meta["row_count"] or len(y) != len(X) or len(g) != len(X):
            ap.error(f"set {label} cache row-count integrity check failed")
        if len(np.unique(g)) != meta["patient_count"]:
            ap.error(f"set {label} cache patient-group integrity check failed")
        if not np.isin(y, [0, 1]).all():
            ap.error(f"set {label} contains non-binary labels")
    if (ma["patient_count"], mb["patient_count"], int(ya.sum()), int(yb.sum())) != (20336, 20000, 17136, 10780):
        ap.error("unexpected official Challenge 2019 cohort totals")

    col = {name: i for i, name in enumerate(ma["columns"])}
    feature_sets = [("static", np.asarray([col[name] for name in BASE])), ("temporal", np.arange(Xa.shape[1]))]
    runs = []
    started = time.time()
    for seed in args.seeds:
        train_idx, val_idx, unused_idx = patient_disjoint_three_way_split(ya, ga, seed)
        run = {
            "seed": seed,
            "patient_counts": {
                "set_a_train": int(len(np.unique(ga[train_idx]))),
                "set_a_validation": int(len(np.unique(ga[val_idx]))),
                "set_a_unused": int(len(np.unique(ga[unused_idx]))),
                "set_b_test": int(mb["patient_count"]),
            },
            "row_counts": {
                "set_a_train": int(len(train_idx)),
                "set_a_validation": int(len(val_idx)),
                "set_a_unused": int(len(unused_idx)),
                "set_b_test": int(len(yb)),
            },
            "set_b_used_for_fit_or_recalibration": False,
            "models": {},
        }
        for name, ix in feature_sets:
            model = make_pipeline(
                SimpleImputer(strategy="median", add_indicator=True),
                StandardScaler(),
                LogisticRegression(max_iter=150, tol=1e-3, class_weight="balanced", solver="lbfgs", random_state=seed),
            )
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                model.fit(Xa[np.ix_(train_idx, ix)], ya[train_idx])
            val_prob = model.predict_proba(Xa[np.ix_(val_idx, ix)])[:, 1]
            recalibrator = fit_platt_recalibrator(ya[val_idx], val_prob)
            raw_parts, recal_parts = [], []
            for start in range(0, len(yb), args.predict_chunk_rows):
                end = min(start + args.predict_chunk_rows, len(yb))
                raw = model.predict_proba(Xb[start:end, ix])[:, 1]
                raw_parts.append(raw)
                recal_parts.append(apply_platt_recalibrator(recalibrator, raw))
            raw_b, recal_b = np.concatenate(raw_parts), np.concatenate(recal_parts)
            run["models"][name] = {
                "fit_warnings": [str(w.message) for w in caught],
                "raw_set_b": probability_metrics(yb, raw_b),
                "recalibrated_set_b": probability_metrics(yb, recal_b),
                "recalibrator_fit_cohort": "training_setA_validation_only",
                "recalibrator_validation_rows": int(len(val_idx)),
            }
            print(
                f"seed={seed} model={name} raw_Brier={run['models'][name]['raw_set_b']['brier_score']:.5f} "
                f"recal_Brier={run['models'][name]['recalibrated_set_b']['brier_score']:.5f}",
                flush=True,
            )
        runs.append(run)

    aggregate = {}
    metric_names = ("auroc", "auprc", "brier_score", "log_loss", "mean_predicted_probability")
    for name in ("static", "temporal"):
        aggregate[name] = {}
        for stream in ("raw_set_b", "recalibrated_set_b"):
            aggregate[name][stream] = {}
            for metric in metric_names:
                values = [r["models"][name][stream][metric] for r in runs]
                aggregate[name][stream][metric] = {
                    "mean": float(np.mean(values)),
                    "sample_sd_across_seeds": float(np.std(values, ddof=1)) if len(values) > 1 else None,
                    "by_seed": {str(r["seed"]): r["models"][name][stream][metric] for r in runs},
                }
    result = {
        "project": "VITALIS",
        "run_type": "cross_cohort_validation_A_recalibration_test_B",
        "dataset": {
            "training_setA": {"patients": ma["patient_count"], "rows": ma["row_count"], "positive_hourly_labels": int(ya.sum())},
            "training_setB": {"patients": mb["patient_count"], "rows": mb["row_count"], "positive_hourly_labels": int(yb.sum()), "positive_hourly_label_prevalence": float(np.mean(yb))},
        },
        "protocol": {
            "seeds": args.seeds,
            "set_a_split": "60% model training / 20% recalibration validation / 20% unused; patient-disjoint",
            "set_b_test": "all set B patients; not used for model fitting, recalibrator fitting, or threshold selection",
            "models": "static and temporal balanced logistic regression with median imputation, missingness indicators, and standard scaling",
            "recalibration": "one-dimensional logistic (Platt) recalibration fit on set A validation predictions only",
            "threshold_selection": "none",
            "row_level_predictions_exported": False,
        },
        "source_provenance": "Aggregate runner records intended protocol; exact-checkout data execution must be separately verified.",
        "aggregate_mean_and_sample_sd_across_seeds": aggregate,
        "per_seed": runs,
        "elapsed_seconds": round(time.time() - started, 2),
        "limitations": [
            "Retrospective hourly Challenge-label metrics only; not patient-level clinical event performance.",
            "Set B is a held-out cohort within the same benchmark, not prospective or independent real-world validation.",
            "Recalibration can improve aggregate scores without establishing clinical calibration.",
            "Thresholds were not selected for clinical use.",
            "Raw records, patient identifiers, caches, and row-level predictions must remain outside Git.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote aggregate-only results to {args.output}; elapsed={result['elapsed_seconds']}s", flush=True)


if __name__ == "__main__":
    main()
