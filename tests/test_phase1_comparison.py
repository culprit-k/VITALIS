import numpy as np

from scripts.run_phase1_repeated_comparison import metric_set, paired_cluster_bootstrap


def test_metric_set_returns_row_counts_and_ranking_metrics():
    y = np.array([0, 0, 1, 1])
    p = np.array([0.1, 0.3, 0.7, 0.9])
    result = metric_set(y, p)
    assert result["rows"] == 4
    assert result["positive_rows"] == 2
    assert result["auroc"] == 1.0
    assert result["average_precision"] == 1.0


def test_paired_cluster_bootstrap_is_zero_for_identical_predictions():
    y = np.array([0, 1, 0, 1, 0, 1])
    p = np.array([0.1, 0.8, 0.2, 0.7, 0.3, 0.9])
    groups = np.array([1, 1, 2, 2, 3, 3])
    result = paired_cluster_bootstrap(y, p, p, groups, seed=7, replicates=30)
    assert result["auroc"]["lower_95"] == 0.0
    assert result["auroc"]["upper_95"] == 0.0
    assert result["average_precision"]["lower_95"] == 0.0
    assert result["average_precision"]["upper_95"] == 0.0
    assert result["brier_score"]["lower_95"] == 0.0
    assert result["brier_score"]["upper_95"] == 0.0
