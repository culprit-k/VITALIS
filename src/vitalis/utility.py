"""Cost-sensitive research operating-point analysis for horizon forecasts."""
from __future__ import annotations
from math import isfinite
from typing import Sequence
import numpy as np
from vitalis.horizon import evaluate_horizon_alerts


def evaluate_utility_operating_points(labels: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray, patient_ids: Sequence[object] | np.ndarray,
    patient_time_indices: Sequence[int] | np.ndarray, *, thresholds: Sequence[float],
    missed_window_costs: Sequence[float], alert_cost: float = 1.0,
    refractory_hours: int = 6) -> dict[str, object]:
    """Rank candidate thresholds under explicit, analyst-specified cost scenarios.

    Costs are a research proxy, not clinical valuations. Use only on a
    patient-disjoint development partition, never to tune on final evaluation.
    """
    y, p, groups, times = map(np.asarray, (labels, probabilities, patient_ids, patient_time_indices))
    if any(x.ndim != 1 for x in (y, p, groups, times)):
        raise ValueError("all inputs must be one-dimensional")
    if len(y) == 0 or not (len(y) == len(p) == len(groups) == len(times)):
        raise ValueError("inputs must be nonempty and equally sized")
    if not np.isin(y, [0, 1]).all():
        raise ValueError("labels must be binary")
    if not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must be finite and in [0, 1]")
    if not isfinite(alert_cost) or alert_cost <= 0:
        raise ValueError("alert_cost must be finite and positive")
    if isinstance(refractory_hours, bool) or not isinstance(refractory_hours, int) or refractory_hours < 1:
        raise ValueError("refractory_hours must be a positive integer")
    ts, costs = [float(v) for v in thresholds], [float(v) for v in missed_window_costs]
    if not ts or any(not isfinite(v) or not 0 <= v <= 1 for v in ts) or len(set(ts)) != len(ts):
        raise ValueError("thresholds must be unique values in [0, 1]")
    if not costs or any(not isfinite(v) or v <= 0 for v in costs) or len(set(costs)) != len(costs):
        raise ValueError("missed_window_costs must be unique finite positive values")

    points = []
    for threshold in ts:
        pred = p >= threshold
        tp, fp, fn = int(np.sum(pred & (y == 1))), int(np.sum(pred & (y == 0))), int(np.sum(~pred & (y == 1)))
        alert = evaluate_horizon_alerts(y, p, groups, times, threshold=threshold,
                                        refractory_hours=refractory_hours)
        windows = int(alert["future_positive_windows"])
        covered = int(alert["covered_future_positive_windows"])
        days = float(alert["eligible_patient_days"])
        points.append({
            "threshold": threshold,
            "row_sensitivity": tp / (tp + fn) if tp + fn else None,
            "row_ppv": tp / (tp + fp) if tp + fp else None,
            "alerts_total": int(alert["alerts_total"]),
            "alerts_per_at_risk_patient_day": alert["alerts_per_at_risk_patient_day"],
            "alerts_outside_future_positive_windows": int(alert["alerts_outside_future_positive_windows"]),
            "future_positive_windows": windows, "covered_future_positive_windows": covered,
            "missed_future_positive_windows": windows - covered,
            "future_positive_window_coverage": alert["future_positive_window_coverage"],
            "eligible_at_risk_patient_days": days,
            "warning_lead_hours_to_challenge_label_entry": alert["warning_lead_hours_to_challenge_label_entry"],
        })
    scenarios = []
    for miss_cost in costs:
        ranked = []
        for point in points:
            miss_total = miss_cost * point["missed_future_positive_windows"]
            alert_total = alert_cost * point["alerts_total"]
            total = miss_total + alert_total
            days = point["eligible_at_risk_patient_days"]
            ranked.append({
                "threshold": point["threshold"],
                "missed_window_cost_relative_to_one_alert": miss_cost, "alert_cost": alert_cost,
                "missed_window_cost_total": miss_total, "alert_cost_total": alert_total,
                "total_weighted_cost": total,
                "weighted_cost_per_at_risk_patient_day": total / days if days else None,
                "missed_future_positive_windows": point["missed_future_positive_windows"],
                "alerts_total": point["alerts_total"], "sensitivity": point["row_sensitivity"],
                "ppv": point["row_ppv"],
                "alerts_per_at_risk_patient_day": point["alerts_per_at_risk_patient_day"],
                "future_positive_window_coverage": point["future_positive_window_coverage"],
            })
        ranked.sort(key=lambda x: (x["weighted_cost_per_at_risk_patient_day"], x["threshold"]))
        scenarios.append({
            "missed_window_cost_relative_to_one_alert": miss_cost, "alert_cost": alert_cost,
            "ranking_by_weighted_cost_per_at_risk_patient_day": ranked,
            "lowest_cost_development_candidate_threshold": ranked[0]["threshold"],
            "selection_warning": "Development-only candidate under an assumed cost ratio; not a clinical threshold. Costs need independent justification.",
        })
    return {
        "method": "explicit weighted cost sensitivity analysis over a predeclared threshold grid",
        "cost_definition": "missed_window_cost * missed_future_positive_windows + alert_cost * all alerts",
        "alert_cost_unit": "one alert", "refractory_hours": refractory_hours,
        "thresholds": ts, "missed_window_cost_scenarios": costs, "operating_points": points,
        "cost_scenarios": scenarios, "set_b_used_for_threshold_selection": False,
        "limitations": [
            "Retrospective Challenge-label utility proxy, not clinical utility.",
            "Challenge-label windows are not independently observed biological onset.",
            "Alerts outside target-positive windows are not verified clinical false alarms.",
            "Cost ratios require independent stakeholder/clinical justification.",
            "The lowest-cost threshold is only a development candidate and needs independent evaluation.",
        ],
    }
