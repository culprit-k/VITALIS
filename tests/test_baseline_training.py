import numpy as np
import pandas as pd

from scripts.train_baseline import calculate_metrics, load_patient_rows


def test_load_rows_keeps_patient_groups_and_labels(tmp_path):
    pd.DataFrame({"HR": [70, 80], "SepsisLabel": [0, 1]}).to_csv(tmp_path / "p1.psv", sep="|", index=False)
    pd.DataFrame({"HR": [90], "SepsisLabel": [0]}).to_csv(tmp_path / "p2.psv", sep="|", index=False)
    X, y, groups, features = load_patient_rows(tmp_path, temporal=False)
    assert list(X.columns) == features
    assert y.tolist() == [0, 1, 0]
    assert groups.nunique() == 2


def test_metrics_report_expected_binary_rates():
    y = pd.Series([0, 0, 1, 1])
    result = calculate_metrics(y, np.array([0.1, 0.7, 0.8, 0.9]), 0.5)
    assert result["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 0, "tp": 2}
    assert result["sensitivity"] == 1.0


def test_patient_cluster_bootstrap_intervals_are_deterministic_and_bounded():
    from scripts.train_baseline import patient_cluster_bootstrap_intervals

    y = pd.Series([0, 0, 1, 1, 0, 1, 0, 1])
    scores = np.array([0.1, 0.2, 0.7, 0.9, 0.3, 0.8, 0.4, 0.6])
    patients = pd.Series(["a", "a", "b", "b", "c", "c", "d", "d"])
    first = patient_cluster_bootstrap_intervals(y, scores, patients, n_bootstrap=30, seed=7)
    second = patient_cluster_bootstrap_intervals(y, scores, patients, n_bootstrap=30, seed=7)
    assert first == second
    assert first["method"] == "patient-cluster percentile bootstrap"
    for metric in ("auroc", "auprc", "brier_score", "sensitivity", "specificity", "ppv", "npv"):
        interval = first["intervals"][metric]
        assert interval["valid_replicates"] > 0
        assert 0 <= interval["lower_95"] <= interval["upper_95"] <= 1
