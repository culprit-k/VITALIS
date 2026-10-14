#!/usr/bin/env python3
"""Evaluate cached VITALIS feature matrices across patient-disjoint split seeds.

This emits aggregate metrics only. It never writes row-level predictions or patient IDs.
The cache is local derived data and must not be committed.
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

BASE = [
    "HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2",
    "BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN",
    "Alkalinephos", "Calcium", "Chloride", "Creatinine", "Bilirubin_direct",
    "Glucose", "Lactate", "Magnesium", "Phosphate", "Potassium",
    "Bilirubin_total", "TroponinI", "Hct", "Hgb", "PTT", "WBC",
    "Fibrinogen", "Platelets", "Age", "Gender", "Unit1", "Unit2",
    "HospAdmTime", "ICULOS",
]


def metrics(y_true: np.ndarray, probability: np.ndarray) -> dict:
    pred = probability >= 0.5
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "rows": int(len(y_true)),
        "positive_label_rows": int(y_true.sum()),
        "threshold": 0.5,
        "auroc": float(roc_auc_score(y_true, probability)),
        "auprc": float(average_precision_score(y_true, probability)),
        "brier_score": float(brier_score_loss(y_true, probability)),
        "sensitivity": float(tp / (tp + fn)) if tp + fn else None,
        "specificity": float(tn / (tn + fp)) if tn + fp else None,
        "ppv": float(tp / (tp + fp)) if tp + fp else None,
        "npv": float(tn / (tn + fn)) if tn + fn else None,
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache-dir", type=Path, required=True)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    meta = json.loads((args.cache_dir / "meta.json").read_text(encoding="utf-8"))
    X = np.load(args.cache_dir / "X.npy", mmap_mode="r")
    y = np.load(args.cache_dir / "y.npy", mmap_mode="r")
    groups = np.load(args.cache_dir / "g.npy", mmap_mode="r")
    if X.shape[0] != meta["row_count"] or y.shape[0] != X.shape[0] or groups.shape[0] != X.shape[0]:
        ap.error("Feature cache dimensions do not match metadata")
    if len(np.unique(groups)) != meta["patient_count"]:
        ap.error("Feature cache has an incomplete or corrupt patient group vector")
    columns = meta["columns"]
    col_index = {name: i for i, name in enumerate(columns)}
    static_index = np.asarray([col_index[name] for name in BASE], dtype=int)
    runs = []
    started = time.time()
    for seed in args.seeds:
        split_started = time.time()
        train_val, test = next(
            GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed).split(np.zeros(len(y)), y, groups)
        )
        train_rel, val_rel = next(
            GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=seed + 1).split(
                np.zeros(len(train_val)), y[train_val], groups[train_val]
            )
        )
        train, validation = train_val[train_rel], train_val[val_rel]
        train_patients, validation_patients, test_patients = set(groups[train]), set(groups[validation]), set(groups[test])
        if train_patients & validation_patients or train_patients & test_patients or validation_patients & test_patients:
            raise RuntimeError(f"Patient overlap detected for seed {seed}")
        test = np.sort(test)
        test_labels = y[test]
        seed_result = {
            "seed": seed,
            "patient_counts": {"train": len(train_patients), "validation": len(validation_patients), "test": len(test_patients)},
            "row_counts": {"train": len(train), "validation": len(validation), "test": len(test)},
            "positive_rows": {"train": int(y[train].sum()), "validation": int(y[validation].sum()), "test": int(y[test].sum())},
            "models": {},
        }
        for name, indices in (("static", static_index), ("temporal", np.arange(X.shape[1]))):
            model = make_pipeline(
                SimpleImputer(strategy="median", add_indicator=True),
                StandardScaler(),
                LogisticRegression(max_iter=500, class_weight="balanced", solver="lbfgs", random_state=seed),
            )
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                fit_started = time.time()
                model.fit(X[np.ix_(train, indices)], y[train])
                fit_seconds = time.time() - fit_started
            probability = model.predict_proba(X[np.ix_(test, indices)])[:, 1]
            seed_result["models"][name] = {
                "features_available": int(len(indices)),
                "fit_seconds": fit_seconds,
                "warnings": [str(w.message) for w in caught],
                "test_metrics": metrics(test_labels, probability),
            }
            print(
                f"seed={seed} model={name} AUROC={seed_result['models'][name]['test_metrics']['auroc']:.4f} "
                f"AUPRC={seed_result['models'][name]['test_metrics']['auprc']:.4f}",
                flush=True,
            )
        seed_result["elapsed_seconds"] = time.time() - split_started
        runs.append(seed_result)
    aggregate = {}
    for model_name in ("static", "temporal"):
        aggregate[model_name] = {}
        for metric_name in ("auroc", "auprc", "brier_score", "sensitivity", "specificity", "ppv", "npv"):
            values = [r["models"][model_name]["test_metrics"][metric_name] for r in runs]
            aggregate[model_name][metric_name] = {
                "mean": float(np.mean(values)),
                "sample_sd_across_seeds": float(np.std(values, ddof=1)) if len(values) > 1 else None,
                "by_seed": {str(r["seed"]): r["models"][model_name]["test_metrics"][metric_name] for r in runs},
            }
    result = {
        "project": "VITALIS",
        "run_type": "cached_feature_matrix_multiseed",
        "dataset": {"patients": meta["patient_count"], "hourly_rows": meta["row_count"], "positive_hourly_labels": int(y.sum())},
        "protocol": {
            "seeds": args.seeds,
            "patient_disjoint_splits": True,
            "model": "LogisticRegression with median imputation, missingness indicators, standard scaling, class_weight=balanced",
            "threshold": 0.5,
            "uncertainty_note": "SD is across split seeds, not a confidence interval. This runner does not export row-level predictions.",
            "temporal_assumption": "Rows in each patient file are treated as chronological hourly observations.",
        },
        "runs": runs,
        "aggregate_metrics": aggregate,
        "elapsed_seconds": time.time() - started,
        "limitations": [
            "Retrospective internal data only; no external/prospective validation.",
            "Hourly challenge-label metrics are not patient-level event sensitivity or clinical false-alarm rates.",
            "Threshold 0.5 is a research comparison threshold, not a clinical operating point.",
            "The local cache must not be committed; it contains derived patient-level rows.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote aggregate-only result to {args.output}", flush=True)


if __name__ == "__main__":
    main()
