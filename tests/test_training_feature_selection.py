import pandas as pd
import pytest

from scripts.train_baseline import observed_training_features


def test_all_missing_features_are_excluded_using_training_fold_only():
    training = pd.DataFrame({
        "HR": [70.0, 80.0, None],
        "EtCO2": [None, None, None],
        "Temp": [36.5, None, 37.0],
    })
    observed, dropped = observed_training_features(training)
    assert observed == ["HR", "Temp"]
    assert dropped == ["EtCO2"]


def test_feature_selection_fails_if_every_predictor_is_missing():
    training = pd.DataFrame({"HR": [None, None], "Temp": [None, None]})
    with pytest.raises(ValueError, match="No predictors"):
        observed_training_features(training)
