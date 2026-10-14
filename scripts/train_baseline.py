"""Train a research-only logistic baseline with patient-level holdout evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from vitalis.features import add_temporal_features
from vitalis.validation import assert_disjoint_patient_splits

TARGET = "SepsisLabel"
CANDIDATE_FEATURES = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2",
    "BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN",
    "Alkalinephos", "Calcium", "Chloride", "Creatinine", "Bilirubin_direct",
    "Glucose", "Lactate", "Magnesium", "Phosphate", "Potassium",
    "Bilirubin_total", "TroponinI", "Hct", "Hgb", "PTT", "WBC", "Fibrinogen",
    "Platelets", "Age", "Gender", "Unit1", "Unit2", "HospAdmTime", "ICULOS",
]
MEASUREMENTS = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2", "BaseExcess",
    "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "BUN", "Creatinine", "Glucose", "Lactate",
    "Potassium", "Hct", "Hgb", "WBC", "Platelets",
]


def load_patient_rows(data_dir: Path, temporal: bool) -> tuple[pd.DataFrame, pd.Series, pd.Series, list[str]]:
    paths = sorted(data_dir.glob("*.psv"))
    if not paths:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")
    frames: list[pd.DataFrame] = []
    labels: list[pd.Series] = []
    groups: list[pd.Series] = []
    used_features: list[str] | None = None

    for index, path in enumerate(paths):
        frame = pd.read_csv(path, sep="|")
        if TARGET not in frame.columns:
            raise ValueError(f"{path.name} lacks {TARGET}")
        y = pd.to_numeric(frame[TARGET], errors="coerce")
        if y.isna().any() or not y.isin([0, 1]).all():
            raise ValueError(f"{path.name} has missing or non-binary {TARGET} values")
        features = [c for c in CANDIDATE_FEATURES if c in frame.columns]
        if not features:
            raise ValueError(f"No supported predictors found in {path.name}")
        x = frame[features].apply(pd.to_numeric, errors="coerce")
        if temporal:
            temporal_cols = [c for c in MEASUREMENTS if c in x.columns]
            temp = add_temporal_features(
                pd.concat([pd.Series([index] * len(frame), name="_patient"), x], axis=1),
                patient_col="_patient", value_cols=temporal_cols, window=6,
            ).drop(columns="_patient")
            x = pd.concat([x, temp[[c for c in temp.columns if c not in x.columns]]], axis=1)
        if used_features is None:
            used_features = list(x.columns)
        else:
            # Align files with differing column availability without inventing values.
            for column in used_features:
                if column not in x:
                    x[column] = np.nan
            new_columns = [column for column in x.columns if column not in used_features]
            if new_columns:
                for previous in frames:
                    for column in new_columns:
                        previous[column] = np.nan
                used_features.extend(new_columns)
        x = x.reindex(columns=used_features)
        frames.append(x)
        labels.append(y.reset_index(drop=True))
        groups.append(pd.Series([path.stem] * len(frame), name="patient_id"))

    X = pd.concat(frames, ignore_index=True).reindex(columns=used_features)
    y_all = pd.concat(labels, ignore_index=True).astype(int)
    group_all = pd.concat(groups, ignore_index=True)
    return X, y_all, group_all, used_features or []


def calculate_metrics(y_true: pd.Series, probability: np.ndarray, threshold: float) -> dict[str, object]:
    prediction = (probability >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "rows": int(len(y_true)),
        "positive_label_rows": int(y_true.sum()),
        "threshold": threshold,
        "auroc": float(roc_auc_score(y_true, probability)) if y_true.nunique() == 2 else None,
        "auprc": float(average_precision_score(y_true, probability)) if y_true.nunique() == 2 else None,
        "brier_score": float(brier_score_loss(y_true, probability)),
        "sensitivity": float(tp / (tp + fn)) if tp + fn else None,
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "ppv": float(tp / (tp + fp)) if tp + fp else None,
        "npv": float(tn / (tn + fn)) if tn + fn else None,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def train_and_evaluate(data_dir: Path, temporal: bool, seed: int = 42) -> dict[str, object]:
    X, y, groups, features = load_patient_rows(data_dir, temporal)
    first_split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed)
    train_val_idx, test_idx = next(first_split.split(X, y, groups))
    X_train_val, y_train_val, groups_train_val = X.iloc[train_val_idx], y.iloc[train_val_idx], groups.iloc[train_val_idx]
    second_split = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed + 1)
    train_idx, val_idx = next(second_split.split(X_train_val, y_train_val, groups_train_val))
    train_groups = set(groups_train_val.iloc[train_idx])
    val_groups = set(groups_train_val.iloc[val_idx])
    test_groups = set(groups.iloc[test_idx])
    assert_disjoint_patient_splits(train_groups, val_groups, test_groups)

    model = make_pipeline(
        SimpleImputer(strategy="median", add_indicator=True),
        StandardScaler(),
        LogisticRegression(max_iter=500, class_weight="balanced", solver="lbfgs", random_state=seed),
    )
    model.fit(X_train_val.iloc[train_idx], y_train_val.iloc[train_idx])
    validation_probability = model.predict_proba(X_train_val.iloc[val_idx])[:, 1]
    # Fixed, predeclared threshold: no test-set threshold tuning.
    threshold = 0.5
    test_probability = model.predict_proba(X.iloc[test_idx])[:, 1]
    return {
        "project": "VITALIS",
        "model": "logistic_regression_with_median_imputation_and_standard_scaling",
        "feature_mode": "temporal" if temporal else "static_baseline",
        "seed": seed,
        "patient_counts": {"train": len(train_groups), "validation": len(val_groups), "test": len(test_groups)},
        "row_counts": {"train": int(len(train_idx)), "validation": int(len(val_idx)), "test": int(len(test_idx))},
        "features": features,
        "threshold_selection": "fixed 0.5; not tuned on test data",
        "validation_metrics": calculate_metrics(y_train_val.iloc[val_idx], validation_probability, threshold),
        "test_metrics": calculate_metrics(y.iloc[test_idx], test_probability, threshold),
        "limitations": [
            "Retrospective challenge dataset only; no external or prospective validation.",
            "Challenge SepsisLabel already uses a six-hour lead convention; it was not shifted again.",
            "Hourly rows are correlated; row-level metrics do not establish event-level clinical utility.",
            "No patient-level predictions are exported by this script.",
            "Threshold 0.5 is a fixed reference threshold, not a clinically selected operating point.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Local directory of per-patient PSV files")
    parser.add_argument("--temporal", action="store_true", help="Add causal lag/delta/trailing mean features")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True, help="Aggregate metrics JSON path")
    args = parser.parse_args()
    report = train_and_evaluate(args.data_dir, args.temporal, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "features" and k != "limitations"}, indent=2))


if __name__ == "__main__":
    main()
