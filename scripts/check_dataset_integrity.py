"""Validate aggregate integrity of a local PhysioNet Challenge PSV partition.

The report intentionally omits filenames, patient identifiers, rows, and predictions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

TARGET = "SepsisLabel"


def check_dataset(data_dir: Path) -> dict[str, object]:
    files = sorted(data_dir.glob("*.psv"))
    if not files:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")

    total_rows = 0
    positive_rows = 0
    patients_with_positive_labels = 0
    invalid_target_rows = 0
    empty_files = 0
    inconsistent_columns = 0
    canonical_columns: tuple[str, ...] | None = None
    min_rows: int | None = None
    max_rows = 0
    total_missing_cells = 0
    columns_seen: set[str] = set()

    for path in files:
        frame = pd.read_csv(path, sep="|")
        if frame.empty:
            empty_files += 1
        columns = tuple(map(str, frame.columns))
        columns_seen.update(columns)
        if canonical_columns is None:
            canonical_columns = columns
        elif set(columns) != set(canonical_columns):
            inconsistent_columns += 1
        if TARGET not in frame.columns:
            raise ValueError(f"A patient file is missing required target column {TARGET}")
        labels = pd.to_numeric(frame[TARGET], errors="coerce")
        invalid_target_rows += int((~labels.isin([0, 1])).sum())
        positives = int(labels.eq(1).sum())
        patients_with_positive_labels += int(positives > 0)
        rows = int(len(frame))
        total_rows += rows
        positive_rows += positives
        min_rows = rows if min_rows is None else min(min_rows, rows)
        max_rows = max(max_rows, rows)
        total_missing_cells += int(frame.isna().sum().sum())

    if invalid_target_rows:
        raise ValueError(f"Found {invalid_target_rows} missing or non-binary target rows")
    if empty_files:
        raise ValueError(f"Found {empty_files} empty patient files")

    return {
        "patient_file_count": len(files),
        "hourly_row_count": total_rows,
        "positive_challenge_label_rows": positive_rows,
        "patients_with_positive_challenge_labels": patients_with_positive_labels,
        "positive_label_row_fraction": positive_rows / total_rows,
        "invalid_target_rows": invalid_target_rows,
        "empty_files": empty_files,
        "files_with_column_set_mismatch": inconsistent_columns,
        "column_count_union": len(columns_seen),
        "columns_union": sorted(columns_seen),
        "min_rows_per_patient": min_rows,
        "max_rows_per_patient": max_rows,
        "missing_cells": total_missing_cells,
        "target": TARGET,
        "label_semantics": "Challenge SepsisLabel used as supplied; do not shift again.",
        "privacy": "Aggregate only; no filenames, patient identifiers, rows, or predictions exported.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = check_dataset(args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "columns_union"}, indent=2))


if __name__ == "__main__":
    main()
