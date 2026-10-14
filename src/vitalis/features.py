"""Leakage-conscious helpers for longitudinal physiological features."""

from __future__ import annotations

import numpy as np
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


def add_patient_baseline_features(
    frame: pd.DataFrame,
    *,
    patient_col: str,
    value_cols: list[str],
    min_history: int = 3,
    min_scale: float = 1e-3,
) -> pd.DataFrame:
    """Add causal personal-baseline deviation features for each patient.

    At row t, the baseline and robust scale use valid observations strictly
    before t. The baseline is the expanding median; scale is 1.4826 times the
    expanding median absolute deviation around that prior median. The current
    value is compared with that prior baseline. If prior history is too short,
    or scale is effectively zero, the normalized deviation is missing rather
    than fabricated. No values are carried between patients.

    The input must already be ordered chronologically within patient. This
    implementation is a research feature, not a clinical score.
    """
    if min_history < 1:
        raise ValueError("min_history must be at least 1")
    if min_scale <= 0:
        raise ValueError("min_scale must be positive")
    required = {patient_col, *value_cols}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    result = frame.copy()
    grouped = result.groupby(patient_col, sort=False, dropna=False)
    for column in value_cols:
        values = pd.to_numeric(result[column], errors="coerce")
        prior_median = grouped[column].transform(
            lambda series: pd.to_numeric(series, errors="coerce")
            .shift(1)
            .expanding(min_periods=min_history)
            .median()
        )
        # MAD must be calculated against the expanding median available at each
        # earlier time, not against a median fitted on the whole patient series.
        deviations = (values - prior_median).abs()
        prior_mad = deviations.groupby(result[patient_col], sort=False, dropna=False).transform(
            lambda series: series.shift(1).expanding(min_periods=min_history).median()
        )
        robust_scale = 1.4826 * prior_mad
        safe_scale = robust_scale.where(robust_scale >= min_scale)
        result[f"{column}_personal_baseline"] = prior_median
        result[f"{column}_personal_deviation"] = values - prior_median
        result[f"{column}_personal_z"] = (values - prior_median) / safe_scale
    return result
