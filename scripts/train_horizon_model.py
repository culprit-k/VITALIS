"""Train patient-disjoint models to forecast future Challenge SepsisLabel entry.

The target is whether a positive challenge label occurs in the next 1, 3, or
6 hourly rows while the current label is zero. Because the source label already
uses a six-hour lead convention, this is not a forecast of independently
observed sepsis onset. Outputs are aggregate-only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from vitalis.horizon import (
    build_future_challenge_targets,
    evaluate_horizon_alerts,
    patient_cluster_bootstrap_horizon_alerts,
)
from vitalis.validation import assert_disjoint_patient_splits
from scripts.train_baseline import (
    calculate_metrics,
    load_patient_rows,
    observed_training_features,
    patient_cluster_bootstrap_intervals,
)

DEFAULT_HORIZONS = (1, 3, 6)


def train_one_horizon(
    data_dir: Path,
    *,
    horizon_hours: int,
    seed: int = 42,
    threshold: float = 0.5,
    refractory_hours: int = 6,
    n_bootstrap: int = 200,
) -> dict[str, object]:
    """Fit one future-label model with patient-disjoint train/validation/test."""
    X_all, labels, patient_codes, feature_names = load_patient_rows(
        data_dir, temporal=True, personalized=False
    )
    targets = build_future_challenge_targets(labels, patient_codes, horizon_hours)
    if len(targets.row_indices) == 0:
        raise ValueError(f"No eligible rows for {horizon_hours}-hour horizon")

    X = X_all.iloc[targets.row_indices].reset_index(drop=True)
    y = pd.Series(targets.targets, name=f"challenge_positive_within_{horizon_hours}h")
    groups = pd.Series(targets.patient_ids, name="patient_code")
    times = targets.patient_time_indices

    first_split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_val_idx, test_idx = next(first_split.split(X, y, groups))
    X_train_val, y_train_val, groups_train_val = (
        X.iloc[train_val_idx], y.iloc[train_val_idx], groups.iloc[train_val_idx]
    )
    second_split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed + 1)
    train_idx, val_idx = next(second_split.split(X_train_val, y_train_val, groups_train_val))
    train_groups = set(groups_train_val.iloc[train_idx])
    val_groups = set(groups_train_val.iloc[val_idx])
    test_groups = set(groups.iloc[test_idx])
    assert_disjoint_patient_splits(train_groups, val_groups, test_groups)

    train_idx = np.sort(train_idx)
    val_idx = np.sort(val_idx)
    test_idx = np.sort(test_idx)
    train_rows = X_train_val.iloc[train_idx]
    observed_features, dropped_features = observed_training_features(train_rows)
    model = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True),
        StandardScaler(),
        LogisticRegression(
            max_iter=500, class_weight="balanced", solver="lbfgs", random_state=seed
        ),
    )
    y_train = y_train_val.iloc[train_idx]
    if y_train.nunique() < 2:
        raise ValueError(
            f"Training split has one target class for horizon {horizon_hours}; "
            "use a larger cohort or a different predeclared patient split."
        )
    model.fit(train_rows[observed_features], y_train)

    validation_rows = X_train_val.iloc[val_idx]
    validation_probability = model.predict_proba(validation_rows[observed_features])[:, 1]
    test_rows = X.iloc[test_idx]
    test_y = y.iloc[test_idx].reset_index(drop=True)
    test_groups_ordered = groups.iloc[test_idx].reset_index(drop=True)
    test_times = times[test_idx]
    test_probability = model.predict_proba(test_rows[observed_features])[:, 1]

    if test_y.nunique() < 2:
        test_auroc_note = "Test split contains one class; AUROC and AUPRC are undefined."
    else:
        test_auroc_note = None

    warning_metrics = evaluate_horizon_alerts(
        test_y.to_numpy(), test_probability, test_groups_ordered.to_numpy(), test_times,
        threshold=threshold, refractory_hours=refractory_hours,
    )
    warning_uncertainty = patient_cluster_bootstrap_horizon_alerts(
        test_y.to_numpy(), test_probability, test_groups_ordered.to_numpy(), test_times,
        threshold=threshold, refractory_hours=refractory_hours,
        n_bootstrap=n_bootstrap, seed=seed,
    )
    return {
        "horizon_hours": horizon_hours,
        "target_definition": (
            f"current SepsisLabel=0 and any SepsisLabel=1 in the next {horizon_hours} hourly rows; "
            "last horizon rows per patient excluded"
        ),
        "source_label_note": (
            "Forecast of Challenge SepsisLabel-positive-window entry only. The source label "
            "already uses a six-hour lead convention and is not an independent onset timestamp."
        ),
        "model": "balanced logistic regression with median imputation, missingness indicators, standard scaling",
        "seed": seed,
        "threshold": threshold,
        "threshold_note": "Fixed research reference; not selected for clinical use.",
        "refractory_hours": refractory_hours,
        "patient_counts": {
            "train": len(train_groups),
            "validation": len(val_groups),
            "test": len(test_groups),
        },
        "row_counts": {
            "eligible_total": int(len(y)),
            "train": int(len(train_idx)),
            "validation": int(len(val_idx)),
            "test": int(len(test_idx)),
        },
        "target_positive_rows": {
            "eligible_total": int(y.sum()),
            "train": int(y_train.sum()),
            "validation": int(y_train_val.iloc[val_idx].sum()),
            "test": int(test_y.sum()),
        },
        "feature_count": len(observed_features),
        "dropped_all_missing_training_features": dropped_features,
        "validation_metrics": calculate_metrics(
            y_train_val.iloc[val_idx].reset_index(drop=True),
            validation_probability,
            threshold,
        ),
        "test_metrics": calculate_metrics(test_y, test_probability, threshold),
        "test_row_metric_patient_bootstrap_95ci": patient_cluster_bootstrap_intervals(
            test_y, test_probability, test_groups_ordered,
            threshold=threshold, n_bootstrap=n_bootstrap, seed=seed,
        ),
        "test_patient_warning_metrics": warning_metrics,
        "test_patient_warning_metric_bootstrap_95ci": warning_uncertainty,
        "test_class_note": test_auroc_note,
        "limitations": [
            "Retrospective challenge-label forecasting only; no independently observed onset time.",
            "The challenge label already uses a six-hour lead convention; it was not shifted to represent onset.",
            "Patient-disjoint split prevents patient overlap but does not establish external or prospective validity.",
            "Threshold and refractory period are research defaults, not clinically selected alarm settings.",
            "Patient-level alert burden is relative to eligible at-risk hours and challenge-label forecast windows.",
            "No patient-level predictions, identifiers, or raw records are exported.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Local per-patient Challenge PSV files")
    parser.add_argument("--horizons", type=int, nargs="+", default=list(DEFAULT_HORIZONS))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--refractory-hours", type=int, default=6)
    parser.add_argument("--bootstrap-replicates", type=int, default=200)
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    args = parser.parse_args()
    if not args.horizons or any(h < 1 for h in args.horizons):
        parser.error("--horizons must contain positive integers")
    if len(set(args.horizons)) != len(args.horizons):
        parser.error("--horizons cannot contain duplicates")
    if not 0 <= args.threshold <= 1:
        parser.error("--threshold must be in [0, 1]")
    if args.refractory_hours < 1:
        parser.error("--refractory-hours must be positive")
    if args.bootstrap_replicates < 20:
        parser.error("--bootstrap-replicates must be at least 20")

    results = [
        train_one_horizon(
            args.data_dir, horizon_hours=horizon, seed=args.seed,
            threshold=args.threshold, refractory_hours=args.refractory_hours,
            n_bootstrap=args.bootstrap_replicates,
        )
        for horizon in args.horizons
    ]
    report = {
        "project": "VITALIS",
        "run_type": "future_challenge_label_horizon_forecasting",
        "dataset": "Local PhysioNet/CinC Challenge 2019 patient PSV files",
        "protocol": {
            "horizons_hours": args.horizons,
            "split_unit": "patient",
            "split_fractions": {"train": 0.64, "validation": 0.16, "test": 0.20},
            "features": "static baseline plus causal lag, delta, and trailing-six-row features",
            "patient_predictions_exported": False,
            "threshold_selection": "fixed predeclared research reference; no test-set tuning",
        },
        "runs": results,
        "global_limitations": [
            "The target forecasts future Challenge SepsisLabel entry, not sepsis onset.",
            "The Challenge label already incorporates a six-hour lead convention.",
            "All findings are retrospective and require external, prospective, and clinical review.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "run_type": report["run_type"],
        "output": str(args.output),
        "horizons": [
            {
                "hours": run["horizon_hours"],
                "test_auroc": run["test_metrics"]["auroc"],
                "test_auprc": run["test_metrics"]["auprc"],
                "forecast_window_coverage": run["test_patient_warning_metrics"]["future_positive_window_coverage"],
                "alerts_per_at_risk_patient_day": run["test_patient_warning_metrics"]["alerts_per_at_risk_patient_day"],
            }
            for run in results
        ],
        "notice": "Aggregate research metrics only; not clinical validation.",
    }, indent=2))


if __name__ == "__main__":
    main()
