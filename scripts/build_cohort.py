"""Build an aggregate cohort inventory from local patient PSV files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

TARGET = "SepsisLabel"


def build_inventory(data_dir: Path) -> dict[str, object]:
    patient_files = sorted(data_dir.glob("*.psv"))
    if not patient_files:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")

    total_rows = 0
    positive_rows = 0
    positive_patients = 0
    missing_by_column: dict[str, int] = {}
    columns_seen: set[str] = set()
    invalid_target_rows = 0
    lengths: list[int] = []

    for patient_file in patient_files:
        frame = pd.read_csv(patient_file, sep="|")
        if TARGET not in frame.columns:
            raise ValueError(f"{patient_file.name} lacks {TARGET}")
        labels = pd.to_numeric(frame[TARGET], errors="coerce")
        invalid_target_rows += int((~labels.isin([0, 1])).sum())
        positive_count = int(labels.eq(1).sum())
        positive_patients += int(positive_count > 0)
        positive_rows += positive_count
        total_rows += len(frame)
        lengths.append(len(frame))
        columns_seen.update(map(str, frame.columns))
        for column, count in frame.isna().sum().items():
            missing_by_column[str(column)] = missing_by_column.get(str(column), 0) + int(count)

    if invalid_target_rows:
        raise ValueError(f"Invalid or missing binary target values: {invalid_target_rows}")

    return {
        "patient_file_count": len(patient_files),
        "hourly_row_count": total_rows,
        "positive_label_row_count": positive_rows,
        "patients_with_positive_labels": positive_patients,
        "positive_label_row_fraction": round(positive_rows / total_rows, 8),
        "min_rows_per_patient": min(lengths),
        "median_rows_per_patient": float(pd.Series(lengths).median()),
        "max_rows_per_patient": max(lengths),
        "columns": sorted(columns_seen),
        "missing_cells_by_column": dict(sorted(missing_by_column.items())),
        "target_column": TARGET,
        "label_semantics": "Challenge label with six-hour lead convention; do not shift again.",
        "privacy_note": "Aggregate summary only; patient-level records are not exported.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Folder with one .psv file per patient")
    parser.add_argument("--output", type=Path, required=True, help="Aggregate JSON output path")
    args = parser.parse_args()
    report = build_inventory(args.data_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "missing_cells_by_column" and k != "columns"}, indent=2))


if __name__ == "__main__":
    main()
