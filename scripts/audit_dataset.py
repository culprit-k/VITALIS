"""Audit a local directory of per-patient PSV files without exporting rows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

TARGET = "SepsisLabel"


def audit_directory(data_dir: Path) -> dict[str, object]:
    files = sorted(data_dir.glob("*.psv"))
    if not files:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")

    total_rows = 0
    positive_rows = 0
    invalid_targets = 0
    missing_cells = 0
    columns_seen: set[str] = set()
    patients_with_positive_label = 0
    row_counts: list[int] = []

    for file_path in files:
        frame = pd.read_csv(file_path, sep="|")
        if TARGET not in frame.columns:
            raise ValueError(f"{file_path.name} is missing required target column {TARGET}")
        labels = pd.to_numeric(frame[TARGET], errors="coerce")
        invalid_targets += int((~labels.isin([0, 1])).sum())
        positives = int(labels.eq(1).sum())
        patients_with_positive_label += int(positives > 0)
        total_rows += len(frame)
        positive_rows += positives
        missing_cells += int(frame.isna().sum().sum())
        row_counts.append(len(frame))
        columns_seen.update(map(str, frame.columns))

    if invalid_targets:
        raise ValueError(f"Found {invalid_targets} target values outside binary 0/1 or missing")

    return {
        "patient_file_count": len(files),
        "total_hourly_rows": total_rows,
        "positive_label_rows": positive_rows,
        "patients_with_positive_label": patients_with_positive_label,
        "missing_cells": missing_cells,
        "columns": sorted(columns_seen),
        "min_rows_per_patient": min(row_counts),
        "max_rows_per_patient": max(row_counts),
        "mean_rows_per_patient": round(sum(row_counts) / len(row_counts), 3),
        "target_column": TARGET,
        "note": "Aggregate audit only; no patient-level records are written.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Local folder containing one PSV file per patient")
    parser.add_argument("--output", type=Path, help="Optional aggregate JSON output path outside the repository")
    args = parser.parse_args()
    report = audit_directory(args.data_dir)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
