"""Train on Challenge 2019 Set A and evaluate future-label horizons on Set B.

The target is future entry into the Challenge SepsisLabel-positive window, not
independently observed sepsis onset. Set B is evaluation-only: it is never used
for fitting, feature selection, calibration, or threshold selection. Cache and
source patient data must remain local; JSON output is aggregate-only.
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
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_info, threadpool_limits

from vitalis.horizon import build_future_challenge_targets, evaluate_horizon_alerts, patient_cluster_bootstrap_horizon_alerts
from vitalis.validation import assert_disjoint_patient_splits

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
    if len(np.unique(groups)) != meta.get("patient_count"):
        raise ValueError(f"Set {cohort} patient groups do not match metadata")
    if not np.isin(y, [0, 1]).all():
        raise ValueError(f"Set {cohort} SepsisLabel must be binary")
    if meta.get("rows_per_patient") and sum(meta["rows_per_patient"]) != len(y):
        raise ValueError(f"Set {cohort} rows_per_patient does not match label array")
    return meta, X, y, groups


def validate_official_cohort(meta, y, groups, cohort: str) -> None:
    expected = EXPECTED[cohort]
    actual = {
        "patients": int(len(np.unique(groups))),
        "rows": int(len(y)),
        "positive_labels": int(np.asarray(y).sum()),
    }
    if actual != expected or meta.get("patient_count") != expected["patients"] or meta.get("row_count") != expected["rows"]:
        raise ValueError(
            f"Set {cohort} does not match expected official Challenge 2019 counts: "
            f"expected {expected}, got {actual}"
        )


def horizon_rows(y, groups, horizon_hours: int):
    """Return eligible source rows, future labels, patient groups, and within-patient times."""
    target = build_future_challenge_targets(y, groups, horizon_hours)
    if not len(target.row_indices):
        raise ValueError(f"No eligible rows for horizon={horizon_hours}h")
    return target


def binary_metrics(y, probabilities, threshold: float) -> dict[str, object]:
    y = np.asarray(y, dtype=np.int8)
    p = np.asarray(probabilities, dtype=np.float64)
    if len(y) == 0 or len(y) != len(p):
        raise ValueError("labels and probabilities must be nonempty and equally sized")
    pred = p >= threshold
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "rows": int(len(y)),
        "positive_future_label_rows": int(y.sum()),
        "prevalence": float(np.mean(y)),
        "threshold": threshold,
        "auroc": float(roc_auc_score(y, p)) if len(np.unique(y)) == 2 else None,
        "auprc": float(average_precision_score(y, p)),
        "brier_score": float(brier_score_loss(y, p)),
        "sensitivity": float(tp / (tp + fn)) if tp + fn else None,
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "ppv": float(tp / (tp + fp)) if tp + fp else None,
        "npv": float(tn / (tn + fn)) if tn + fn else None,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def evaluate_one_horizon(
    meta_a, Xa, ya, ga, meta_b, Xb, yb, gb, columns,
    *, horizon_hours: int, seed: int, threshold: float = 0.5,
    refractory_hours: int = 6, n_bootstrap: int = 200, predict_chunk_rows: int = 50000,
) -> dict[str, object]:
    target_a = horizon_rows(ya, ga, horizon_hours)
    target_b = horizon_rows(yb, gb, horizon_hours)
    if columns != meta_a["columns"] or columns != meta_b["columns"]:
        raise ValueError("Set A and Set B feature schemas differ")
    col_index = {name: i for i, name in enumerate(columns)}
    static_names = [name for name in BASE if name in col_index]
    if not static_names:
        raise ValueError("No baseline features found in cache schema")
    feature_sets = {
        "static": np.asarray([col_index[name] for name in static_names], dtype=np.int64),
        "temporal": np.arange(len(columns), dtype=np.int64),
    }

    first = GroupShuffleSplit(n_splits=1, test_size=0.4, random_state=seed)
    train_pos, heldout_pos = next(first.split(
        np.zeros(len(target_a.targets)), target_a.targets, target_a.patient_ids
    ))
    train_patients = set(target_a.patient_ids[train_pos].tolist())
    heldout_patients = set(target_a.patient_ids[heldout_pos].tolist())
    assert_disjoint_patient_splits(train_patients, heldout_patients, set())
    if len(np.unique(target_a.targets[train_pos])) < 2:
        raise ValueError(f"Set A training partition has one class at horizon {horizon_hours}h")

    result = {
        "horizon_hours": horizon_hours,
        "target_definition": f"current SepsisLabel=0 and any positive challenge label in the next {horizon_hours} rows; incomplete patient tails excluded",
        "source_label_note": "The Challenge label already uses a six-hour lead convention; this predicts challenge-label entry, not independent sepsis onset.",
        "seed": seed,
        "threshold": threshold,
        "threshold_note": "Fixed research reference; no Set B threshold selection.",
        "refractory_hours": refractory_hours,
        "patient_counts": {
            "set_a_train_eligible": int(len(train_patients)),
            "set_a_heldout_unused_eligible": int(len(heldout_patients)),
            "set_b_test_eligible": int(len(np.unique(target_b.patient_ids))),
        },
        "row_counts": {
            "set_a_eligible": int(len(target_a.targets)),
            "set_a_train": int(len(train_pos)),
            "set_a_heldout_unused": int(len(heldout_pos)),
            "set_b_eligible": int(len(target_b.targets)),
        },
        "positive_target_rows": {
            "set_a_train": int(target_a.targets[train_pos].sum()),
            "set_a_heldout_unused": int(target_a.targets[heldout_pos].sum()),
            "set_b_test": int(target_b.targets.sum()),
        },
        "models": {},
    }

    for model_name, feature_indices in feature_sets.items():
        model = make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
            StandardScaler(),
            LogisticRegression(
                max_iter=300, class_weight="balanced", solver="lbfgs", random_state=seed
            ),
        )
        train_source_rows = target_a.row_indices[train_pos]
        train_X = Xa[np.ix_(train_source_rows, feature_indices)]
        train_y = target_a.targets[train_pos]
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always")
            start_fit = time.time()
            # Environment variables alone do not reliably constrain already-loaded BLAS
            # runtimes. Apply the cap at the point of execution for repeatable fits.
            with threadpool_limits(limits=1):
                model.fit(train_X, train_y)
            fit_seconds = time.time() - start_fit

        test_probabilities = np.empty(len(target_b.targets), dtype=np.float64)
        with threadpool_limits(limits=1):
            for start in range(0, len(target_b.targets), predict_chunk_rows):
                end = min(start + predict_chunk_rows, len(target_b.targets))
                source_rows = target_b.row_indices[start:end]
                chunk = Xb[np.ix_(source_rows, feature_indices)]
                test_probabilities[start:end] = model.predict_proba(chunk)[:, 1]

        warning_metrics = evaluate_horizon_alerts(
            target_b.targets, test_probabilities, target_b.patient_ids,
            target_b.patient_time_indices, threshold=threshold,
            refractory_hours=refractory_hours,
        )
        warning_ci = patient_cluster_bootstrap_horizon_alerts(
            target_b.targets, test_probabilities, target_b.patient_ids,
            target_b.patient_time_indices, threshold=threshold,
            refractory_hours=refractory_hours, n_bootstrap=n_bootstrap, seed=seed,
        )
        result["models"][model_name] = {
            "feature_count": int(len(feature_indices)),
            "fit_seconds": round(fit_seconds, 3),
            "fit_warnings": [str(item.message) for item in captured],
            "set_b_test_metrics": binary_metrics(target_b.targets, test_probabilities, threshold),
            "set_b_patient_warning_metrics": warning_metrics,
            "set_b_patient_warning_metric_bootstrap_95ci": warning_ci,
        }
        print(
            f"horizon={horizon_hours}h seed={seed} model={model_name} "
            f"SetB AUROC={result['models'][model_name]['set_b_test_metrics']['auroc']} "
            f"AUPRC={result['models'][model_name]['set_b_test_metrics']['auprc']:.4f}",
            flush=True,
        )
        del model, test_probabilities

    result["limitations"] = [
        "Set B is used only for final evaluation; no fitting, feature selection, calibration, or threshold tuning occurs on Set B.",
        "Patient-level 60/40 split is made within Set A; the held-out Set A patients are not used for model or threshold selection.",
        "The fixed threshold and refractory period are research defaults, not clinically selected alarm settings.",
        "Forecast-window coverage and alerts outside forecast-positive windows are not event-level sensitivity or verified clinical false-alarm rates.",
        "The Challenge label already uses a six-hour lead convention; results do not estimate independently observed sepsis onset.",
    ]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--set-b-cache", type=Path, required=True)
    parser.add_argument("--horizons", type=int, nargs="+", default=[1, 3, 6])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--refractory-hours", type=int, default=6)
    parser.add_argument("--bootstrap-replicates", type=int, default=200)
    parser.add_argument("--predict-chunk-rows", type=int, default=50000)
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    args = parser.parse_args()
    if not args.horizons or any(h < 1 for h in args.horizons) or len(set(args.horizons)) != len(args.horizons):
        parser.error("--horizons must contain unique positive integers")
    if not args.seeds or len(set(args.seeds)) != len(args.seeds):
        parser.error("--seeds must contain unique integers")
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be in [0, 1]")
    if args.refractory_hours < 1 or args.bootstrap_replicates < 20 or args.predict_chunk_rows < 1:
        parser.error("refractory hours, bootstrap replicates, and chunk rows must be positive (bootstrap >=20)")

    meta_a, Xa, ya, ga = load_cache(args.set_a_cache, "A")
    meta_b, Xb, yb, gb = load_cache(args.set_b_cache, "B")
    validate_official_cohort(meta_a, ya, ga, "A")
    validate_official_cohort(meta_b, yb, gb, "B")
    if meta_a["columns"] != meta_b["columns"]:
        parser.error("Set A and Set B cache feature schemas differ")

    start = time.time()
    runs = []
    for seed in args.seeds:
        for horizon in args.horizons:
            runs.append(evaluate_one_horizon(
                meta_a, Xa, ya, ga, meta_b, Xb, yb, gb, meta_a["columns"],
                horizon_hours=horizon, seed=seed, threshold=args.threshold,
                refractory_hours=args.refractory_hours, n_bootstrap=args.bootstrap_replicates,
                predict_chunk_rows=args.predict_chunk_rows,
            ))
    summary = {
        "project": "VITALIS",
        "run_type": "cross_cohort_future_challenge_label_horizon_forecasting",
        "cohorts": {
            "set_a": {"patients": int(meta_a["patient_count"]), "hourly_rows": int(meta_a["row_count"]), "positive_hourly_challenge_labels": int(np.asarray(ya).sum())},
            "set_b": {"patients": int(meta_b["patient_count"]), "hourly_rows": int(meta_b["row_count"]), "positive_hourly_challenge_labels": int(np.asarray(yb).sum())},
        },
        "protocol": {
            "horizons_hours": args.horizons,
            "seeds": args.seeds,
            "set_a_patient_split": "60% training / 40% held-out unused, patient-disjoint",
            "set_b": "all eligible rows from all Set B patients; evaluation-only",
            "models": ["static baseline logistic regression", "temporal-feature logistic regression"],
            "threshold": args.threshold,
            "refractory_hours": args.refractory_hours,
            "bootstrap_replicates": args.bootstrap_replicates,
            "bootstrap_unit": "patient",
            "raw_data_or_row_level_predictions_exported": False,
        },
        "runs": runs,
        "numerical_runtime": {
            "threadpool_limit_per_fit_and_prediction": 1,
            "threadpools_observed_after_evaluation": threadpool_info(),
            "note": "BLAS/OpenMP thread limits are applied explicitly around model fitting and prediction; runtime details are retained for reproducibility audits.",
        },
        "elapsed_seconds": round(time.time() - start, 3),
        "interpretation_note": "Retrospective Challenge-label forecast evaluation only; not clinical validation or prediction of independent biological onset.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "runs": len(runs), "elapsed_seconds": summary["elapsed_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
