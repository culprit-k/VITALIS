import numpy as np

from scripts.evaluate_cached_multiseed import metrics


def test_metrics_are_aggregate_and_use_fixed_threshold():
    y_true = np.asarray([0, 0, 0, 1, 1, 1], dtype=np.int8)
    probability = np.asarray([0.05, 0.2, 0.4, 0.6, 0.8, 0.95])
    result = metrics(y_true, probability)

    assert result["rows"] == 6
    assert result["positive_label_rows"] == 3
    assert result["threshold"] == 0.5
    assert result["auroc"] == 1.0
    assert result["sensitivity"] == 1.0
    assert result["specificity"] == 1.0
    assert result["confusion_matrix"] == {"tn": 3, "fp": 0, "fn": 0, "tp": 3}
    assert "predictions" not in result
    assert "patient_ids" not in result


def test_metrics_report_low_precision_when_positive_class_is_rare():
    y_true = np.asarray([0] * 9 + [1], dtype=np.int8)
    probability = np.asarray([0.1] * 9 + [0.9])
    result = metrics(y_true, probability)

    assert result["ppv"] == 1.0
    assert result["npv"] == 1.0
    assert result["positive_label_rows"] == 1



def test_paired_patient_cluster_bootstrap_is_deterministic_and_aggregate_only():
    from scripts.evaluate_cached_multiseed import paired_patient_cluster_bootstrap

    y = np.asarray([0, 1, 0, 0, 1, 0, 1, 0], dtype=np.int8)
    static = np.asarray([0.2, 0.6, 0.3, 0.4, 0.7, 0.1, 0.8, 0.2])
    temporal = np.asarray([0.1, 0.8, 0.2, 0.3, 0.9, 0.2, 0.7, 0.1])
    groups = np.asarray([1, 1, 2, 2, 3, 3, 4, 4])
    a = paired_patient_cluster_bootstrap(
        y, static, temporal, groups, n_bootstrap=40, seed=17
    )
    b = paired_patient_cluster_bootstrap(
        y, static, temporal, groups, n_bootstrap=40, seed=17
    )

    assert a == b
    assert a["replicates_valid"] >= 20
    assert set(a["temporal_minus_static"]) == {"auroc", "auprc", "brier_score"}
    assert "predictions" not in a
    assert "patient_ids" not in a
    assert len(a["temporal_minus_static"]["auroc"]["ci_95_percentile"]) == 2


def test_paired_patient_cluster_bootstrap_rejects_mismatched_inputs():
    import pytest
    from scripts.evaluate_cached_multiseed import paired_patient_cluster_bootstrap

    with pytest.raises(ValueError, match="equal lengths"):
        paired_patient_cluster_bootstrap(
            np.asarray([0, 1]), np.asarray([0.1]), np.asarray([0.2, 0.8]),
            np.asarray([1, 2]), n_bootstrap=40
        )



def test_optimized_weighted_metrics_match_sklearn_with_ties():
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
    from scripts.evaluate_cached_multiseed import _prepare_rank_metrics, _weighted_rank_metrics

    rng = np.random.default_rng(20261014)
    for n in (8, 100, 1000):
        for _ in range(20):
            y = rng.integers(0, 2, n)
            p = np.round(rng.random(n), 1)
            weights = rng.integers(0, 4, n).astype(float)
            if weights[y == 1].sum() == 0 or weights[y == 0].sum() == 0:
                continue
            actual = _weighted_rank_metrics(_prepare_rank_metrics(y, p), weights)
            expected = (
                roc_auc_score(y, p, sample_weight=weights),
                average_precision_score(y, p, sample_weight=weights),
                brier_score_loss(y, p, sample_weight=weights),
            )
            assert np.allclose(actual, expected, atol=1e-12)


def test_bootstrap_rejects_single_patient_cluster():
    import pytest
    from scripts.evaluate_cached_multiseed import paired_patient_cluster_bootstrap

    with pytest.raises(ValueError, match="at least two patient groups"):
        paired_patient_cluster_bootstrap(
            np.asarray([0, 1, 0, 1]), np.asarray([0.1, 0.8, 0.2, 0.7]),
            np.asarray([0.2, 0.9, 0.1, 0.8]), np.asarray([1, 1, 1, 1]),
            n_bootstrap=20
        )



def test_batched_weighted_metrics_match_sklearn_with_ties():
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
    from scripts.bootstrap_heldout_scores import batch_weighted_rank_metrics, prepare_score_metrics

    rng = np.random.default_rng(90210)
    for n in (8, 100, 1000):
        for _ in range(10):
            y = rng.integers(0, 2, n, dtype=np.int8)
            p = np.round(rng.random(n), 1)
            weights = rng.integers(0, 4, n).astype(float)
            if weights[y == 1].sum() == 0 or weights[y == 0].sum() == 0:
                continue
            actual = batch_weighted_rank_metrics(prepare_score_metrics(y, p), weights[None, :])[0]
            expected = (
                roc_auc_score(y, p, sample_weight=weights),
                average_precision_score(y, p, sample_weight=weights),
                brier_score_loss(y, p, sample_weight=weights),
            )
            assert np.allclose(actual, expected, atol=1e-12)


def test_batched_bootstrap_is_deterministic_and_aggregate_only():
    from scripts.bootstrap_heldout_scores import run_bootstrap

    y = np.asarray([0, 1, 0, 0, 1, 0, 1, 0], dtype=np.int8)
    static = np.asarray([0.2, 0.6, 0.3, 0.4, 0.7, 0.1, 0.8, 0.2])
    temporal = np.asarray([0.1, 0.8, 0.2, 0.3, 0.9, 0.2, 0.7, 0.1])
    groups = np.asarray([1, 1, 2, 2, 3, 3, 4, 4])
    result = run_bootstrap(y, static, temporal, groups, replicates=40, model_seed=17, batch_size=4)
    repeat = run_bootstrap(y, static, temporal, groups, replicates=40, model_seed=17, batch_size=4)
    assert result["temporal_minus_static"] == repeat["temporal_minus_static"]
    assert result["replicates_valid"] == 40
    assert "patient_ids" not in result
    assert "predictions" not in result
    assert "groups" not in result
