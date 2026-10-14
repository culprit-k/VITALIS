import pandas as pd
import pytest

from vitalis.features import add_patient_baseline_features


def test_personal_baseline_uses_only_prior_rows():
    frame = pd.DataFrame({"patient": ["a"] * 5, "hr": [70.0, 72.0, 71.0, 90.0, 91.0]})
    result = add_patient_baseline_features(frame, patient_col="patient", value_cols=["hr"])
    assert result["hr_personal_baseline"].iloc[:3].isna().all()
    assert result["hr_personal_baseline"].iloc[3] == pytest.approx(71.0)
    assert result["hr_personal_deviation"].iloc[3] == pytest.approx(19.0)


def test_personal_baseline_does_not_cross_patient_boundaries():
    frame = pd.DataFrame({
        "patient": ["a", "a", "a", "b", "b", "b", "b"],
        "hr": [70.0, 71.0, 72.0, 150.0, 151.0, 149.0, 160.0],
    })
    result = add_patient_baseline_features(frame, patient_col="patient", value_cols=["hr"])
    assert result["hr_personal_baseline"].iloc[3:6].isna().all()
    assert result["hr_personal_baseline"].iloc[6] == pytest.approx(150.0)


def test_personal_z_is_missing_when_prior_variability_is_zero():
    frame = pd.DataFrame({"patient": ["a"] * 5, "hr": [70.0, 70.0, 70.0, 70.0, 90.0]})
    result = add_patient_baseline_features(frame, patient_col="patient", value_cols=["hr"])
    assert result["hr_personal_z"].isna().all()


def test_personal_baseline_rejects_invalid_parameters_and_missing_columns():
    frame = pd.DataFrame({"patient": ["a"], "hr": [70.0]})
    with pytest.raises(ValueError, match="min_history"):
        add_patient_baseline_features(frame, patient_col="patient", value_cols=["hr"], min_history=0)
    with pytest.raises(ValueError, match="Missing required columns"):
        add_patient_baseline_features(frame, patient_col="patient", value_cols=["temp"])
