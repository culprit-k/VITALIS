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


def patient_cluster_bootstrap_utility_uncertainty(
    labels: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
    patient_ids: Sequence[object] | np.ndarray,
    patient_time_indices: Sequence[int] | np.ndarray,
    *,
    thresholds: Sequence[float],
    missed_window_costs: Sequence[float],
    alert_cost: float = 1.0,
    refractory_hours: int = 6,
    n_bootstrap: int = 200,
    seed: int = 42,
) -> dict[str, object]:
    """Estimate patient-cluster uncertainty and candidate-selection stability.

    Whole patient blocks are resampled. For each predeclared threshold and cost
    scenario, percentile intervals cover row sensitivity/PPV, alerts per
    at-risk patient-day, forecast-window coverage, and weighted cost/day.
    Selection frequency is descriptive stability, not a probability that a
    threshold is clinically optimal.
    """

    y, p, groups, times = map(np.asarray, (labels, probabilities, patient_ids, patient_time_indices))
    # Reuse the validated deterministic calculation for common input checks.
    base = evaluate_utility_operating_points(
        y, p, groups, times, thresholds=thresholds,
        missed_window_costs=missed_window_costs, alert_cost=alert_cost,
        refractory_hours=refractory_hours,
    )
    if isinstance(n_bootstrap, bool) or not isinstance(n_bootstrap, int) or n_bootstrap < 20:
        raise ValueError("n_bootstrap must be an integer >= 20")
    boundaries = np.r_[0, np.flatnonzero(groups[1:] != groups[:-1]) + 1, len(groups)]
    if len(boundaries) < 4:
        raise ValueError("at least three patient blocks are required")
    # Reappearing patient IDs would invalidate the cluster unit and time-window logic.
    block_ids = [groups[start] for start in boundaries[:-1]]
    if len(set(x.item() if hasattr(x, "item") else x for x in block_ids)) != len(block_ids):
        raise ValueError("patient rows must be contiguous and each patient must appear once")
    n_patients = len(boundaries) - 1
    rng = np.random.default_rng(seed)
    sampled = rng.integers(0, n_patients, size=(n_bootstrap, n_patients))
    threshold_values = np.asarray(base["thresholds"], dtype=np.float64)
    sorted_order = np.argsort(threshold_values, kind="stable")
    threshold_values_sorted = threshold_values[sorted_order]
    costs = np.asarray(base["missed_window_cost_scenarios"], dtype=np.float64)

    # This helper computes all patient summaries in one pass over the aligned
    # cohort. Calling the public aggregate evaluator separately for every
    # patient would repeat setup work thousands of times on the full cohort.
    try:
        from vitalis.horizon import _patient_summaries as summarize_patients
    except ImportError:  # compatibility with the earlier reconstructed local runner
        from vitalis.horizon import _summaries as summarize_patients

    per_threshold = []
    for threshold in threshold_values:
        patient_tp, patient_fp, patient_fn = [], [], []
        patient_hours, patient_alerts, patient_windows, patient_covered = [], [], [], []
        summaries = summarize_patients(y, p, groups, times, threshold=float(threshold),
                                       refractory_hours=refractory_hours)
        for (start, end), summary in zip(zip(boundaries[:-1], boundaries[1:]), summaries):
            yp = y[start:end].astype(np.int8, copy=False)
            pp = p[start:end]
            pred = pp >= threshold
            patient_tp.append(np.sum(pred & (yp == 1)))
            patient_fp.append(np.sum(pred & (yp == 0)))
            patient_fn.append(np.sum(~pred & (yp == 1)))
            patient_hours.append(summary["hours"])
            patient_alerts.append(summary["alerts"])
            patient_windows.append(summary["windows"])
            patient_covered.append(summary["covered"])
        arrays = [np.asarray(v, dtype=np.float64) for v in (
            patient_tp, patient_fp, patient_fn, patient_hours, patient_alerts,
            patient_windows, patient_covered,
        )]
        boot = [values[sampled].sum(axis=1) for values in arrays]
        tp, fp, fn, hours, alerts, windows, covered = boot
        days = hours / 24.0
        metrics = {
            "row_sensitivity": np.divide(tp, tp + fn, out=np.full(n_bootstrap, np.nan), where=(tp + fn) > 0),
            "row_ppv": np.divide(tp, tp + fp, out=np.full(n_bootstrap, np.nan), where=(tp + fp) > 0),
            "alerts_per_at_risk_patient_day": np.divide(alerts, days, out=np.full(n_bootstrap, np.nan), where=days > 0),
            "future_positive_window_coverage": np.divide(covered, windows, out=np.full(n_bootstrap, np.nan), where=windows > 0),
        }
        for cost in costs:
            cost_day = np.divide(cost * (windows - covered) + alert_cost * alerts, days,
                                 out=np.full(n_bootstrap, np.nan), where=days > 0)
            metrics[f"weighted_cost_per_patient_day__miss_cost_{cost:g}"] = cost_day
        per_threshold.append(metrics)

    def interval(values):
        finite = values[np.isfinite(values)]
        return {
            "lower_95": float(np.percentile(finite, 2.5)) if len(finite) else None,
            "upper_95": float(np.percentile(finite, 97.5)) if len(finite) else None,
            "valid_replicates": int(len(finite)),
            "requested_replicates": n_bootstrap,
        }

    threshold_results = []
    for i, threshold in enumerate(threshold_values):
        threshold_results.append({
            "threshold": float(threshold),
            "intervals": {name: interval(values) for name, values in per_threshold[i].items()},
        })

    scenarios = []
    for cost in costs:
        key = f"weighted_cost_per_patient_day__miss_cost_{cost:g}"
        matrix = np.column_stack([per_threshold[i][key] for i in range(len(threshold_values))])
        matrix_sorted = matrix[:, sorted_order]
        valid_rows = np.isfinite(matrix_sorted).all(axis=1)
        chosen = np.argmin(np.where(np.isfinite(matrix_sorted), matrix_sorted, np.inf), axis=1)
        counts = np.bincount(chosen[valid_rows], minlength=len(threshold_values))
        denom = int(valid_rows.sum())
        scenarios.append({
            "missed_window_cost_relative_to_one_alert": float(cost),
            "selection_frequency_by_threshold": [
                {"threshold": float(threshold_values_sorted[j]),
                 "selected_replicates": int(counts[j]),
                 "selection_fraction": float(counts[j] / denom) if denom else None}
                for j in range(len(threshold_values_sorted))
            ],
            "valid_replicates": denom,
            "requested_replicates": n_bootstrap,
            "interpretation": "Resampling stability of the minimum-cost development candidate under this assumed cost ratio; not clinical optimality.",
        })
    return {
        "method": "patient-cluster percentile bootstrap of operating-point metrics and cost-ranking stability",
        "confidence_level": 0.95,
        "seed": seed,
        "unique_patients": n_patients,
        "requested_replicates": n_bootstrap,
        "threshold_results": threshold_results,
        "cost_scenario_selection_stability": scenarios,
        "set_b_used_for_threshold_selection": False,
        "limitations": [
            "Conditional retrospective uncertainty on the Set-A development partition.",
            "Selection frequency measures resampling stability under assumed costs, not a probability of clinical optimality.",
            "Cost ratios are illustrative unless independently elicited and justified.",
            "Challenge-label windows are not independently observed biological onset.",
            "A new independent cohort is required for final evaluation.",
        ],
    }
