# Utility-based horizon operating-point framework

**Status (15 October 2026):** utility function, calibration-evaluator integration, CLI cost-scenario arguments, focused tests, and an exploratory nine-run aggregate analysis are complete. Results and provenance caveats are documented in [the results report](HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md) and [aggregate JSON](../results/horizon_utility_operating_point_aggregate_2026-10-15.json).

## Purpose

The framework compares a predeclared threshold grid under explicit relative costs for missed forecast-positive windows and alert burden. It reports row-level sensitivity and positive predictive value (PPV), alerts per at-risk patient-day, forecast-positive-window coverage, missed windows, label-relative warning time, and alerts outside target-positive windows.

The scenario score is:

    weighted_cost = missed_window_cost × missed_forecast_positive_windows
                  + alert_cost × all_alerts
    weighted_cost_per_patient_day = weighted_cost / eligible_at_risk_patient_days

The alert cost is expressed in units of one alert. Missed-window cost is an analyst-specified multiple of that unit. The function accepts cost assumptions as inputs rather than asserting a medically justified default. The CLI default sensitivity grid is missed-window cost 1, 10, 100, 500, and 1,000 relative units per alert-cost unit; these values are illustrative and intentionally span a broad range. Compare multiple plausible scenarios; do not treat one ratio as objective truth. All alerts count toward burden, including those inside positive windows. Alerts outside target-positive windows are not presumed to be clinical false alarms.

## Data partition and selection discipline

- Fit the model and any recalibration using patient-disjoint Set A training/calibration partitions only.
- Calculate development candidate rankings only on the untouched, patient-disjoint Set A operating-point partition.
- Rankings are conditional on the stated cost ratios, horizon, model, refractory interval, and threshold grid.
- Never choose or modify thresholds from Set B. Set B remains evaluation-only; a new independent cohort is needed for final evaluation after a policy is frozen.
- If costs or the threshold grid are revised after inspecting development results, document the revision and treat the comparison as exploratory.

## Implementation

Pure analysis function: `src/vitalis/utility.py` (`evaluate_utility_operating_points`). It validates aligned inputs, uses patient-level alert/window semantics from `src/vitalis/horizon.py`, and ranks candidates under each supplied cost ratio. Its lowest-cost threshold is explicitly labeled a development candidate, not a clinical threshold.

Focused tests: `tests/test_utility.py`.

## Remaining gates

1. Use the [independent utility-cost review checklist](UTILITY_COST_REVIEW_CHECKLIST.md) to obtain a qualified clinician/statistician review of plausible cost ratios, utility assumptions, and label-window semantics before interpreting any scenario ranking.
2. Treat Set-A candidate rankings as development-only. Freeze any policy only after the cost assumptions and selection rule are predeclared; evaluate it once on a new independent cohort. Set B results already inspected must not be reused for threshold selection.
3. When runtime/network constraints permit, rerun from a verified clean checkout and repeat the utility-focused analysis with a larger uncertainty-replicate count if uncertainty intervals are needed. The current local execution is explicitly not byte-identically verified and used 20 bootstrap replicates.
4. Prospective evaluation, governance review, and clinical validation remain separate gates.

## Interpretation limits

The target forecasts entry into the Challenge SepsisLabel-positive window, whose construction includes a six-hour lead convention; it is not independently observed biological onset. An alert outside a forecast-positive window is not necessarily a clinical false alarm. This cost proxy does not encode treatment harms, alarm fatigue, staffing, delayed treatment, patient preferences, or competing outcomes. VITALIS remains research-only and must not guide patient care.


## Patient-cluster uncertainty and selection stability

The evaluator also bootstraps whole patients from the untouched Set-A operating-point holdout. For each threshold it reports percentile intervals for row sensitivity, row PPV, alerts per at-risk patient-day, future-positive-window coverage, and weighted cost per at-risk patient-day under each cost scenario. For each cost ratio it reports how often each threshold is the minimum-cost candidate across bootstrap replicates.

These are conditional intervals and resampling-stability summaries for the current development partition. A high selection frequency means only that a threshold tends to minimize this particular proxy under the supplied costs and observed cohort structure; it is **not** the probability that a threshold is clinically optimal. The bootstrap does not account for uncertainty in the cost ratios, model development choices, site/domain shift, or the validity of the Challenge-label proxy. A new independent cohort and independent cost/endpoint review remain necessary.

The default is 200 patient-cluster replicates, configured with \`--utility-bootstrap-replicates\` (minimum 20). The aggregate-only report contains no patient-level resamples or predictions.
