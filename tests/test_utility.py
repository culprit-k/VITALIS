import importlib.util
from pathlib import Path
import numpy as np
import pytest

MODULE = Path(__file__).parents[1] / "src" / "vitalis" / "utility.py"
SPEC = importlib.util.spec_from_file_location("vitalis_utility", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def fixture():
    y = np.array([0, 1, 1, 0, 0, 0, 1, 0], dtype=np.int8)
    p = np.array([.1, .8, .7, .2, .1, .6, .9, .2])
    groups = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    times = np.array([0, 1, 2, 3, 0, 1, 2, 3])
    return y, p, groups, times


def test_cost_analysis_reports_required_metrics_and_explicit_scenarios():
    y, p, groups, times = fixture()
    result = MOD.evaluate_utility_operating_points(y, p, groups, times,
        thresholds=[.3, .75], missed_window_costs=[1, 10], alert_cost=1, refractory_hours=1)
    assert result["set_b_used_for_threshold_selection"] is False
    assert len(result["operating_points"]) == 2
    point = result["operating_points"][0]
    assert {"row_sensitivity", "row_ppv", "alerts_per_at_risk_patient_day",
            "future_positive_window_coverage", "missed_future_positive_windows"} <= set(point)
    assert len(result["cost_scenarios"]) == 2
    assert all(s["lowest_cost_development_candidate_threshold"] in [.3, .75]
               for s in result["cost_scenarios"])
    assert all(s["selection_warning"] for s in result["cost_scenarios"])


def test_increasing_missed_window_cost_increases_cost_for_fixed_operating_point():
    y, p, groups, times = fixture()
    result = MOD.evaluate_utility_operating_points(y, p, groups, times,
        thresholds=[.3], missed_window_costs=[1, 10], alert_cost=1, refractory_hours=1)
    low, high = result["cost_scenarios"]
    a = low["ranking_by_weighted_cost_per_at_risk_patient_day"][0]["weighted_cost_per_at_risk_patient_day"]
    b = high["ranking_by_weighted_cost_per_at_risk_patient_day"][0]["weighted_cost_per_at_risk_patient_day"]
    assert b >= a


@pytest.mark.parametrize("kwargs", [
    {"thresholds": [], "missed_window_costs": [1]},
    {"thresholds": [1.1], "missed_window_costs": [1]},
    {"thresholds": [.5, .5], "missed_window_costs": [1]},
    {"thresholds": [.5], "missed_window_costs": [0]},
    {"thresholds": [.5], "missed_window_costs": [1], "alert_cost": 0},
])
def test_rejects_invalid_cost_grid(kwargs):
    y, p, groups, times = fixture()
    with pytest.raises(ValueError):
        MOD.evaluate_utility_operating_points(y, p, groups, times, **kwargs)


def test_patient_cluster_bootstrap_reports_metric_intervals_and_selection_stability():
    y, p, groups, times = fixture()
    result = MOD.patient_cluster_bootstrap_utility_uncertainty(
        y, p, groups, times, thresholds=[.3, .75],
        missed_window_costs=[1, 10], alert_cost=1,
        refractory_hours=1, n_bootstrap=40, seed=123,
    )
    assert result["set_b_used_for_threshold_selection"] is False
    assert result["unique_patients"] == 2
    assert result["requested_replicates"] == 40
    metrics = result["threshold_results"][0]["intervals"]
    assert "row_sensitivity" in metrics
    assert "row_ppv" in metrics
    assert "alerts_per_at_risk_patient_day" in metrics
    assert "future_positive_window_coverage" in metrics
    assert "weighted_cost_per_patient_day__miss_cost_10" in metrics
    for scenario in result["cost_scenario_selection_stability"]:
        assert scenario["valid_replicates"] > 0
        assert sum(x["selected_replicates"] for x in scenario["selection_frequency_by_threshold"]) == scenario["valid_replicates"]
        assert sum(x["selection_fraction"] or 0 for x in scenario["selection_frequency_by_threshold"]) == pytest.approx(1.0)


def test_patient_cluster_bootstrap_is_reproducible_and_rejects_small_replicate_count():
    y, p, groups, times = fixture()
    kwargs = dict(thresholds=[.3, .75], missed_window_costs=[1, 10],
                  refractory_hours=1, n_bootstrap=40, seed=7)
    first = MOD.patient_cluster_bootstrap_utility_uncertainty(y, p, groups, times, **kwargs)
    second = MOD.patient_cluster_bootstrap_utility_uncertainty(y, p, groups, times, **kwargs)
    assert first == second
    with pytest.raises(ValueError):
        MOD.patient_cluster_bootstrap_utility_uncertainty(
            y, p, groups, times, thresholds=[.5], missed_window_costs=[1], n_bootstrap=19,
        )
