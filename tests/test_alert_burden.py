import numpy as np
import pandas as pd
import pytest

from scripts.train_baseline import calculate_alert_burden


def test_alert_burden_applies_refractory_and_counts_label_episodes():
    labels = pd.Series([0, 1, 1, 0, 0, 1, 1, 0])
    probabilities = np.array([0.7, 0.8, 0.9, 0.8, 0.1, 0.9, 0.8, 0.1])
    patients = pd.Series(["p1"] * len(labels))
    result = calculate_alert_burden(labels, probabilities, patients, threshold=0.5, refractory_hours=3)
    assert result["alerts_total"] == 3
    assert result["challenge_positive_label_episodes"] == 2
    assert result["challenge_positive_episodes_with_alert"] == 2
    assert result["alerts_outside_challenge_positive_windows"] == 1


def test_alert_burden_requires_positive_refractory_period():
    with pytest.raises(ValueError, match="at least 1"):
        calculate_alert_burden(pd.Series([0]), np.array([0.9]), pd.Series(["p1"]), refractory_hours=0)
