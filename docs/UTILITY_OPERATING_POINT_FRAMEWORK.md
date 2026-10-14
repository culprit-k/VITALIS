# Utility-based horizon operating-point framework

**Status:** utility function and focused tests added; full-cohort utility results are not yet generated.

## Purpose

The framework compares a predeclared threshold grid under explicit relative costs for missed forecast-positive windows and alert burden. It reports row-level sensitivity and positive predictive value (PPV), alerts per at-risk patient-day, forecast-positive-window coverage, missed windows, label-relative warning time, and alerts outside target-positive windows.

The scenario score is:

    weighted_cost = missed_window_cost × missed_forecast_positive_windows
                  + alert_cost × all_alerts
    weighted_cost_per_patient_day = weighted_cost / eligible_at_risk_patient_days

The alert cost is expressed in units of one alert. Missed-window cost is an analyst-specified multiple of that unit. The function accepts cost assumptions as inputs rather than asserting a medically justified default. Compare multiple plausible scenarios; do not treat one ratio as objective truth. All alerts count toward burden, including those inside positive windows. Alerts outside target-positive windows are not presumed to be clinical false alarms.

## Data partition and selection discipline

- Fit the model and any recalibration using patient-disjoint Set A training/calibration partitions only.
- Calculate development candidate rankings only on the untouched, patient-disjoint Set A operating-point partition.
- Rankings are conditional on the stated cost ratios, horizon, model, refractory interval, and threshold grid.
- Never choose or modify thresholds from Set B. Set B remains evaluation-only; a new independent cohort is needed for final evaluation after a policy is frozen.
- If costs or the threshold grid are revised after inspecting development results, document the revision and treat the comparison as exploratory.

## Implementation

Pure analysis function: \`src/vitalis/utility.py\` (\`evaluate_utility_operating_points\`). It validates aligned inputs, uses patient-level alert/window semantics from \`src/vitalis/horizon.py\`, and ranks candidates under each supplied cost ratio. Its lowest-cost threshold is explicitly labeled a development candidate, not a clinical threshold.

Focused tests: \`tests/test_utility.py\`.

## Remaining work before a full-cohort result

1. Integrate the function into the calibration evaluator for the untouched Set A holdout, using a predeclared threshold grid and explicit cost-sensitivity scenarios.
2. Run the integrated evaluator in the authorized local environment against the verified Set A cache; commit aggregate-only summaries, never patient-level predictions or score archives.
3. Obtain independent clinician/statistician review of plausible cost ratios and label-window semantics.
4. Freeze any development policy, then evaluate it once on a new independent cohort. Set B results already inspected must not be reused for threshold selection.
5. Prospective evaluation, governance review, and clinical validation remain separate gates.

## Interpretation limits

The target forecasts entry into the Challenge SepsisLabel-positive window, whose construction includes a six-hour lead convention; it is not independently observed biological onset. An alert outside a forecast-positive window is not necessarily a clinical false alarm. This cost proxy does not encode treatment harms, alarm fatigue, staffing, delayed treatment, patient preferences, or competing outcomes. VITALIS remains research-only and must not guide patient care.
