import numpy as np
import pandas as pd
import pytest

from scripts.train_baseline import calculate_alert_burden, calculate_metrics


def test_calculate_metrics_returns_expected_confusion_matrix_and_rates():
    y = pd.Series([0, 0, 1, 1])
    p = np.array([0.1, 0.8, 0.4, 0.9])
    result = calculate_metrics(y, p, threshold=0.5)
    assert result["confusion_matrix"] == {"tn": 1, "fp": 1, "fn": 1, "tp": 1}
    assert result["sensitivity"] == pytest.approx(0.5)
    assert result["specificity"] == pytest.approx(0.5)
    assert result["ppv"] == pytest.approx(0.5)
    assert result["npv"] == pytest.approx(0.5)


def test_alert_burden_suppresses_repeat_alerts_and_counts_label_episodes():
    # Patient p1 has one 2-hour positive-label episode and an alarm during it.
    # The refractory interval suppresses the next alarm. p2 has no positive labels.
    y = pd.Series([0, 1, 1, 0, 0, 0, 0, 0])
    p = np.array([0.1, 0.9, 0.95, 0.1, 0.8, 0.9, 0.1, 0.1])
    patients = pd.Series(["p1", "p1", "p1", "p1", "p2", "p2", "p2", "p2"])
    result = calculate_alert_burden(
        y, p, patients, threshold=0.5, refractory_hours=3
    )
    assert result["alerts_total"] == 2
    assert result["alerts_outside_challenge_positive_windows"] == 1
    assert result["challenge_positive_label_episodes"] == 1
    assert result["challenge_positive_episodes_with_alert"] == 1
    assert result["challenge_positive_episode_coverage"] == pytest.approx(1.0)
    assert "not event-level" in result["interpretation_note"]


def test_alert_burden_rejects_invalid_refractory_period():
    with pytest.raises(ValueError, match="at least 1"):
        calculate_alert_burden(
            pd.Series([0]), np.array([0.2]), pd.Series(["p1"]), refractory_hours=0
        )
