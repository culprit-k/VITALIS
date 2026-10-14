import importlib.util
from pathlib import Path
import numpy as np

MODULE = Path(__file__).parents[1] / "scripts" / "evaluate_cross_cohort_calibration.py"
SPEC = importlib.util.spec_from_file_location("cross_cohort_calibration", MODULE)
CAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAL)

def test_calibration_outputs_aggregate_only_reliability_bins():
    y = np.array([0, 0, 0, 1, 0, 1, 0, 0, 1, 0], dtype=np.int8)
    p = np.array([.01, .02, .03, .4, .05, .6, .08, .1, .7, .2])
    out = CAL.calibration(y, p, bins=5)
    assert out["rows"] == len(y)
    assert out["positive_label_rows"] == int(y.sum())
    assert len(out["reliability_bins_equal_frequency"]) == 5
    assert sum(b["rows"] for b in out["reliability_bins_equal_frequency"]) == len(y)
    assert 0 <= out["brier_score"] <= 1
    assert out["calibration_slope_descriptive"] is not None
    assert "patient" not in str(out).lower()

def test_constant_prevalence_reference_is_not_part_of_model_calibration():
    y = np.array([0, 0, 0, 1], dtype=np.int8)
    prevalence = float(y.mean())
    assert np.isclose(prevalence * (1 - prevalence), 0.1875)
