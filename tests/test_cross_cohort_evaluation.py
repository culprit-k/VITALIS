import numpy as np

from scripts.evaluate_cross_cohort import metrics


def test_cross_cohort_metrics_are_aggregate_only():
    y = np.asarray([0, 0, 0, 1, 1, 1], dtype=np.int8)
    p = np.asarray([0.05, 0.2, 0.4, 0.6, 0.8, 0.95])
    result = metrics(y, p)
    assert result["rows"] == 6
    assert result["positive_label_rows"] == 3
    assert result["prevalence"] == 0.5
    assert result["threshold"] == 0.5
    assert result["auroc"] == 1.0
    assert result["sensitivity"] == 1.0
    assert result["specificity"] == 1.0
    assert result["confusion_matrix"] == {"tn": 3, "fp": 0, "fn": 0, "tp": 3}
    assert "predictions" not in result
    assert "patient_ids" not in result


def test_cross_cohort_metrics_handle_no_positive_predictions():
    y = np.asarray([0, 0, 0, 1], dtype=np.int8)
    p = np.asarray([0.1, 0.2, 0.3, 0.4])
    result = metrics(y, p)
    assert result["sensitivity"] == 0.0
    assert result["ppv"] is None
    assert result["npv"] == 0.75
