import importlib.util
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import brier_score_loss, log_loss

MODULE = Path(__file__).parents[1] / "src" / "vitalis" / "calibration_uncertainty.py"
SPEC = importlib.util.spec_from_file_location("vitalis_calibration_uncertainty", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def fixture_data():
    groups = np.repeat(np.arange(12), 4)
    y = np.tile(np.array([0, 0, 1, 0], dtype=np.int8), 12)
    p = np.tile(np.array([0.01, 0.08, 0.2, 0.03]), 12)
    q = np.tile(np.array([0.03, 0.12, 0.35, 0.07]), 12)
    return y, p, q, groups


def test_cluster_bootstrap_is_reproducible_and_aggregate_only():
    y, p, q, groups = fixture_data()
    a = MOD.patient_cluster_bootstrap_calibration_metrics(y, p, groups, comparison_probabilities=q, n_bootstrap=40, seed=7)
    b = MOD.patient_cluster_bootstrap_calibration_metrics(y, p, groups, comparison_probabilities=q, n_bootstrap=40, seed=7)
    assert a == b
    assert a["patients"] == 12
    assert a["rows"] == len(y)
    assert a["intervals"]["brier_score"]["valid_replicates"] == 40
    assert "patient_ids" not in a and "predictions" not in a
    assert "brier_difference_vs_comparison" in a["intervals"]


def test_point_estimates_match_sklearn_brier_and_log_loss():
    y, p, _, groups = fixture_data()
    out = MOD.patient_cluster_bootstrap_calibration_metrics(y, p, groups, n_bootstrap=20)
    assert out["point_estimates"]["brier_score"] == pytest.approx(brier_score_loss(y, p))
    assert out["point_estimates"]["log_loss"] == pytest.approx(log_loss(y, p, labels=[0, 1]))
    prevalence = y.mean()
    assert out["point_estimates"]["brier_minus_constant_prevalence_reference"] == pytest.approx(brier_score_loss(y, p) - prevalence * (1-prevalence))


def test_rejects_patient_reappearance_and_bad_vectors():
    with pytest.raises(ValueError, match="contiguous"):
        MOD.patient_cluster_bootstrap_calibration_metrics([0, 1, 0], [.1, .8, .2], [1, 2, 1], n_bootstrap=20)
    with pytest.raises(ValueError, match="finite"):
        MOD.patient_cluster_bootstrap_calibration_metrics([0, 1], [.1, np.nan], [1, 2], n_bootstrap=20)
    with pytest.raises(ValueError, match="at least 20"):
        MOD.patient_cluster_bootstrap_calibration_metrics([0, 1], [.1, .8], [1, 2], n_bootstrap=19)


def test_rejects_invalid_comparison_stream():
    with pytest.raises(ValueError, match="comparison_probabilities"):
        MOD.patient_cluster_bootstrap_calibration_metrics([0, 1], [.1, .8], [1, 2], comparison_probabilities=[.1], n_bootstrap=20)
