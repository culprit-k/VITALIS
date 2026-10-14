"""Run reproducible matched static-versus-temporal evaluations across patient split seeds.

Outputs aggregate metrics only. The source patient-level data and predictions are never exported.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, stdev

from scripts.compare_models import compare

METRICS = ("auroc", "auprc", "brier_score", "sensitivity", "specificity", "ppv", "npv")


def compact_result(report: dict[str, object]) -> dict[str, object]:
    """Keep aggregate metrics and cohort counts; omit feature lists and row-level predictions."""
    static = report["static"]
    temporal = report["temporal"]
    assert isinstance(static, dict) and isinstance(temporal, dict)
    return {
        "seed": report["seed"],
        "static": {
            "patient_counts": static["patient_counts"],
            "row_counts": static["row_counts"],
            "test_metrics": static["test_metrics"],
            "bootstrap_intervals": static["test_metric_patient_bootstrap_95ci"],
            "alert_burden": static["test_alert_burden"],
        },
        "temporal": {
            "patient_counts": temporal["patient_counts"],
            "row_counts": temporal["row_counts"],
            "test_metrics": temporal["test_metrics"],
            "bootstrap_intervals": temporal["test_metric_patient_bootstrap_95ci"],
            "alert_burden": temporal["test_alert_burden"],
        },
        "temporal_minus_static_test_metric_delta": report["temporal_minus_static_test_metric_delta"],
    }


def summarize(reports: list[dict[str, object]]) -> dict[str, object]:
    """Summarize seed-to-seed variability; SD is not a confidence interval."""
    summary: dict[str, object] = {}
    for model_name in ("static", "temporal"):
        summary[model_name] = {}
        for metric in METRICS:
            values = [
                float(report[model_name]["test_metrics"][metric])
                for report in reports
                if report[model_name]["test_metrics"].get(metric) is not None
            ]
            summary[model_name][metric] = {
                "mean_across_seeds": mean(values) if values else None,
                "sd_across_seeds": stdev(values) if len(values) > 1 else (0.0 if values else None),
                "valid_seeds": len(values),
            }
    summary["temporal_minus_static_delta"] = {}
    for metric in METRICS:
        values = [
            float(report["temporal_minus_static_test_metric_delta"][metric])
            for report in reports
            if report["temporal_minus_static_test_metric_delta"].get(metric) is not None
        ]
        summary["temporal_minus_static_delta"][metric] = {
            "mean_across_seeds": mean(values) if values else None,
            "sd_across_seeds": stdev(values) if len(values) > 1 else (0.0 if values else None),
            "valid_seeds": len(values),
        }
    return summary


def run_suite(data_dir: Path, seeds: list[int]) -> dict[str, object]:
    if not seeds:
        raise ValueError("At least one seed is required")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be unique")
    reports = [compact_result(compare(data_dir, seed)) for seed in seeds]
    return {
        "project": "VITALIS",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": "User-supplied local PhysioNet Challenge 2019 patient PSV files",
        "protocol": {
            "seeds": seeds,
            "split_unit": "patient",
            "threshold": 0.5,
            "preprocessing": "fit within training split only",
            "bootstrap": "200 patient-cluster resamples per model and seed",
            "output_policy": "aggregate metrics only; no patient-level records or predictions",
        },
        "per_seed_results": reports,
        "summary": summarize(reports),
        "interpretation_limits": [
            "This is retrospective internal validation on the supplied dataset.",
            "Seed-to-seed standard deviation is not a confidence interval.",
            "Metrics are hourly-row metrics, not patient-level event-detection metrics.",
            "The challenge SepsisLabel already follows its early-warning definition and must not be shifted again.",
            "No external or prospective clinical validation is performed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_dir", type=Path, help="Directory containing per-patient .psv files")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--output", type=Path, required=True, help="Aggregate JSON output path")
    args = parser.parse_args()
    result = run_suite(args.data_dir, args.seeds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "seeds": result["protocol"]["seeds"],
        "summary": result["summary"],
    }, indent=2))


if __name__ == "__main__":
    main()
