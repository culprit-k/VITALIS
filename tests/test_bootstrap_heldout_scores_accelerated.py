import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("numba")

ROOT = Path(__file__).parents[1]
FAST_PATH = ROOT / "scripts" / "bootstrap_heldout_scores_accelerated.py"
BASE_PATH = ROOT / "scripts" / "bootstrap_heldout_scores.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FAST = load_module("bootstrap_heldout_scores_accelerated", FAST_PATH)
BASE = load_module("bootstrap_heldout_scores_baseline", BASE_PATH)


def test_accelerated_weighted_metrics_match_checked_in_runner_with_ties():
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=np.int8)
    p = np.array([0.1, 0.5, 0.5, 0.5, 0.8, 0.8, 0.1, 0.9])
    groups = np.array([10, 10, 20, 20, 30, 30, 40, 40])
    _, row_group = np.unique(groups, return_inverse=True)
    multiplicity = np.array([2, 1, 3, 2], dtype=np.uint16)

    prepared = BASE.prepare_score_metrics(y, p)
    row_weights = multiplicity[row_group].astype(np.float64)[None, :]
    expected = BASE.batch_weighted_rank_metrics(prepared, row_weights)[0]

    order_asc = np.argsort(p, kind="mergesort")
    order_desc = np.argsort(-p, kind="mergesort")
    actual = FAST.weighted_metrics(y, p, order_asc, order_desc, multiplicity, row_group)

    assert np.allclose(actual, expected, rtol=0, atol=1e-14)


def test_accelerated_bootstrap_chunk_offsets_reproduce_contiguous_stream(tmp_path):
    scores = tmp_path / "scores.npz"
    labels = np.tile(np.array([0, 1, 0, 1], dtype=np.int8), 10)
    groups = np.repeat(np.arange(10), 4)
    static = np.linspace(0.05, 0.8, len(labels))
    temporal = np.clip(static + np.tile([0.02, 0.03, -0.01, 0.01], 10), 0, 1)
    np.savez_compressed(scores, y=labels, groups=groups, p_static=static, p_temporal=temporal)

    full_diff = tmp_path / "full.npz"
    first_diff = tmp_path / "first.npz"
    second_diff = tmp_path / "second.npz"
    FAST.run_bootstrap(scores, 40, 42, tmp_path / "full.json",
                       private_differences_output=full_diff)
    FAST.run_bootstrap(scores, 20, 42, tmp_path / "first.json", offset=0,
                       private_differences_output=first_diff)
    FAST.run_bootstrap(scores, 20, 42, tmp_path / "second.json", offset=20,
                       private_differences_output=second_diff)

    with np.load(full_diff, allow_pickle=False) as data:
        full = data["differences"]
    with np.load(first_diff, allow_pickle=False) as data:
        first = data["differences"]
    with np.load(second_diff, allow_pickle=False) as data:
        second = data["differences"]
    assert np.array_equal(np.concatenate([first, second]), full)


def test_accelerated_runner_rejects_private_artifacts_inside_repository(tmp_path):
    with pytest.raises(ValueError, match="outside the repository"):
        FAST.validate_external_path(ROOT / "local-score.npz", ROOT)
