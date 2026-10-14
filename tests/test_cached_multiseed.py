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
