"""Normalize supported aggregate-only VITALIS result formats for reporting UIs.

This module exposes aggregate metrics only. It does not load cohort files, fit
models, or provide access to row-level predictions.
"""
from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

_FORBIDDEN_KEYS = {
    "patient_id", "patient_ids", "patient_records", "patient_predictions",
    "row_level_predictions", "predictions", "probabilities", "y_true", "y_pred",
    "records", "score_archive",
}
_BASELINE_METRICS = (
    "auroc", "auprc", "brier_score", "sensitivity", "specificity",
    "ppv", "npv", "log_loss",
)


class AggregateReportError(ValueError):
    """Raised when a JSON document is not a supported aggregate-only report."""


def _reject_row_level_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if normalized in _FORBIDDEN_KEYS:
                raise AggregateReportError(
                    f"Unsupported row-level field at {path}.{key}; upload aggregate-only results."
                )
            _reject_row_level_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_row_level_fields(child, f"{path}[{index}]")


def _number(value: Any, *, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise AggregateReportError(f"{field} must be a finite number.")
    result = float(value)
    if not math.isfinite(result):
        raise AggregateReportError(f"{field} must be a finite number.")
    return result


def _metric_row(
    *,
    metric: str,
    value: Any,
    model: str,
    horizon_hours: int | None = None,
    mean_sd: bool = False,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "metric": metric,
        "model": model,
        "horizon_hours": horizon_hours,
    }
    if mean_sd:
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise AggregateReportError(
                f"Aggregate metric {metric!r} must be [mean, sample_sd]."
            )
        row["mean"] = _number(value[0], field=f"{metric}.mean")
        row["sample_sd"] = _number(value[1], field=f"{metric}.sample_sd")
    else:
        row["value"] = _number(value, field=metric)
    return row


def normalize_aggregate_report(report: Any) -> dict[str, Any]:
    """Validate a supported report and return a uniform aggregate-metrics view.

    Supported formats are baseline test_metrics/patient_counts, full cross-cohort
    aggregate_by_horizon, and source-verified aggregate_metrics.
    """
    if not isinstance(report, Mapping):
        raise AggregateReportError("The JSON root must be an object.")
    _reject_row_level_fields(report)

    metadata = {
        "project": report.get("project", "VITALIS"),
        "run_date": report.get("run_date"),
        "run_type": report.get("run_type"),
        "status": report.get("status"),
        "archive_sha256": report.get("archive_sha256"),
        "feature_count": report.get("feature_count"),
        "protocol": report.get("protocol") if isinstance(report.get("protocol"), Mapping) else {},
        "cohorts": report.get("cohorts") if isinstance(report.get("cohorts"), Mapping) else {},
    }
    rows: list[dict[str, Any]] = []

    if isinstance(report.get("test_metrics"), Mapping) and isinstance(
        report.get("patient_counts"), Mapping
    ):
        metrics = report["test_metrics"]
        model = str(report.get("model") or report.get("feature_mode") or "baseline")
        for name in _BASELINE_METRICS:
            if metrics.get(name) is not None:
                rows.append(_metric_row(metric=name, value=metrics[name], model=model))
        if not rows:
            raise AggregateReportError("Baseline report contains no recognized numeric metrics.")
        return {
            "kind": "baseline",
            "metadata": metadata,
            "patient_counts": dict(report["patient_counts"]),
            "rows": rows,
        }

    aggregate_by_horizon = report.get("aggregate_by_horizon")
    if isinstance(aggregate_by_horizon, list) and aggregate_by_horizon:
        for group in aggregate_by_horizon:
            if not isinstance(group, Mapping):
                raise AggregateReportError("Each aggregate_by_horizon entry must be an object.")
            horizon = group.get("horizon_hours")
            if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
                raise AggregateReportError("horizon_hours must be a positive integer.")
            models = group.get("models")
            if not isinstance(models, Mapping):
                raise AggregateReportError("Each horizon entry must contain a models object.")
            for model, metrics in models.items():
                if not isinstance(metrics, Mapping):
                    raise AggregateReportError(f"Metrics for {model!r} must be an object.")
                for name, pair in metrics.items():
                    if name.endswith("_bootstrap_interval_endpoint_mean"):
                        continue
                    if isinstance(pair, (list, tuple)) and len(pair) == 2:
                        rows.append(
                            _metric_row(
                                metric=str(name), value=pair, model=str(model),
                                horizon_hours=horizon, mean_sd=True,
                            )
                        )
        if not rows:
            raise AggregateReportError("No recognized aggregate horizon metrics were found.")
        return {"kind": "horizon_aggregate", "metadata": metadata, "rows": rows}

    aggregate_metrics = report.get("aggregate_metrics")
    if isinstance(aggregate_metrics, list) and aggregate_metrics:
        for entry in aggregate_metrics:
            if not isinstance(entry, Mapping):
                raise AggregateReportError("Each aggregate_metrics entry must be an object.")
            horizon = entry.get("horizon_hours")
            if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
                raise AggregateReportError("horizon_hours must be a positive integer.")
            model = str(entry.get("model") or "unspecified")
            metrics = entry.get("metrics")
            if not isinstance(metrics, Mapping):
                raise AggregateReportError("Each aggregate_metrics entry must contain metrics.")
            for name, summary in metrics.items():
                if not isinstance(summary, Mapping) or "mean" not in summary or "sd" not in summary:
                    continue
                rows.append({
                    "metric": str(name), "model": model, "horizon_hours": horizon,
                    "mean": _number(summary["mean"], field=f"{name}.mean"),
                    "sample_sd": _number(summary["sd"], field=f"{name}.sd"),
                })
        if not rows:
            raise AggregateReportError("No recognized aggregate metrics were found.")
        return {"kind": "horizon_aggregate", "metadata": metadata, "rows": rows}

    raise AggregateReportError(
        "Unsupported report schema. Expected baseline test_metrics, "
        "aggregate_by_horizon, or aggregate_metrics."
    )
