import pandas as pd
import pytest

from vitalis.features import add_temporal_features


def test_temporal_features_do_not_cross_patient_boundaries():
    frame = pd.DataFrame({"patient": ["a", "a", "b", "b"], "hr": [70, 80, 90, 100]})
    actual = add_temporal_features(frame, patient_col="patient", value_cols=["hr"], window=2)
    assert pd.isna(actual.loc[0, "hr_lag1"])
    assert actual.loc[1, "hr_lag1"] == 70
    assert pd.isna(actual.loc[2, "hr_lag1"])
    assert actual.loc[3, "hr_lag1"] == 90
    assert actual.loc[3, "hr_delta1"] == 10


def test_window_must_be_positive():
    frame = pd.DataFrame({"patient": ["a"], "hr": [70]})
    with pytest.raises(ValueError):
        add_temporal_features(frame, patient_col="patient", value_cols=["hr"], window=0)


def test_missing_columns_are_reported():
    frame = pd.DataFrame({"patient": ["a"]})
    with pytest.raises(ValueError, match="hr"):
        add_temporal_features(frame, patient_col="patient", value_cols=["hr"])
