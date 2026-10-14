import importlib.util
from pathlib import Path

import numpy as np
import pytest

MODULE = Path(__file__).parents[1] / "scripts" / "evaluate_horizon_calibration.py"
SPEC = importlib.util.spec_from_file_location("horizon_calibration", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_three_way_split_is_patient_disjoint_and_reproducible():
    groups = np.repeat(np.arange(100), 4)
    labels = np.tile(np.array([0, 0, 0, 1]), 100)
    train, calibration, holdout = MOD.patient_disjoint_three_way_split(labels, groups, 42)
    sets = [set(groups[ix]) for ix in (train, calibration, holdout)]
    assert all(not (sets[i] & sets[j]) for i in range(3) for j in range(i + 1, 3))
    again = MOD.patient_disjoint_three_way_split(labels, groups, 42)
    assert all(np.array_equal(a, b) for a, b in zip((train, calibration, holdout), again))
    assert all(len(x) > 0 for x in (train, calibration, holdout))


def test_platt_recalibrator_outputs_finite_probabilities():
    y = np.array([0, 0, 0, 1, 0, 1, 0, 1], dtype=np.int8)
    p = np.array([.01, .02, .04, .3, .08, .6, .12, .8])
    model = MOD.fit_platt_recalibrator(y, p)
    out = MOD.apply_platt_recalibrator(model, np.array([.01, .5, .99]))
    assert out.shape == (3,)
    assert np.isfinite(out).all() and np.all((out > 0) & (out < 1))


@pytest.mark.parametrize("y,p", [
    (np.array([], dtype=np.int8), np.array([])),
    (np.array([0, 1]), np.array([.1])),
    (np.array([0, 0]), np.array([.1, .2])),
    (np.array([0, 1]), np.array([np.nan, .8])),
])
def test_platt_recalibrator_rejects_invalid_inputs(y, p):
    with pytest.raises(ValueError):
        MOD.fit_platt_recalibrator(y, p)


def test_probability_metrics_include_prevalence_reference_and_aggregate_only_bins():
    y = np.array([0, 0, 1, 1], dtype=np.int8)
    p = np.array([.05, .1, .7, .9])
    out = MOD.probability_metrics(y, p)
    assert out["rows"] == 4
    assert out["positive_rows"] == 2
    assert out["constant_prevalence_brier_reference"] == pytest.approx(.25)
    assert out["auroc"] == 1.0
    assert "patient_ids" not in out and "predictions" not in out
    assert all(set(b) == {"lower", "upper", "rows", "mean_predicted", "observed_prevalence"}
               for b in out["calibration_bins"])


def test_threshold_metrics_fixed_boundary_and_confusion_counts():
    out = MOD.threshold_metrics(np.array([0, 0, 1, 1]), np.array([.1, .5, .5, .9]), .5)
    assert out["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 0, "tp": 2}
    assert out["sensitivity"] == 1.0
    assert out["ppv"] == pytest.approx(2 / 3)


def test_threshold_grid_is_predeclared_and_not_empty():
    assert MOD.THRESHOLDS == (.001, .005, .01, .05, .5)
    assert all(0 < x <= 1 for x in MOD.THRESHOLDS)


def test_evaluate_one_reports_paired_static_temporal_bootstrap_on_set_b():
    rng = np.random.default_rng(17)
    n_patients, hours = 60, 10
    columns = list(MOD.BASE) + ["SyntheticExtra"]
    groups = np.repeat(np.arange(n_patients), hours)
    labels = np.zeros(n_patients * hours, dtype=np.int8)
    labels[np.arange(n_patients) * hours + 8] = 1
    Xa = rng.normal(size=(len(labels), len(columns)))
    Xb = rng.normal(size=(len(labels), len(columns)))
    Xa[:, columns.index("HR")] += np.repeat(rng.normal(size=n_patients), hours)
    Xb[:, columns.index("HR")] += np.repeat(rng.normal(size=n_patients), hours)
    meta_a = {"columns": columns}
    meta_b = {"columns": columns}
    out = MOD.evaluate_one(
        meta_a, Xa, labels, groups, meta_b, Xb, labels.copy(), groups.copy(),
        horizon=1, seed=17, chunk_rows=128, refractory_hours=6, bootstrap_replicates=20,
    )
    paired = out["set_b_paired_static_vs_temporal_bootstrap_95ci"]
    assert paired["reference_model"] == "static"
    assert paired["comparison_model"] == "temporal"
    assert paired["rows"] == (hours - 1) * n_patients - n_patients
    assert set(paired["intervals_comparison_minus_reference"]) == {"auroc", "auprc", "brier_score", "log_loss"}
    assert out["set_b_used_for_fit_or_threshold_selection"] is False
    utility = out["models"]["static"]["cohorts"]["set_a_untouched_holdout"]["platt_calibrated"]["utility_cost_sensitivity"]
    assert utility["set_b_used_for_threshold_selection"] is False
    assert utility["missed_window_cost_scenarios"] == [1.0, 5.0, 10.0, 20.0]
    assert len(utility["cost_scenarios"]) == 4
    assert all("future_positive_window_coverage" in point for point in utility["operating_points"])
