"""Future challenge-label targets and patient-level warning metrics.

This predicts entry into the Challenge 2019 SepsisLabel-positive window, not
independently observed sepsis onset. The label already uses a six-hour lead
convention, so these results must not be described as onset prediction.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HorizonTargets:
    row_indices: np.ndarray
    targets: np.ndarray
    patient_ids: np.ndarray
    patient_time_indices: np.ndarray
    horizon_hours: int


def build_future_challenge_targets(
    labels: Sequence[int] | pd.Series | np.ndarray,
    patient_ids: Sequence[object] | pd.Series | np.ndarray,
    horizon_hours: int,
) -> HorizonTargets:
    """Target=1 when any of the next H labels is positive, at current label 0.

    Input rows must be contiguous patient blocks, in chronological order, with
    one row per hour. Current-positive rows and each patient's last H rows are
    excluded. The full future window is therefore known for every target row.
    """
    if not isinstance(horizon_hours, int) or isinstance(horizon_hours, bool) or horizon_hours < 1:
        raise ValueError("horizon_hours must be a positive integer")
    y, patients = np.asarray(labels), np.asarray(patient_ids)
    if y.ndim != 1 or patients.ndim != 1 or len(y) != len(patients):
        raise ValueError("labels and patient_ids must be equally sized one-dimensional arrays")
    if len(y) == 0 or not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be nonempty and binary")
    if pd.isna(patients).any():
        raise ValueError("patient_ids cannot contain missing values")

    seen: set[object] = set()
    previous = object()
    for patient in patients:
        key = patient.item() if hasattr(patient, "item") else patient
        prev = previous.item() if hasattr(previous, "item") else previous
        if key != prev:
            if key in seen:
                raise ValueError("patient rows must be in contiguous chronological blocks")
            seen.add(key)
            previous = patient

    rows, targets, output_patients, times = [], [], [], []
    start = 0
    while start < len(y):
        end = start + 1
        while end < len(y) and patients[end] == patients[start]:
            end += 1
        block = y[start:end].astype(np.int8, copy=False)
        for t in range(max(0, len(block) - horizon_hours)):
            if block[t] == 1:
                continue
            rows.append(start + t)
            targets.append(int(np.any(block[t + 1:t + horizon_hours + 1] == 1)))
            output_patients.append(patients[start + t])
            times.append(t)
        start = end
    return HorizonTargets(
        np.asarray(rows, dtype=np.int64), np.asarray(targets, dtype=np.int8),
        np.asarray(output_patients), np.asarray(times, dtype=np.int64), horizon_hours,
    )


def _patient_summary(y, p, times, threshold, refractory_hours):
    alarms = []
    last_alarm = None
    for i, score in enumerate(p):
        t = int(times[i])
        if score >= threshold and (last_alarm is None or t - last_alarm >= refractory_hours):
            alarms.append(i)
            last_alarm = t

    windows = []
    i = 0
    while i < len(y):
        if y[i] == 0:
            i += 1
            continue
        start = end = i
        while end + 1 < len(y) and y[end + 1] == 1 and times[end + 1] == times[end] + 1:
            end += 1
        windows.append((start, end))
        i = end + 1

    covered = 0
    lead_hours = []
    alarms_in_windows = set()
    for start, end in windows:
        inside = [a for a in alarms if start <= a <= end]
        if inside:
            covered += 1
            entry_time = int(times[end]) + 1
            lead_hours.append(float(entry_time - min(int(times[a]) for a in inside)))
            alarms_in_windows.update(inside)
    return {
        "hours": len(y),
        "alerts": len(alarms),
        "outside": sum(a not in alarms_in_windows for a in alarms),
        "windows": len(windows),
        "covered": covered,
        "leads": lead_hours,
        "any_alert": bool(alarms),
    }


def _aggregate(summaries):
    hours = sum(s["hours"] for s in summaries)
    alerts = sum(s["alerts"] for s in summaries)
    outside = sum(s["outside"] for s in summaries)
    windows = sum(s["windows"] for s in summaries)
    covered = sum(s["covered"] for s in summaries)
    leads = [lead for s in summaries for lead in s["leads"]]
    patients_alerted = sum(s["any_alert"] for s in summaries)
    return {
        "patients": len(summaries),
        "eligible_hours": hours,
        "eligible_patient_days": hours / 24.0,
        "alerts_total": alerts,
        "alerts_per_at_risk_patient_day": alerts / (hours / 24.0) if hours else None,
        "alerts_outside_future_positive_windows": outside,
        "alerts_outside_future_positive_windows_per_at_risk_patient_day": outside / (hours / 24.0) if hours else None,
        "future_positive_windows": windows,
        "covered_future_positive_windows": covered,
        "future_positive_window_coverage": covered / windows if windows else None,
        "patients_with_at_least_one_alert": patients_alerted,
        "fraction_of_patients_with_at_least_one_alert": patients_alerted / len(summaries) if summaries else None,
        "warning_lead_hours_to_challenge_label_entry": {
            "n_covered_windows": len(leads),
            "mean": float(np.mean(leads)) if leads else None,
            "median": float(np.median(leads)) if leads else None,
            "min": float(np.min(leads)) if leads else None,
            "max": float(np.max(leads)) if leads else None,
        },
        "interpretation_note": (
            "Timing is relative to entry into the Challenge SepsisLabel-positive window, "
            "not clinical onset. Outside-window alerts are not verified clinical false alarms."
        ),
    }


def _patient_summaries(targets, probabilities, patient_ids, times, threshold, refractory_hours):
    y, p, patients, t = map(np.asarray, (targets, probabilities, patient_ids, times))
    if not (y.ndim == p.ndim == patients.ndim == t.ndim == 1):
        raise ValueError("all inputs must be one-dimensional")
    if len(y) == 0 or not (len(y) == len(p) == len(patients) == len(t)):
        raise ValueError("inputs must be nonempty and equally sized")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("targets must be binary")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be finite and in [0, 1]")
    if not isfinite(threshold) or not 0 <= threshold <= 1 or refractory_hours < 1:
        raise ValueError("threshold must be in [0, 1] and refractory_hours positive")
    summaries = []
    for patient in pd.unique(patients):
        mask = patients == patient
        pt = t[mask].astype(int)
        if len(pt) > 1 and np.any(np.diff(pt) <= 0):
            raise ValueError("time indices must be strictly increasing within each patient")
        summaries.append(_patient_summary(y[mask].astype(np.int8), p[mask], pt, threshold, refractory_hours))
    return summaries


def evaluate_horizon_alerts(
    targets, probabilities, patient_ids, patient_time_indices, *, threshold=0.5, refractory_hours=6
) -> dict[str, object]:
    """Summarize alert burden, forecast-window coverage and label-relative warning time."""
    return _aggregate(_patient_summaries(
        targets, probabilities, patient_ids, patient_time_indices, threshold, refractory_hours
    ))


def patient_cluster_bootstrap_horizon_alerts(
    targets, probabilities, patient_ids, patient_time_indices, *,
    threshold=0.5, refractory_hours=6, n_bootstrap=200, seed=42,
) -> dict[str, object]:
    """Patient-cluster percentile intervals for horizon-specific alert metrics."""
    if n_bootstrap < 20:
        raise ValueError("n_bootstrap must be at least 20")
    summaries = _patient_summaries(
        targets, probabilities, patient_ids, patient_time_indices, threshold, refractory_hours
    )
    if len(summaries) < 2:
        raise ValueError("at least two unique patients are required")
    getters = {
        "alerts_per_at_risk_patient_day": lambda s: sum(x["alerts"] for x in s) / (sum(x["hours"] for x in s) / 24) if sum(x["hours"] for x in s) else np.nan,
        "alerts_outside_future_positive_windows_per_at_risk_patient_day": lambda s: sum(x["outside"] for x in s) / (sum(x["hours"] for x in s) / 24) if sum(x["hours"] for x in s) else np.nan,
        "future_positive_window_coverage": lambda s: sum(x["covered"] for x in s) / sum(x["windows"] for x in s) if sum(x["windows"] for x in s) else np.nan,
        "fraction_of_patients_with_at_least_one_alert": lambda s: sum(x["any_alert"] for x in s) / len(s) if s else np.nan,
        "mean_warning_lead_hours_to_challenge_label_entry": lambda s: float(np.mean([lead for x in s for lead in x["leads"]])) if any(x["leads"] for x in s) else np.nan,
    }
    rng = np.random.default_rng(seed)
    values = {name: [] for name in getters}
    for _ in range(n_bootstrap):
        selected = rng.integers(0, len(summaries), size=len(summaries))
        sample = [summaries[int(i)] for i in selected]
        for name, getter in getters.items():
            value = float(getter(sample))
            if np.isfinite(value):
                values[name].append(value)
    intervals = {
        name: {
            "lower_95": float(np.percentile(v, 2.5)) if v else None,
            "upper_95": float(np.percentile(v, 97.5)) if v else None,
            "valid_replicates": len(v),
            "requested_replicates": n_bootstrap,
        }
        for name, v in values.items()
    }
    return {
        "method": "patient-cluster percentile bootstrap",
        "confidence_level": 0.95,
        "seed": seed,
        "unique_patients": len(summaries),
        "intervals": intervals,
        "interpretation_note": "Patients are resampled as clusters; intervals are not clinical validation.",
    }
