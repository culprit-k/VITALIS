#!/usr/bin/env python3
"""Set-A-only utility sensitivity analysis for future Challenge-label forecasts.

This runner deliberately has no Set-B input. It fits each model on a patient-
disjoint Set-A training partition, fits Platt recalibration on a separate Set-A
calibration partition, and evaluates a predeclared utility sensitivity grid on
a Set-A operating-point development holdout. Scenario minima are exploratory
and require independent evaluation.
"""
from __future__ import annotations

import argparse
import gc
import importlib.util
import json
import time
import warnings
from pathlib import Path

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from vitalis.horizon import build_future_challenge_targets
from vitalis.utility import evaluate_utility_operating_points

# Reuse established cohort-integrity and split/calibration helpers.
_HELPER_PATH = Path(__file__).with_name("evaluate_horizon_calibration.py")
_SPEC = importlib.util.spec_from_file_location("_vitalis_horizon_calibration_helpers", _HELPER_PATH)
_HELPERS = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
_SPEC.loader.exec_module(_HELPERS)

BASE = _HELPERS.BASE
UTILITY_THRESHOLDS = _HELPERS.THRESHOLDS
MISSED_WINDOW_COSTS = (1.0, 5.0, 10.0, 25.0, 50.0)
ALERT_COST = 1.0


def evaluate_set_a_one(meta, X, y, groups, *, horizon: int, seed: int,
                       chunk_rows: int, refractory_hours: int):
    target = build_future_challenge_targets(y, groups, horizon)
    columns = meta["columns"]
    col = {name: i for i, name in enumerate(columns)}
    static = np.asarray([col[name] for name in BASE if name in col], dtype=np.int64)
    if not len(static):
        raise ValueError("no baseline features found")
    train_idx, cal_idx, hold_idx = _HELPERS.patient_disjoint_three_way_split(
        target.targets, target.patient_ids, seed
    )
    if len(np.unique(target.targets[train_idx])) < 2:
        raise ValueError("Set-A training partition has one class")
    result = {
        "horizon_hours": horizon,
        "seed": seed,
        "split": "patient-disjoint 60% train / 20% calibration / 20% Set-A operating-point development holdout",
        "partition_patient_counts": {
            "train": int(len(np.unique(target.patient_ids[train_idx]))),
            "calibration": int(len(np.unique(target.patient_ids[cal_idx]))),
            "development_holdout": int(len(np.unique(target.patient_ids[hold_idx]))),
        },
        "partition_rows": {
            "train": int(len(train_idx)),
            "calibration": int(len(cal_idx)),
            "development_holdout": int(len(hold_idx)),
        },
        "set_b_loaded_or_used": False,
        "models": {},
    }
    feature_sets = {"static": static, "temporal": np.arange(len(columns), dtype=np.int64)}
    for model_name, feature_indices in feature_sets.items():
        print(f"horizon={horizon} seed={seed} model={model_name} fitting Set-A model", flush=True)
        model = make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(max_iter=100, tol=1e-2, class_weight="balanced",
                               solver="lbfgs", random_state=seed),
        )
        train_rows = target.row_indices[train_idx]
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model.fit(X[np.ix_(train_rows, feature_indices)], target.targets[train_idx])
        raw_cal = _HELPERS._predict(model, X, target.row_indices[cal_idx], feature_indices, chunk_rows)
        calibrator = _HELPERS.fit_platt_recalibrator(target.targets[cal_idx], raw_cal)
        raw_hold = _HELPERS._predict(model, X, target.row_indices[hold_idx], feature_indices, chunk_rows)
        calibrated = _HELPERS.apply_platt_recalibrator(calibrator, raw_hold)
        patients = target.patient_ids[hold_idx]
        times = target.patient_time_indices[hold_idx]
        print(f"horizon={horizon} seed={seed} model={model_name} evaluating development utility", flush=True)
        utility = evaluate_utility_operating_points(
            target.targets[hold_idx], calibrated, patients, times,
            thresholds=UTILITY_THRESHOLDS, missed_window_costs=MISSED_WINDOW_COSTS,
            alert_cost=ALERT_COST, refractory_hours=refractory_hours,
        )
        utility["thresholds_are_clinically_selected"] = False
        utility["costs_clinically_or_economically_elicited"] = False
        result["models"][model_name] = {
            "feature_count": int(len(feature_indices)),
            "fit_warning_count": int(len(caught)),
            "calibration_method": "Platt recalibration fitted only on Set-A calibration patients",
            "utility_sensitivity_development_only": utility,
        }
        del model, raw_cal, calibrator, raw_hold, calibrated
        gc.collect()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--horizons", type=int, nargs="+", default=[1, 3, 6])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--predict-chunk-rows", type=int, default=50000)
    parser.add_argument("--refractory-hours", type=int, default=6)
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    args = parser.parse_args()
    if not args.horizons or any(h < 1 for h in args.horizons) or len(set(args.horizons)) != len(args.horizons):
        parser.error("--horizons must contain unique positive integers")
    if not args.seeds or len(set(args.seeds)) != len(args.seeds) or args.predict_chunk_rows < 1 or args.refractory_hours < 1:
        parser.error("seeds must be unique; chunk rows and refractory hours must be positive")
    meta, X, y, groups = _HELPERS.load_cache(args.set_a_cache, "A")
    _HELPERS.validate_official_cohort(meta, y, groups, "A")
    started = time.time()
    runs = [
        evaluate_set_a_one(meta, X, y, groups, horizon=h, seed=s,
                           chunk_rows=args.predict_chunk_rows, refractory_hours=args.refractory_hours)
        for s in args.seeds for h in args.horizons
    ]
    summary = {
        "project": "VITALIS",
        "run_type": "set_a_only_utility_operating_point_sensitivity",
        "cohort": {
            "patients": int(meta["patient_count"]),
            "rows": int(meta["row_count"]),
            "positive_challenge_labels": int(np.asarray(y).sum()),
        },
        "protocol": {
            "horizons_hours": args.horizons,
            "seeds": args.seeds,
            "set_a_split": "patient-disjoint 60% model training / 20% Platt calibration / 20% operating-point development holdout",
            "threshold_grid": list(UTILITY_THRESHOLDS),
            "missed_window_costs": list(MISSED_WINDOW_COSTS),
            "alert_cost": ALERT_COST,
            "costs_clinically_or_economically_elicited": False,
            "refractory_hours": args.refractory_hours,
            "set_b_loaded_or_used": False,
            "raw_data_or_row_level_predictions_exported": False,
        },
        "runs": runs,
        "elapsed_seconds": round(time.time() - started, 3),
        "limitations": [
            "Cost ratios are abstract sensitivity scenarios, not costs elicited from clinicians, patients, or health systems.",
            "Threshold scenario minima are development-only and not a selected or recommended clinical threshold.",
            "Row-level sensitivity/PPV and patient-level window coverage/alert burden are different estimands.",
            "The target forecasts Challenge SepsisLabel-positive window entry, not independently observed sepsis onset.",
            "Alerts outside forecast-positive windows are not verified clinical false alarms.",
            "Independent cohort evaluation and independent clinical/statistical review remain necessary.",
            "VITALIS is research-only and not clinically validated.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "runs": len(runs),
                      "elapsed_seconds": summary["elapsed_seconds"],
                      "set_b_loaded_or_used": False}, indent=2))


if __name__ == "__main__":
    main()
