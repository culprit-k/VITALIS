"""Leakage-conscious helpers for longitudinal physiological features."""

from __future__ import annotations

import pandas as pd


def add_temporal_features(
    frame: pd.DataFrame,
    *,
    patient_col: str,
    value_cols: list[str],
    window: int = 6,
) -> pd.DataFrame:
    """Add prior-value, one-step change, and trailing-mean features per patient.

    Rows must already be sorted chronologically within patient. Trailing means
    include the current row and past rows only. This function does not impute
    missing values and never carries values between patients.
    """
    if window < 1:
        raise ValueError("window must be at least 1")
    required = {patient_col, *value_cols}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = frame.copy()
    grouped = result.groupby(patient_col, sort=False, dropna=False)
    for column in value_cols:
        result[f"{column}_lag1"] = grouped[column].shift(1)
        result[f"{column}_delta1"] = result[column] - result[f"{column}_lag1"]
        result[f"{column}_rollmean{window}"] = grouped[column].transform(
            lambda series: series.rolling(window=window, min_periods=1).mean()
        )
    return result
