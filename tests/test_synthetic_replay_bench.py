"""Tests for the aggregate-only synthetic replay bench harness."""
from scripts.run_synthetic_bench import run_bench


def test_synthetic_bench_functional_checks_pass_and_report_is_aggregate_only():
    report = run_bench(frames=40)
    assert report["functional_status"] == "pass"
    assert all(report["functional_checks"].values())
    assert report["patient_data_used"] is False
    assert report["row_level_data_retained"] is False
    assert report["clinical_use"] is False
    assert "observations" not in report
    assert "predictions" not in report
    assert "patient_id" not in report


def test_synthetic_bench_rejects_too_short_replay():
    import pytest

    with pytest.raises(ValueError, match="at least 30"):
        run_bench(frames=10)
