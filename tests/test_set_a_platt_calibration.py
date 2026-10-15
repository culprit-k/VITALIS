import numpy as np
import pytest

from scripts.evaluate_set_a_platt_calibration import platt_apply, platt_fit


def test_platt_calibration_returns_finite_monotone_probabilities():
    p = np.asarray([0.05, 0.1, 0.15, 0.25, 0.4, 0.55, 0.7, 0.85, 0.9, 0.95])
    y = np.asarray([0, 0, 0, 0, 0, 0, 1, 1, 1, 1], dtype=np.int8)
    calibrator = platt_fit(p, y, seed=42)
    calibrated = platt_apply(calibrator, p)
    assert np.all(np.isfinite(calibrated))
    assert np.all((calibrated >= 0) & (calibrated <= 1))
    assert np.all(np.diff(calibrated) >= 0)
    assert np.all(np.isfinite(calibrator.coef_))
    assert np.all(np.isfinite(calibrator.intercept_))


def test_platt_calibration_fails_closed_without_both_classes():
    with pytest.raises(ValueError, match="both target classes"):
        platt_fit(np.asarray([0.1, 0.2, 0.3]), np.asarray([0, 0, 0]), seed=1)
