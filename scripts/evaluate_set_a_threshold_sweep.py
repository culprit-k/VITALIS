"""Set A-only operating-threshold sweep; Set B is never loaded or evaluated here."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from scripts.evaluate_physiological_features import BASE, load_cache, personal_z
from scripts.evaluate_set_a_platt_calibration import platt_apply, platt_fit
from vitalis.horizon import build_future_challenge_targets, evaluate_horizon_alerts, patient_cluster_bootstrap_horizon_alerts
from vitalis.validation import assert_disjoint_patient_splits

EXTRA_THRESHOLDS = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10, 0.50)
ALERT_CI_THRESHOLDS = (0.01, 0.05, 0.10, 0.50)


def threshold_grid():
    return sorted(set([round(x / 100, 2) for x in range(1, 100)] + list(EXTRA_THRESHOLDS)))


def row_metrics(y, p, threshold):
    y = np.asarray(y, dtype=np.int8)
    p = np.asarray(p, dtype=np.float64)
    pred = p >= threshold
    tp = int(np.sum(pred & (y == 1)))
    fp = int(np.sum(pred & (y == 0)))
    fn = int(np.sum(~pred & (y == 1)))
    tn = int(np.sum(~pred & (y == 0)))
    positives = tp + fn
    negatives = tn + fp
    return {
        "threshold": float(threshold),
        "sensitivity": tp / positives if positives else None,
        "specificity": tn / negatives if negatives else None,
        "ppv": tp / (tp + fp) if tp + fp else None,
        "npv": tn / (tn + fn) if tn + fn else None,
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
    }


def cluster_intervals(y, p, groups, threshold, replicates, seed):
    """Patient-cluster percentile intervals for row-level sensitivity and PPV."""
    y = np.asarray(y, dtype=np.int8)
    pred = np.asarray(p) >= threshold
    groups = np.asarray(groups)
    _, inverse = np.unique(groups, return_inverse=True)
    n = int(inverse.max()) + 1
    counts = np.zeros((n, 4), dtype=np.float64)  # TP, FP, FN, positives
    np.add.at(counts[:, 0], inverse, pred & (y == 1))
    np.add.at(counts[:, 1], inverse, pred & (y == 0))
    np.add.at(counts[:, 2], inverse, (~pred) & (y == 1))
    np.add.at(counts[:, 3], inverse, y == 1)
    rng = np.random.default_rng(seed)
    sampled = counts[rng.integers(0, n, size=(replicates, n))].sum(axis=1)
    sens = np.divide(sampled[:, 0], sampled[:, 3], out=np.full(replicates, np.nan), where=sampled[:, 3] > 0)
    ppv_denom = sampled[:, 0] + sampled[:, 1]
    ppv = np.divide(sampled[:, 0], ppv_denom, out=np.full(replicates, np.nan), where=ppv_denom > 0)
    def ci(values):
        values = values[np.isfinite(values)]
        return {"lower_95": float(np.percentile(values, 2.5)) if len(values) else None,
                "upper_95": float(np.percentile(values, 97.5)) if len(values) else None,
                "valid_replicates": int(len(values)), "requested_replicates": int(replicates)}
    return {"method": "patient-cluster percentile bootstrap", "sensitivity": ci(sens), "ppv": ci(ppv)}


def digest(values):
    a = np.ascontiguousarray(np.asarray(values))
    return hashlib.sha256(a.dtype.str.encode() + str(a.shape).encode() + a.tobytes()).hexdigest()


def run_one(meta, X, y, groups, horizon, seed, bootstrap_replicates, refractory_hours):
    target = build_future_challenge_targets(y, groups, horizon)
    # Patient-level 60/20/20 split: model fit / probability calibration / threshold selection.
    development, threshold_pos = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
        .split(np.zeros(len(target.targets)), target.targets, target.patient_ids))
    dev_groups = np.unique(target.patient_ids[development])
    threshold_groups = np.unique(target.patient_ids[threshold_pos])
    fit_local, calibration_local = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed + 10000)
        .split(np.zeros(len(development)), target.targets[development], target.patient_ids[development]))
    fit_pos = development[fit_local]
    calibration_pos = development[calibration_local]
    fit_groups = set(target.patient_ids[fit_pos].tolist())
    calibration_groups = set(target.patient_ids[calibration_pos].tolist())
    threshold_group_set = set(threshold_groups.tolist())
    assert_disjoint_patient_splits(fit_groups, calibration_groups, threshold_group_set)
    if len(np.unique(target.targets[fit_pos])) < 2 or len(np.unique(target.targets[calibration_pos])) < 2:
        raise ValueError(f"Both classes required in fit and calibration partitions at {horizon}h seed {seed}")
    if len(np.unique(target.targets[threshold_pos])) < 2:
        raise ValueError(f"Both classes required in threshold-selection partition at {horizon}h seed {seed}")

    z = personal_z(X, groups, meta["columns"])
    ix = {name: i for i, name in enumerate(meta["columns"])}
    static_ix = np.asarray([ix[n] for n in BASE if n in ix], dtype=np.int64)
    temporal_ix = np.arange(len(meta["columns"]), dtype=np.int64)
    configs = (
        ("temporal_baseline_balanced", temporal_ix, False, "balanced"),
        ("temporal_baseline_unweighted", temporal_ix, False, None),
        ("temporal_plus_personal_physiology_balanced", temporal_ix, True, "balanced"),
        ("temporal_plus_personal_physiology_unweighted", temporal_ix, True, None),
    )
    rows = target.row_indices
    out = {
        "horizon_hours": int(horizon), "seed": int(seed),
        "partition_patients": {"model_fit": len(fit_groups), "calibration": len(calibration_groups),
                               "threshold_selection": len(threshold_group_set)},
        "partition_rows": {"model_fit": int(len(fit_pos)), "calibration": int(len(calibration_pos)),
                           "threshold_selection": int(len(threshold_pos))},
        "partition_group_digests": {"model_fit": digest(sorted(fit_groups)),
                                    "calibration": digest(sorted(calibration_groups)),
                                    "threshold_selection": digest(sorted(threshold_group_set))},
        "threshold_selection_prevalence": float(np.mean(target.targets[threshold_pos])),
        "constant_prevalence_brier_reference": float(np.mean(target.targets[threshold_pos]) *
            (1 - np.mean(target.targets[threshold_pos]))),
        "models": {},
    }
    grid = threshold_grid()
    for name, indices, add_z, class_weight in configs:
        def select(pos):
            raw = np.asarray(X[np.ix_(rows[pos], indices)], dtype=np.float32)
            return np.concatenate((raw, z[rows[pos]]), axis=1) if add_z else raw
        model = make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(max_iter=300, class_weight=class_weight, solver="lbfgs", random_state=seed),
        )
        with threadpool_limits(limits=1):
            model.fit(select(fit_pos), target.targets[fit_pos])
            p_cal = model.predict_proba(select(calibration_pos))[:, 1]
            p_select_raw = model.predict_proba(select(threshold_pos))[:, 1]
        if not np.all(np.asarray(model[-1].n_iter_) < model[-1].max_iter):
            raise RuntimeError(f"Base model did not converge: {name}, {horizon}h, seed {seed}")
        calibrator = platt_fit(p_cal, target.targets[calibration_pos], seed)
        p = platt_apply(calibrator, p_select_raw)
        y_select = target.targets[threshold_pos]
        g_select = target.patient_ids[threshold_pos]
        t_select = target.patient_time_indices[threshold_pos]
        sweep = []
        for threshold in grid:
            m = row_metrics(y_select, p, threshold)
            if threshold in ALERT_CI_THRESHOLDS:
                m["patient_cluster_ci"] = cluster_intervals(
                    y_select, p, g_select, threshold, bootstrap_replicates, seed + int(threshold * 1_000_000) + horizon
                )
                m["alert_burden"] = evaluate_horizon_alerts(
                    y_select, p, g_select, t_select, threshold=threshold, refractory_hours=refractory_hours
                )
                m["alert_burden_patient_cluster_ci"] = patient_cluster_bootstrap_horizon_alerts(
                    y_select, p, g_select, t_select, threshold=threshold, refractory_hours=refractory_hours,
                    n_bootstrap=bootstrap_replicates, seed=seed + 200000 + int(threshold * 1_000_000) + horizon
                )
            sweep.append(m)
        out["models"][name] = {
            "base_model_class_weight": class_weight,
            "calibrator": {"method": "Platt scaling", "fit_partition": "Set A calibration patients only",
                           "converged": bool(np.all(np.asarray(calibrator.n_iter_) < calibrator.max_iter))},
            "threshold_independent_metrics": {
                "auroc": float(roc_auc_score(y_select, p)),
                "auprc": float(average_precision_score(y_select, p)),
                "brier_score": float(brier_score_loss(y_select, p)),
            },
            "sweep": sweep,
            "uncertainty_scope_note": "Sensitivity/PPV and alert-burden bootstrap intervals are reported at thresholds 0.01, 0.05, 0.10, and 0.50; other thresholds have point estimates only.",
            "diagnostics": {"calibration_rows_sha256": digest(calibration_pos), "threshold_rows_sha256": digest(threshold_pos)},
        }
        del model, calibrator, p_cal, p_select_raw, p
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--horizons", type=int, nargs="+", default=[1, 3, 6])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--bootstrap-replicates", type=int, default=200)
    parser.add_argument("--refractory-hours", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    meta, X, y, groups = load_cache(args.set_a_cache, "A")
    started = time.time()
    runs = [run_one(meta, X, y, groups, h, seed, args.bootstrap_replicates, args.refractory_hours)
            for h in args.horizons for seed in args.seeds]
    result = {
        "project": "VITALIS", "experiment": "Set A-only operating-threshold sweep",
        "protocol": {"horizons_hours": args.horizons, "seeds": args.seeds, "thresholds": threshold_grid(),
                     "Set_A_partition": "60% model fit / 20% probability calibration / 20% threshold selection by patient",
                     "Set_B_role": "not loaded; not evaluated; final evaluation only in a separate frozen run",
                     "threshold_selection_partition_not_used_for_fit_or_calibration": True,
                     "refractory_hours": args.refractory_hours, "bootstrap_replicates": args.bootstrap_replicates,
                     "alert_uncertainty_thresholds": list(ALERT_CI_THRESHOLDS),
                     "row_level_predictions_exported": False},
        "cohort": {"patients": int(len(np.unique(groups))), "rows": int(len(y)), "positive_labels": int(np.asarray(y).sum())},
        "runtime_seconds": round(time.time() - started, 3), "runs": runs,
        "limitations": ["Research-only; not clinical validation.", "Challenge label-window entry is not independently adjudicated sepsis onset.",
                        "No Set B data are loaded by this script.", "No single threshold is selected; supervisor must predeclare objective and alert budget.",
                        "Alert-burden uncertainty intervals are computed at four predeclared reference thresholds; all grid points have aggregate point estimates.",
                        "No patient-level predictions or identifiers are written to output."]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(runs), "thresholds_per_model": len(threshold_grid()),
                      "runtime_seconds": result["runtime_seconds"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
