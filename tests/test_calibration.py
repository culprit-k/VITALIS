import numpy as np
import pandas as pd
import pytest

from vitalis.calibration import calibration_summary, missingness_summary


def test_calibration_summary_reports_brier_and_slope_for_two_classes():
    y = np.array([0, 0, 0, 1, 1, 1])
    p = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    result = calibration_summary(y, p, bins=5)
    assert result["rows"] == 6
    assert result["brier_score"] == pytest.approx(0.04666666666666667)
    assert result["calibration_slope"] is not None
    assert result["calibration_intercept"] is not None
    assert sum(row["count"] for row in result["reliability_bins"]) == len(y)


def test_calibration_summary_rejects_invalid_probabilities():
    with pytest.raises(ValueError):
        calibration_summary([0, 1], [-0.1, 0.8])


def test_calibration_summary_returns_null_slope_for_single_class():
    result = calibration_summary([0, 0, 0], [0.1, 0.2, 0.3])
    assert result["calibration_slope"] is None
    assert result["calibration_intercept"] is None


def test_missingness_summary_is_aggregate_and_sorted():
    frame = pd.DataFrame({"HR": [80, np.nan, 90], "Lactate": [np.nan, np.nan, 2.0]})
    result = missingness_summary(frame)
    assert result["rows"] == 3
    assert result["feature_count"] == 2
    assert result["overall_cell_missingness"] == pytest.approx(0.5)
    assert result["features"][0]["feature"] == "Lactate"
