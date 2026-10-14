import numpy as np

from scripts.evaluate_calibration_robustness import _apply_recalibrator, _fit_recalibrator


def test_recalibrator_fits_validation_only_and_returns_bounded_probabilities():
    y = np.array([0, 0, 1, 0, 1, 1, 0, 1])
    p = np.array([0.1, 0.2, 0.7, 0.3, 0.8, 0.6, 0.4, 0.9])
    model = _fit_recalibrator(y, p)
    assert model is not None
    adjusted = _apply_recalibrator(model, p)
    assert adjusted.shape == p.shape
    assert np.isfinite(adjusted).all()
    assert ((adjusted > 0) & (adjusted < 1)).all()


def test_recalibrator_skips_single_class_validation_data():
    assert _fit_recalibrator(np.zeros(4, dtype=int), np.array([0.1, 0.2, 0.3, 0.4])) is None
