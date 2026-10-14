"""Run matched static and temporal experiments and compare aggregate metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.train_baseline import train_and_evaluate


def compare(data_dir: Path, seed: int) -> dict[str, object]:
    static = train_and_evaluate(data_dir, temporal=False, seed=seed)
    temporal = train_and_evaluate(data_dir, temporal=True, seed=seed)
    personalized = train_and_evaluate(data_dir, temporal=True, seed=seed, personalized=True)
    static_metrics = static["test_metrics"]
    temporal_metrics = temporal["test_metrics"]
    personalized_metrics = personalized["test_metrics"]
    deltas: dict[str, float | None] = {}
    for metric in ("auroc", "auprc", "brier_score", "sensitivity", "specificity", "ppv", "npv"):
        left, right = static_metrics.get(metric), temporal_metrics.get(metric)
        deltas[metric] = None if left is None or right is None else float(right - left)
    personalized_deltas: dict[str, float | None] = {}
    for metric in ("auroc", "auprc", "brier_score", "sensitivity", "specificity", "ppv", "npv"):
        left, right = temporal_metrics.get(metric), personalized_metrics.get(metric)
        personalized_deltas[metric] = None if left is None or right is None else float(right - left)
    return {
        "project": "VITALIS",
        "comparison": "static baseline versus temporal features versus patient-baseline deviations",
        "seed": seed,
        "same_patient_split_strategy": True,
        "static": static,
        "temporal": temporal,
        "personalized": personalized,
        "temporal_minus_static_test_metric_delta": deltas,
        "personalized_minus_temporal_test_metric_delta": personalized_deltas,
        "interpretation": "Deltas are descriptive retrospective row-level comparisons, not proof of clinical benefit.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Local directory of per-patient PSV files")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, required=True, help="Aggregate JSON comparison output")
    args = parser.parse_args()
    report = compare(args.data_dir, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "comparison": report["comparison"],
        "seed": args.seed,
        "temporal_minus_static": report["temporal_minus_static_test_metric_delta"],
        "personalized_minus_temporal": report["personalized_minus_temporal_test_metric_delta"],
    }, indent=2))


if __name__ == "__main__":
    main()
