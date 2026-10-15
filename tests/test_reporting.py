"""Tests for aggregate-only report validation and normalization."""
import pytest

from vitalis.reporting import AggregateReportError, normalize_aggregate_report


def test_normalizes_baseline_metrics() -> None:
    result = normalize_aggregate_report({
        "model": "static",
        "patient_counts": {"test": 12},
        "test_metrics": {
            "auroc": 0.71, "auprc": 0.08, "rows": 99,
            "confusion_matrix": {"tp": 2, "fp": 3, "tn": 5, "fn": 2},
        },
        "test_alert_burden": {"alerts_per_patient_day": 0.4},
        "limitations": ["Synthetic test report."],
    })
    assert result["kind"] == "baseline"
    assert result["patient_counts"]["test"] == 12
    assert result["confusion_matrix"] == {"tp": 2, "fp": 3, "tn": 5, "fn": 2}
    assert result["test_alert_burden"] == {"alerts_per_patient_day": 0.4}
    assert result["limitations"] == ["Synthetic test report."]
    assert {row["metric"] for row in result["rows"]} == {"auroc", "auprc"}
    assert all(row["value"] >= 0 for row in result["rows"])


def test_normalizes_cross_cohort_horizon_metrics() -> None:
    result = normalize_aggregate_report({
        "project": "VITALIS",
        "aggregate_by_horizon": [{
            "horizon_hours": 3,
            "models": {
                "static": {
                    "auroc": [0.7, 0.02],
                    "alerts_per_at_risk_patient_day": [1.2, 0.1],
                    "coverage_bootstrap_interval_endpoint_mean": [0.2, 0.3],
                }
            },
        }],
    })
    assert result["kind"] == "horizon_aggregate"
    assert len(result["rows"]) == 2
    auroc = next(row for row in result["rows"] if row["metric"] == "auroc")
    assert auroc == {
        "metric": "auroc",
        "model": "static",
        "horizon_hours": 3,
        "mean": 0.7,
        "sample_sd": 0.02,
    }


def test_normalizes_source_verified_flat_aggregate_metrics() -> None:
    result = normalize_aggregate_report({
        "aggregate_metrics": [{
            "horizon_hours": 6,
            "model": "temporal",
            "auroc": {"mean": 0.68, "sd": 0.01},
            "brier_score": {"mean": 0.14, "sd": 0.004},
        }],
    })
    assert result["kind"] == "horizon_aggregate"
    assert len(result["rows"]) == 2
    assert result["rows"][0]["horizon_hours"] == 6


@pytest.mark.parametrize("report", [None, [], {"unexpected": True}])
def test_rejects_unsupported_report_shapes(report: object) -> None:
    with pytest.raises(AggregateReportError):
        normalize_aggregate_report(report)


def test_rejects_patient_level_prediction_field_variants() -> None:
    with pytest.raises(AggregateReportError, match="row-level"):
        normalize_aggregate_report({
            "patient_counts": {"test": 1},
            "test_metrics": {"auroc": 0.7},
            "patient_level_predictions": [0.2, 0.9],
        })


def test_rejects_row_level_prediction_fields() -> None:
    report = {
        "patient_counts": {"test": 1},
        "test_metrics": {"auroc": 0.7},
        "predictions": [{"patient_id": "example", "score": 0.9}],
    }
    with pytest.raises(AggregateReportError, match="row-level"):
        normalize_aggregate_report(report)


def test_rejects_non_finite_metric_values() -> None:
    with pytest.raises(AggregateReportError, match="finite number"):
        normalize_aggregate_report({
            "patient_counts": {"test": 1},
            "test_metrics": {"auroc": float("nan")},
        })


def test_rejects_invalid_horizon() -> None:
    with pytest.raises(AggregateReportError, match="positive integer"):
        normalize_aggregate_report({
            "aggregate_by_horizon": [{
                "horizon_hours": 0,
                "models": {"static": {"auroc": [0.7, 0.1]}},
            }],
        })
