import numpy as np
import pytest

from scripts.evaluate_set_a_threshold_sweep import (
    cluster_intervals,
    row_metrics,
    threshold_grid,
)


def test_threshold_grid_is_sorted_unique_and_contains_predeclared_points():
    grid = threshold_grid()
    assert grid == sorted(set(grid))
    assert len(grid) == 103
    for point in (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10, 0.50, 0.99):
        assert point in grid


def test_threshold_metrics_use_inclusive_threshold_and_aggregate_counts():
    result = row_metrics(
        np.asarray([0, 0, 1, 1]),
        np.asarray([0.1, 0.5, 0.5, 0.9]),
        0.5,
    )
    assert result["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 0, "tp": 2}
    assert result["sensitivity"] == 1.0
    assert result["specificity"] == 0.5
    assert result["ppv"] == pytest.approx(2 / 3)
    assert result["npv"] == 1.0


def test_patient_cluster_intervals_are_deterministic_and_aggregate_only():
    y = np.asarray([0, 1, 0, 1, 0, 1])
    p = np.asarray([0.1, 0.8, 0.2, 0.7, 0.3, 0.9])
    groups = np.asarray(["a", "a", "b", "b", "c", "c"])
    a = cluster_intervals(y, p, groups, 0.5, 40, 7)
    b = cluster_intervals(y, p, groups, 0.5, 40, 7)
    assert a == b
    assert a["method"] == "patient-cluster percentile bootstrap"
    assert a["sensitivity"]["requested_replicates"] == 40
    assert a["ppv"]["lower_95"] is not None
    assert "patient_ids" not in str(a).lower()
