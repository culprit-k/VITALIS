#!/usr/bin/env python3
"""Patient-level feature availability audit for local VITALIS feature caches.

This is descriptive cohort characterization, not a missingness-mechanism test.
Only aggregate counts/rates are written; patient identifiers and row-level data
must remain local and outside version control.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


DEFAULT_FEATURES = [
    "DBP", "HCO3", "BaseExcess", "FiO2", "pH", "PaCO2",
    "EtCO2", "Resp", "Unit1", "Glucose", "Lactate",
]


def audit_cache(cache_dir: Path, feature_names: list[str] | None = None) -> dict:
    meta = json.loads((cache_dir / "meta.json").read_text(encoding="utf-8"))
    columns = meta.get("columns")
    rows = meta.get("row_count")
    patients = meta.get("patient_count")
    if not isinstance(columns, list) or not isinstance(rows, int) or not isinstance(patients, int):
        raise ValueError("cache metadata must include columns, row_count, and patient_count")
    col_index = {name: i for i, name in enumerate(columns)}
    selected = feature_names or DEFAULT_FEATURES
    missing = sorted(set(selected) - set(col_index))
    if missing:
        raise ValueError(f"requested features absent from cache schema: {missing}")

    X = np.load(cache_dir / "X.npy", mmap_mode="r", allow_pickle=False)
    y = np.load(cache_dir / "y.npy", mmap_mode="r", allow_pickle=False)
    groups = np.load(cache_dir / "g.npy", mmap_mode="r", allow_pickle=False)
    if X.ndim != 2 or X.shape != (rows, len(columns)) or len(y) != rows or len(groups) != rows:
        raise ValueError("cache array dimensions do not match metadata")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be binary")
    unique_groups, starts, counts = np.unique(groups, return_index=True, return_counts=True)
    if len(unique_groups) != patients:
        raise ValueError("group count does not match metadata patient_count")
    order = np.argsort(starts)
    starts, counts = starts[order], counts[order]
    if not np.array_equal(starts[1:], starts[:-1] + counts[:-1]):
        raise ValueError("patient rows are not contiguous in cache; cannot safely aggregate by slices")

    patient_positive = np.zeros(patients, dtype=bool)
    patient_available = {name: np.zeros(patients, dtype=bool) for name in selected}
    for i, (start, count) in enumerate(zip(starts, counts)):
        end = int(start + count)
        patient_positive[i] = bool(np.any(y[start:end] == 1))
        for name in selected:
            patient_available[name][i] = bool(np.isfinite(X[start:end, col_index[name]]).any())

    features = {}
    for name, available in patient_available.items():
        absent = ~available
        features[name] = {
            "patients_with_any_finite_value": int(available.sum()),
            "patient_availability_rate": float(available.mean()),
            "patients_with_positive_label_feature_present": int((patient_positive & available).sum()),
            "patients_with_positive_label_feature_absent": int((patient_positive & absent).sum()),
            "positive_label_patient_rate_feature_present": float(patient_positive[available].mean()) if available.any() else None,
            "positive_label_patient_rate_feature_absent": float(patient_positive[absent].mean()) if absent.any() else None,
        }
    duration_strata = []
    duration_bins = [
        (1, 24, "1-24 h"),
        (25, 48, "25-48 h"),
        (49, 72, "49-72 h"),
        (73, int(counts.max()), "73+ h"),
    ]
    for lower, upper, label in duration_bins:
        mask = (counts >= lower) & (counts <= upper)
        if not mask.any():
            continue
        positive_mask = mask & patient_positive
        negative_mask = mask & ~patient_positive
        duration_features = {}
        for name, available in patient_available.items():
            duration_features[name] = {
                "availability_rate": float(available[mask].mean()),
                "availability_rate_positive_label": (
                    float(available[positive_mask].mean()) if positive_mask.any() else None
                ),
                "availability_rate_no_positive_label": (
                    float(available[negative_mask].mean()) if negative_mask.any() else None
                ),
            }
        duration_strata.append({
            "duration_hours": label,
            "patients": int(mask.sum()),
            "patients_with_positive_label": int(positive_mask.sum()),
            "positive_label_patient_rate": float(patient_positive[mask].mean()),
            "features": duration_features,
        })

    return {
        "patients": int(patients),
        "hourly_rows": int(rows),
        "patients_with_any_positive_hourly_label": int(patient_positive.sum()),
        "patient_positive_label_rate": float(patient_positive.mean()),
        "median_rows_per_patient": float(np.median(counts)),
        "p90_rows_per_patient": float(np.quantile(counts, 0.9)),
        "features": features,
        "duration_strata": duration_strata,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--set-a-cache", type=Path, required=True)
    parser.add_argument("--set-b-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        a = audit_cache(args.set_a_cache)
        b = audit_cache(args.set_b_cache)
        if a["features"].keys() != b["features"].keys():
            raise ValueError("cohort feature sets differ")
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    result = {
        "project": "VITALIS",
        "analysis": "patient-level feature availability and descriptive association with any positive hourly SepsisLabel",
        "cohorts": {"set_a": a, "set_b": b},
        "method": {
            "unit_of_analysis": "patient",
            "feature_available": "at least one finite value in a patient's record",
            "outcome": "at least one positive hourly SepsisLabel in a patient's record",
            "set_b_role": "evaluation-cohort characterization only; not used for fitting, feature selection, or tuning",
            "causal_or_missingness_mechanism_claim": False,
            "model_fitted": False,
            "row_level_data_exported": False,
            "patient_ids_exported": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"Patient-level audit: Set A {a['patients']:,} patients, Set B {b['patients']:,}; "
        f"{len(a['features'])} features. Aggregate output only."
    )


if __name__ == "__main__":
    main()
