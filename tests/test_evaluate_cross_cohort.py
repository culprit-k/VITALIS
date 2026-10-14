import importlib.util
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

MODULE = Path(__file__).parents[1] / "scripts" / "evaluate_cross_cohort.py"
SPEC = importlib.util.spec_from_file_location("evaluate_cross_cohort", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_metrics_matches_sklearn_and_reports_fixed_threshold_counts():
    y = np.array([0, 0, 1, 1], dtype=np.int8)
    p = np.array([0.1, 0.8, 0.4, 0.9], dtype=np.float64)

    result = MOD.metrics(y, p)

    assert result["rows"] == 4
    assert result["positive_label_rows"] == 2
    assert result["prevalence"] == 0.5
    assert result["threshold"] == 0.5
    assert result["auroc"] == roc_auc_score(y, p) == 0.75
    assert result["auprc"] == average_precision_score(y, p)
    assert np.isclose(result["brier_score"], brier_score_loss(y, p), atol=1e-15)
    assert np.isclose(result["brier_score"], 0.255, atol=1e-15)
    assert result["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}
    assert result["sensitivity"] == 0.5
    assert result["specificity"] == 0.5
    assert result["ppv"] == 0.5
    assert result["npv"] == 0.5
    assert not ({"predictions", "patient_ids", "scores"} & result.keys())


def test_metrics_treats_probability_equal_to_threshold_as_positive():
    y = np.array([0, 1], dtype=np.int8)
    p = np.array([0.5, 0.5], dtype=np.float64)

    result = MOD.metrics(y, p)

    assert result["confusion_matrix"] == {"tn": 0, "fp": 1, "fn": 0, "tp": 1}
    assert result["sensitivity"] == 1.0
    assert result["specificity"] == 0.0
    assert result["ppv"] == 0.5
    assert result["npv"] is None


def test_score_archive_directory_must_be_outside_repository(tmp_path):
    import pytest

    repository_root = tmp_path / "repo"
    repository_root.mkdir()
    with pytest.raises(ValueError, match="outside the repository"):
        MOD.validate_private_score_archive_dir(repository_root / "scores", repository_root)

    outside = MOD.validate_private_score_archive_dir(tmp_path / "private-scores", repository_root)
    assert outside == (tmp_path / "private-scores").resolve()


def test_local_score_archive_contains_only_expected_arrays(tmp_path):
    labels = np.asarray([0, 1, 0], dtype=np.int8)
    groups = np.asarray([10, 10, 20], dtype=np.int32)
    static = np.asarray([0.1, 0.8, 0.2])
    temporal = np.asarray([0.2, 0.9, 0.3])
    path = MOD.write_local_score_archive(tmp_path / "heldout.npz", labels, groups, static, temporal)

    with np.load(path, allow_pickle=False) as data:
        assert set(data.files) == {"y", "groups", "p_static", "p_temporal"}
        assert np.array_equal(data["y"], labels)
        assert np.array_equal(data["groups"], groups)
        assert np.array_equal(data["p_static"], static)
        assert np.array_equal(data["p_temporal"], temporal)


def test_local_score_archive_rejects_misaligned_vectors(tmp_path):
    import pytest

    with pytest.raises(ValueError, match="equal lengths"):
        MOD.write_local_score_archive(
            tmp_path / "heldout.npz", np.asarray([0, 1]), np.asarray([1]),
            np.asarray([0.1, 0.9]), np.asarray([0.2, 0.8]),
        )
