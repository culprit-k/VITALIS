import numpy as np
import pytest

from vitalis.horizon import (
    build_future_challenge_targets,
    evaluate_horizon_alerts,
    patient_cluster_bootstrap_horizon_alerts,
)


def test_future_target_uses_only_next_rows_and_excludes_current_positive_and_tail():
    labels = [0, 0, 0, 1, 1, 1, 0, 0, 0, 0]
    patients = ["a"] * 7 + ["b"] * 3
    result = build_future_challenge_targets(labels, patients, horizon_hours=2)

    # Patient a contributes source rows 0, 1, 2; rows 3-6 are positive or tail.
    # Patient b is shorter than the horizon plus one, so it contributes no rows.
    assert result.row_indices.tolist() == [0, 1, 2]
    assert result.targets.tolist() == [0, 1, 1]
    assert result.patient_ids.tolist() == ["a", "a", "a"]
    assert result.patient_time_indices.tolist() == [0, 1, 2]


def test_future_target_never_crosses_patient_boundary():
    labels = [0, 0, 1, 0]
    patients = ["a", "a", "b", "b"]
    result = build_future_challenge_targets(labels, patients, horizon_hours=1)
    assert result.row_indices.tolist() == [0]
    assert result.targets.tolist() == [0]


@pytest.mark.parametrize("horizon", [0, -1, 1.5, True])
def test_horizon_must_be_positive_integer(horizon):
    with pytest.raises(ValueError, match="positive integer"):
        build_future_challenge_targets([0, 1, 0], ["a", "a", "a"], horizon)


def test_target_builder_rejects_noncontiguous_patient_blocks():
    with pytest.raises(ValueError, match="contiguous"):
        build_future_challenge_targets([0, 0, 0, 1], ["a", "b", "a", "b"], 1)


def test_patient_warning_metrics_count_forecast_windows_and_refractory_alerts():
    targets = [0, 1, 1, 0, 0, 0, 0]
    probabilities = [0.1, 0.8, 0.9, 0.1, 0.9, 0.1, 0.1]
    patients = ["a", "a", "a", "a", "b", "b", "b"]
    times = [0, 1, 2, 3, 0, 1, 2]
    result = evaluate_horizon_alerts(
        targets, probabilities, patients, times, threshold=0.5, refractory_hours=2
    )
    assert result["patients"] == 2
    assert result["eligible_hours"] == 7
    assert result["alerts_total"] == 3
    assert result["future_positive_windows"] == 1
    assert result["covered_future_positive_windows"] == 1
    assert result["future_positive_window_coverage"] == 1
    assert result["warning_lead_hours_to_challenge_label_entry"]["mean"] == 2
    assert result["alerts_outside_future_positive_windows"] == 2
    assert "not clinical onset" in result["interpretation_note"]


def test_warning_metrics_validate_probabilities_and_time_order():
    with pytest.raises(ValueError, match="probabilities"):
        evaluate_horizon_alerts([0], [1.2], ["a"], [0])
    with pytest.raises(ValueError, match="strictly increasing"):
        evaluate_horizon_alerts([0, 0], [0.1, 0.2], ["a", "a"], [1, 1])


def test_patient_cluster_bootstrap_returns_intervals():
    result = patient_cluster_bootstrap_horizon_alerts(
        targets=[0, 1, 1, 0, 0, 0],
        probabilities=[0.1, 0.8, 0.9, 0.1, 0.9, 0.1],
        patient_ids=["a", "a", "a", "a", "b", "b"],
        patient_time_indices=[0, 1, 2, 3, 0, 1],
        threshold=0.5,
        refractory_hours=2,
        n_bootstrap=20,
        seed=7,
    )
    assert result["unique_patients"] == 2
    interval = result["intervals"]["alerts_per_at_risk_patient_day"]
    assert interval["lower_95"] is not None
    assert interval["upper_95"] is not None
    assert interval["requested_replicates"] == 20
