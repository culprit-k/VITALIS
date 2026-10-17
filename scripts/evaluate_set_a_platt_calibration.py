"""Patient-disjoint Set A Platt-calibration experiment; Set B is final evaluation only."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits

from scripts.evaluate_physiological_features import (
    BASE, EXPECTED, VITALS, calibration_summary, load_cache, metric,
    paired_brier_cluster_bootstrap, personal_z,
)
from vitalis.horizon import build_future_challenge_targets
from vitalis.validation import assert_disjoint_patient_splits


def digest(a):
    a = np.ascontiguousarray(np.asarray(a))
    return hashlib.sha256(a.dtype.str.encode() + str(a.shape).encode() + a.tobytes()).hexdigest()


def platt_fit(calibration_probability, calibration_y, seed):
    """Fit a one-dimensional logistic calibration map on Set A calibration patients."""
    p = np.clip(np.asarray(calibration_probability, dtype=float), 1e-7, 1 - 1e-7)
    logits = np.log(p / (1 - p)).reshape(-1, 1)
    y = np.asarray(calibration_y, dtype=np.int8)
    if len(np.unique(y)) != 2:
        raise ValueError("Calibration partition must contain both target classes.")
    model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=500, random_state=seed)
    with threadpool_limits(limits=1):
        model.fit(logits, y)
    if not np.all(np.asarray(model.n_iter_) < model.max_iter):
        raise RuntimeError("Platt calibration fit did not converge.")
    return model


def platt_apply(calibrator, probability):
    p = np.clip(np.asarray(probability, dtype=float), 1e-7, 1 - 1e-7)
    logits = np.log(p / (1 - p)).reshape(-1, 1)
    with threadpool_limits(limits=1):
        return calibrator.predict_proba(logits)[:, 1]


def run_one(ma, Xa, ya, ga, mb, Xb, yb, gb, horizon, seed, boot):
    ta = build_future_challenge_targets(ya, ga, horizon)
    tb = build_future_challenge_targets(yb, gb, horizon)

    # First reserve 20% of eligible Set A patients as untouched development holdout.
    outer = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    development_pos, unused_pos = next(
        outer.split(np.zeros(len(ta.targets)), ta.targets, ta.patient_ids)
    )
    development_groups = np.unique(ta.patient_ids[development_pos])
    unused_groups = np.unique(ta.patient_ids[unused_pos])

    # Of the remaining 80%, reserve 25% (20% overall) for calibration; fit on 60%.
    inner = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed + 10000)
    fit_local, calibration_local = next(
        inner.split(np.zeros(len(development_pos)), ta.targets[development_pos],
                    ta.patient_ids[development_pos])
    )
    fit_pos = development_pos[fit_local]
    calibration_pos = development_pos[calibration_local]
    fit_groups = set(ta.patient_ids[fit_pos].tolist())
    calibration_groups = set(ta.patient_ids[calibration_pos].tolist())
    unused_group_set = set(unused_groups.tolist())
    assert_disjoint_patient_splits(fit_groups, calibration_groups, unused_group_set)
    if len(np.unique(ta.targets[fit_pos])) < 2 or len(np.unique(ta.targets[calibration_pos])) < 2:
        raise ValueError(f"Both classes are required in Set A partitions at {horizon}h seed {seed}")

    fit_rows = ta.row_indices[fit_pos]
    calibration_rows = ta.row_indices[calibration_pos]
    fit_y = ta.targets[fit_pos]
    calibration_y = ta.targets[calibration_pos]
    test_rows = tb.row_indices
    if ma["columns"] != mb["columns"]:
        raise ValueError("Set A and Set B feature schemas differ")

    za = personal_z(Xa, ga, ma["columns"])
    zb = personal_z(Xb, gb, mb["columns"])
    ix = {name: i for i, name in enumerate(ma["columns"])}
    static_ix = np.array([ix[n] for n in BASE if n in ix], dtype=np.int64)
    temporal_ix = np.arange(len(ma["columns"]), dtype=np.int64)
    configs = (
        ("temporal_baseline_balanced", temporal_ix, False, "balanced"),
        ("temporal_baseline_unweighted", temporal_ix, False, None),
        ("temporal_plus_personal_physiology_balanced", temporal_ix, True, "balanced"),
        ("temporal_plus_personal_physiology_unweighted", temporal_ix, True, None),
    )
    out = {
        "horizon_hours": horizon, "seed": seed,
        "partition_patients": {
            "model_fit": len(fit_groups), "calibration": len(calibration_groups),
            "unused_holdout": len(unused_group_set),
            "fit_patient_ids_sha256": digest(sorted(fit_groups)),
            "calibration_patient_ids_sha256": digest(sorted(calibration_groups)),
            "unused_patient_ids_sha256": digest(sorted(unused_group_set)),
        },
        "set_b_patients": int(len(np.unique(tb.patient_ids))),
        "set_b_rows": int(len(tb.targets)),
        "set_b_positive_target_rows": int(tb.targets.sum()),
        "models": {},
    }
    for name, indices, add_z, class_weight in configs:
        def select(X, rows, z):
            raw = np.asarray(X[np.ix_(rows, indices)], dtype=np.float32)
            return np.concatenate((raw, z[rows]), axis=1) if add_z else raw

        fit_X = select(Xa, fit_rows, za)
        calibration_X = select(Xa, calibration_rows, za)
        test_X = select(Xb, test_rows, zb)
        model = make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(max_iter=300, class_weight=class_weight, solver="lbfgs", random_state=seed),
        )
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with threadpool_limits(limits=1):
                model.fit(fit_X, fit_y)
        if not np.all(np.asarray(model[-1].n_iter_) < model[-1].max_iter):
            raise RuntimeError(f"Base model did not converge: {name}, {horizon}h, seed {seed}")
        with threadpool_limits(limits=1):
            p_cal = model.predict_proba(calibration_X)[:, 1]
            p_raw = model.predict_proba(test_X)[:, 1]
        calibrator = platt_fit(p_cal, calibration_y, seed)
        p_calibrated = platt_apply(calibrator, p_raw)
        raw_metrics = metric(tb.targets, p_raw, 0.5)
        calibrated_metrics = metric(tb.targets, p_calibrated, 0.5)
        out["models"][name] = {
            "set_a_calibration_rows": int(len(calibration_y)),
            "calibration_prevalence": float(np.mean(calibration_y)),
            "calibrator": {
                "method": "Platt scaling on clipped logit of predicted probability",
                "base_model_class_weight": class_weight,
                "fit_partition": "patient-disjoint Set A calibration partition only",
                "intercept": float(calibrator.intercept_[0]),
                "slope": float(calibrator.coef_[0, 0]),
                "converged": bool(np.all(np.asarray(calibrator.n_iter_) < calibrator.max_iter)),
            },
            "set_b_raw": {
                "metrics": raw_metrics,
                "calibration": calibration_summary(tb.targets, p_raw, tb.patient_ids),
            },
            "set_b_platt_calibrated": {
                "metrics": calibrated_metrics,
                "calibration": calibration_summary(tb.targets, p_calibrated, tb.patient_ids),
            },
            "paired_brier_raw_vs_calibrated": paired_brier_cluster_bootstrap(
                tb.targets, p_raw, p_calibrated, tb.patient_ids, boot, seed + horizon * 100000
            ),
            "fit_warnings": [str(w.message) for w in caught],
            "diagnostics": {
                "fit_rows_sha256": digest(fit_rows),
                "calibration_rows_sha256": digest(calibration_rows),
                "raw_predictions_sha256": digest(p_raw),
                "calibrated_predictions_sha256": digest(p_calibrated),
            },
        }
        print(f"horizon={horizon} seed={seed} model={name} "
              f"raw_brier={raw_metrics['brier_score']:.6f} "
              f"platt_brier={calibrated_metrics['brier_score']:.6f}", flush=True)
        del model, calibrator, fit_X, calibration_X, test_X, p_cal, p_raw, p_calibrated
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--set-b-cache", type=Path, required=True)
    parser.add_argument("--horizons", type=int, nargs="+", default=[1, 3, 6])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--bootstrap-replicates", type=int, default=200)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ma, Xa, ya, ga = load_cache(args.set_a_cache, "A")
    mb, Xb, yb, gb = load_cache(args.set_b_cache, "B")
    started = time.time()
    runs = [run_one(ma, Xa, ya, ga, mb, Xb, yb, gb, h, seed, args.bootstrap_replicates)
            for h in args.horizons for seed in args.seeds]
    result = {
        "project": "VITALIS",
        "experiment": "patient-disjoint Set A Platt calibration",
        "protocol": {
            "horizons_hours": args.horizons, "seeds": args.seeds,
            "Set_A_partition": "60% model fit / 20% calibration / 20% untouched holdout by patient",
            "calibration": "Platt scaling on model logits; fit only on Set A calibration patients",
            "Set_B_role": "frozen final evaluation only",
            "no_Set_B_fit_selection_or_threshold_tuning": True,
            "base_model_class_weight_comparison": ["balanced", None],
            "class_weight_note": "Unweighted model is prevalence-aware; comparison is exploratory.",
            "threshold_reported_for_diagnostics_only": 0.5,
            "bootstrap_replicates": args.bootstrap_replicates,
        },
        "cohorts": {
            "A": {"patients": len(np.unique(ga)), "rows": len(ya), "positive_labels": int(np.asarray(ya).sum())},
            "B": {"patients": len(np.unique(gb)), "rows": len(yb), "positive_labels": int(np.asarray(yb).sum())},
        },
        "runtime_seconds": round(time.time() - started, 3),
        "runs": runs,
        "limitations": [
            "Retrospective cross-cohort experiment; not clinical validation.",
            "Set B is evaluation-only and must not be used for calibrator selection or threshold tuning.",
            "Platt calibration may not transport across cohorts with differing prevalence or measurement processes.",
            "Challenge label-window entry is not independently adjudicated biological sepsis onset.",
            "No patient-level predictions or identifiers are written to the output artifact.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"runs": len(runs), "runtime_seconds": result["runtime_seconds"],
                      "output": str(args.output)}))


if __name__ == "__main__":
    main()
