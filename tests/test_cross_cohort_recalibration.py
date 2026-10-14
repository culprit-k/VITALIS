import importlib.util
from pathlib import Path

import numpy as np
import pytest

MODULE = Path(__file__).parents[1] / "scripts" / "evaluate_cross_cohort_recalibration.py"
SPEC = importlib.util.spec_from_file_location("cross_cohort_recalibration", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_three_way_split_is_patient_disjoint_and_reproducible():
    groups = np.repeat(np.arange(100), 4)
    y = np.tile(np.array([0, 0, 0, 1], dtype=np.int8), 100)
    train, validation, unused = MOD.patient_disjoint_three_way_split(y, groups, 42)
    patient_sets = [set(groups[ix]) for ix in (train, validation, unused)]
    assert not (patient_sets[0] & patient_sets[1])
    assert not (patient_sets[0] & patient_sets[2])
    assert not (patient_sets[1] & patient_sets[2])
    again = MOD.patient_disjoint_three_way_split(y, groups, 42)
    assert all(np.array_equal(a, b) for a, b in zip((train, validation, unused), again))
    assert all(len(ix) > 0 for ix in (train, validation, unused))


def test_platt_recalibrator_is_fit_only_from_passed_validation_arrays():
    y_val = np.array([0, 0, 0, 1, 0, 1, 0, 1], dtype=np.int8)
    p_val = np.array([.01, .02, .04, .3, .08, .6, .12, .8])
    model = MOD.fit_platt_recalibrator(y_val, p_val)
    result = MOD.apply_platt_recalibrator(model, np.array([.01, .5, .99]))
    assert result.shape == (3,)
    assert np.isfinite(result).all()
    assert ((result > 0) & (result < 1)).all()


@pytest.mark.parametrize(
    "y,p",
    [
        (np.array([], dtype=np.int8), np.array([])),
        (np.array([0, 1]), np.array([.1])),
        (np.array([0, 0]), np.array([.1, .2])),
        (np.array([0, 1]), np.array([np.nan, .8])),
    ],
)
def test_platt_recalibrator_rejects_invalid_validation_data(y, p):
    with pytest.raises(ValueError):
        MOD.fit_platt_recalibrator(y, p)


def test_probability_metrics_are_aggregate_only():
    out = MOD.probability_metrics(np.array([0, 0, 1, 1]), np.array([.1, .2, .7, .9]))
    assert out["rows"] == 4
    assert out["positive_label_rows"] == 2
    assert out["auroc"] == 1.0
    assert "predictions" not in out
    assert "patient_ids" not in out
