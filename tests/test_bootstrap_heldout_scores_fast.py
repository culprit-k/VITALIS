import importlib.util
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

MODULE = Path(__file__).parents[1] / "scripts" / "bootstrap_heldout_scores_fast.py"
SPEC = importlib.util.spec_from_file_location("bootstrap_heldout_scores_fast", MODULE)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_weighted_metrics_match_sklearn_with_tied_scores():
    y = np.array([0, 1, 0, 1, 1, 0, 0, 1], dtype=np.int8)
    p = np.array([0.1, 0.5, 0.1, 0.5, 0.9, 0.5, 0.1, 0.9])
    row_group = np.array([0, 0, 1, 1, 2, 2, 3, 3], dtype=np.int32)
    multiplicity = np.array([2, 0, 3, 1], dtype=np.uint16)
    weights = multiplicity[row_group].astype(float)
    order_asc = np.argsort(p, kind="mergesort")
    order_desc = np.argsort(-p, kind="mergesort")

    got = np.asarray(MOD.weighted_metrics(y, p, order_asc, order_desc, multiplicity, row_group))
    expected = np.array([
        roc_auc_score(y, p, sample_weight=weights),
        average_precision_score(y, p, sample_weight=weights),
        brier_score_loss(y, p, sample_weight=weights),
    ])
    np.testing.assert_allclose(got, expected, rtol=0, atol=1e-12)


def test_bootstrap_is_deterministic_and_aggregate_only():
    y = np.tile(np.array([0, 0, 1, 0], dtype=np.int8), 12)
    groups = np.repeat(np.arange(12), 4)
    p_static = np.tile(np.array([0.1, 0.2, 0.3, 0.4]), 12)
    p_temporal = np.tile(np.array([0.05, 0.2, 0.5, 0.6]), 12)

    first = MOD.run_bootstrap(y, p_static, p_temporal, groups, replicates=20, model_seed=42, batch_size=4)
    second = MOD.run_bootstrap(y, p_static, p_temporal, groups, replicates=20, model_seed=42, batch_size=4)

    assert first["replicates_valid"] == 20
    assert first["test_patients"] == 12
    assert first["positive_hourly_labels"] == 12
    assert first["temporal_minus_static"] == second["temporal_minus_static"]
    assert not ({"predictions", "patient_ids", "scores", "groups"} & first.keys())


def test_archive_path_must_be_outside_repository(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    with pytest.raises(ValueError, match="outside the repository"):
        MOD.validate_archive_path(repository / "scores.npz", repository)
    outside = MOD.validate_archive_path(tmp_path / "private" / "scores.npz", repository)
    assert outside == (tmp_path / "private" / "scores.npz").resolve()


@pytest.mark.parametrize(
    "y,ps,pt,groups,match",
    [
        ([0, 2], [0.1, 0.2], [0.2, 0.3], [1, 2], "binary"),
        ([0, 1], [0.1, float("nan")], [0.2, 0.3], [1, 2], "finite"),
        ([0, 1], [0.1], [0.2, 0.3], [1, 2], "aligned"),
        ([0, 1], [0.1, 0.2], [0.2, 0.3], [1, 1], "two patient groups"),
    ],
)
def test_bootstrap_rejects_invalid_inputs(y, ps, pt, groups, match):
    with pytest.raises(ValueError, match=match):
        MOD.run_bootstrap(y, ps, pt, groups, replicates=20, model_seed=42)
