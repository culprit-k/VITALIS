"""Run a deterministic patient-sampled static-versus-temporal comparison.

Only aggregate metrics are written. Patient identifiers, source rows, and
patient-level predictions remain local and are not included in the output.
"""
from __future__ import annotations

import argparse
import json
import random
import tempfile
from pathlib import Path

from scripts.compare_models import compare


def select_patient_files(data_dir: Path, sample_size: int, sampling_seed: int) -> list[Path]:
    files = sorted(data_dir.glob("*.psv"))
    if not files:
        raise FileNotFoundError(f"No .psv files found in {data_dir}")
    if sample_size < 2:
        raise ValueError("sample_size must be at least 2")
    if sample_size > len(files):
        raise ValueError(f"Requested {sample_size} patients, but only {len(files)} files exist")
    return sorted(random.Random(sampling_seed).sample(files, sample_size))


def run_subset(data_dir: Path, sample_size: int = 1500, sampling_seed: int = 2026, split_seed: int = 42) -> dict[str, object]:
    selected = select_patient_files(data_dir, sample_size, sampling_seed)
    # The existing training workflow accepts a directory; symlinks avoid copying
    # the source cohort. The temporary directory is removed after both runs.
    with tempfile.TemporaryDirectory(prefix="vitalis_subset_") as temporary:
        subset_dir = Path(temporary)
        for index, path in enumerate(selected):
            (subset_dir / f"patient_{index:06d}.psv").symlink_to(path.resolve())
        report = compare(subset_dir, split_seed)
    return {
        "project": "VITALIS",
        "run_type": "deterministic patient-sampled exploratory comparison",
        "dataset_partition": data_dir.name,
        "cohort": {
            "sampled_patient_files": len(selected),
            "sampling_seed": sampling_seed,
            "sampling": "Uniform sample without replacement from sorted PSV paths",
        },
        "protocol": {
            "split_seed": split_seed,
            "split_unit": "patient",
            "same_patient_split_for_both_models": True,
            "threshold": 0.5,
            "model": "LogisticRegression(max_iter=500,class_weight=balanced,lbfgs)",
            "output_privacy": "Aggregate metrics only; no patient identifiers or predictions",
        },
        "results": {
            "static": {
                "patient_counts": report["static"]["patient_counts"],
                "row_counts": report["static"]["row_counts"],
                "test_metrics": report["static"]["test_metrics"],
                "bootstrap_intervals": report["static"].get("test_metric_patient_bootstrap_95ci"),
            },
            "temporal": {
                "patient_counts": report["temporal"]["patient_counts"],
                "row_counts": report["temporal"]["row_counts"],
                "test_metrics": report["temporal"]["test_metrics"],
                "bootstrap_intervals": report["temporal"].get("test_metric_patient_bootstrap_95ci"),
            },
        },
        "temporal_minus_static_test_metric_delta": report["temporal_minus_static_test_metric_delta"],
        "limitations": [
            "Exploratory subset only; not full-cohort or external validation.",
            "Metrics are hourly-row metrics, not patient-level event metrics.",
            "Threshold 0.5 is a fixed reference threshold, not clinically selected.",
            "The challenge SepsisLabel already uses a six-hour lead convention and is not shifted again.",
            "No clinical utility, novelty, or patentability claim.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Local folder containing one PSV file per patient")
    parser.add_argument("--sample-size", type=int, default=1500)
    parser.add_argument("--sampling-seed", type=int, default=2026)
    parser.add_argument("--split-seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True, help="Aggregate-only JSON output")
    args = parser.parse_args()
    report = run_subset(args.data_dir, args.sample_size, args.sampling_seed, args.split_seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "sampled_patient_files": report["cohort"]["sampled_patient_files"],
        "split_seed": args.split_seed,
        "deltas": report["temporal_minus_static_test_metric_delta"],
        "output": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
