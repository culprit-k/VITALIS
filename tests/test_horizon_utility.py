import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).parents[1] / "scripts" / "evaluate_horizon_utility.py"
SPEC = importlib.util.spec_from_file_location("horizon_utility", SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_set_a_utility_evaluator_is_synthetic_and_never_loads_set_b():
    rng = np.random.default_rng(31)
    patients, hours = 80, 12
    groups = np.repeat(np.arange(patients), hours)
    labels = np.zeros(patients * hours, dtype=np.int8)
    labels[np.arange(patients) * hours + 9] = 1
    columns = list(MOD.BASE) + ["SyntheticExtra"]
    X = rng.normal(size=(len(labels), len(columns)))
    X[:, columns.index("HR")] += np.repeat(rng.normal(size=patients), hours)
    result = MOD.evaluate_set_a_one(
        {"columns": columns}, X, labels, groups,
        horizon=1, seed=31, chunk_rows=128, refractory_hours=6,
    )
    assert result["set_b_loaded_or_used"] is False
    assert set(result["models"]) == {"static", "temporal"}
    for model in result["models"].values():
        utility = model["utility_sensitivity_development_only"]
        assert utility["thresholds_are_clinically_selected"] is False
        assert utility["costs_clinically_or_economically_elicited"] is False
        assert len(utility["operating_points"]) == len(MOD.UTILITY_THRESHOLDS)
        assert len(utility["cost_scenarios"]) == len(MOD.MISSED_WINDOW_COSTS)
        for point in utility["operating_points"]:
            assert "row_sensitivity" in point
            assert "row_ppv" in point
            assert "alerts_per_at_risk_patient_day" in point
            assert "future_positive_window_coverage" in point
            assert "missed_future_positive_windows" in point


def test_development_split_remains_patient_disjoint():
    groups = np.repeat(np.arange(100), 8)
    labels = np.tile(np.array([0, 0, 0, 0, 0, 0, 0, 1]), 100)
    train, calibration, holdout = MOD._HELPERS.patient_disjoint_three_way_split(labels, groups, 42)
    sets = [set(groups[ix]) for ix in (train, calibration, holdout)]
    assert all(not (sets[i] & sets[j]) for i in range(3) for j in range(i + 1, 3))
