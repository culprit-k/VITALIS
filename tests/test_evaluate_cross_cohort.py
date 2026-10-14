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
