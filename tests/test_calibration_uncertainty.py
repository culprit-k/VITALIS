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


def test_paired_model_bootstrap_matches_sklearn_point_differences():
    from sklearn.metrics import average_precision_score, roc_auc_score

    groups = np.repeat(np.arange(10), 5)
    y = np.tile(np.array([0, 0, 1, 0, 1], dtype=np.int8), 10)
    p_static = np.tile(np.array([0.02, 0.08, 0.25, 0.04, 0.4]), 10)
    p_temporal = np.tile(np.array([0.01, 0.12, 0.3, 0.06, 0.55]), 10)
    out = MOD.patient_cluster_bootstrap_paired_model_metrics(
        y, p_static, p_temporal, groups, n_bootstrap=40, seed=23
    )
    expected = {
        "auroc": roc_auc_score(y, p_temporal) - roc_auc_score(y, p_static),
        "auprc": average_precision_score(y, p_temporal) - average_precision_score(y, p_static),
        "brier_score": brier_score_loss(y, p_temporal) - brier_score_loss(y, p_static),
        "log_loss": log_loss(y, p_temporal, labels=[0, 1]) - log_loss(y, p_static, labels=[0, 1]),
    }
    assert out["point_estimates"]["comparison_minus_reference"] == pytest.approx(expected)
    assert out["intervals_comparison_minus_reference"]["auroc"]["valid_replicates"] == 40
    assert "patient_ids" not in out and "predictions" not in out


def test_paired_model_bootstrap_rejects_patient_reappearance():
    with pytest.raises(ValueError, match="contiguous"):
        MOD.patient_cluster_bootstrap_paired_model_metrics(
            [0, 1, 0, 1], [.1, .8, .2, .7], [.2, .9, .3, .8], [1, 2, 1, 2], n_bootstrap=20
        )


def test_paired_model_bootstrap_intervals_match_explicit_patient_resampling():
    from sklearn.metrics import average_precision_score, roc_auc_score

    groups = np.repeat(np.arange(8), 4)
    y = np.tile(np.array([0, 0, 1, 0], dtype=np.int8), 8)
    p_static = np.tile(np.array([0.01, 0.08, 0.3, 0.04]), 8)
    p_temporal = np.tile(np.array([0.03, 0.12, 0.4, 0.02]), 8)
    reps, seed = 40, 19
    out = MOD.patient_cluster_bootstrap_paired_model_metrics(
        y, p_static, p_temporal, groups, n_bootstrap=reps, seed=seed
    )
    rng = np.random.default_rng(seed)
    differences = {name: [] for name in ("auroc", "auprc", "brier_score", "log_loss")}
    blocks = [np.flatnonzero(groups == g) for g in np.unique(groups)]
    for sample in rng.integers(0, len(blocks), size=(reps, len(blocks))):
        idx = np.concatenate([blocks[g] for g in sample])
        differences["auroc"].append(roc_auc_score(y[idx], p_temporal[idx]) - roc_auc_score(y[idx], p_static[idx]))
        differences["auprc"].append(average_precision_score(y[idx], p_temporal[idx]) - average_precision_score(y[idx], p_static[idx]))
        differences["brier_score"].append(brier_score_loss(y[idx], p_temporal[idx]) - brier_score_loss(y[idx], p_static[idx]))
        differences["log_loss"].append(log_loss(y[idx], p_temporal[idx], labels=[0, 1]) - log_loss(y[idx], p_static[idx], labels=[0, 1]))
    for name, values in differences.items():
        assert out["intervals_comparison_minus_reference"][name]["lower_95"] == pytest.approx(np.percentile(values, 2.5))
        assert out["intervals_comparison_minus_reference"][name]["upper_95"] == pytest.approx(np.percentile(values, 97.5))
