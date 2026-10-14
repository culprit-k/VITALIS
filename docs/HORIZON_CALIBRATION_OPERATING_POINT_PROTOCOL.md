# Horizon calibration and operating-point protocol

**Status (15 October 2026):** the full nine-run official-cohort execution is complete. Aggregate-only results and interpretation are recorded in [Horizon calibration results](HORIZON_CALIBRATION_RESULTS_2026-10-15.md) and [the machine-readable summary](../results/horizon_calibration_summary_2026-10-15.json).

## Purpose

The earlier full-cohort horizon experiment used class-weighted logistic-regression scores directly. Because class weighting changes the fitted probability scale, its raw probabilities should not be interpreted as calibrated event probabilities. This separate, predeclared Set-A-only calibration protocol evaluates 1-, 3-, and 6-hour future-Challenge-label targets.

## Leakage-safe split and fit protocol

For every seed (42, 123, 2026) and horizon (1, 3, 6 hours):

1. Build the target within each patient's contiguous chronological rows. Current-positive rows and each patient's final H rows remain excluded.
2. Split eligible Set A patients into three disjoint partitions: approximately 60% model training, 20% calibration, and 20% untouched operating-point holdout.
3. Fit median imputation, missingness indicators, standard scaling, and a class-weighted logistic-regression model on the training partition only.
4. Predict the calibration partition and fit a one-dimensional Platt logistic recalibrator on those Set A calibration patients only.
5. Report raw and recalibrated discrimination, Brier score, log loss, mean predicted probability, fixed-bin calibration error, and a constant-prevalence Brier reference on both the untouched Set A holdout and Set B.
6. Report confusion-matrix metrics at the fixed probability grid `0.001, 0.005, 0.01, 0.05, 0.5`. These thresholds are descriptive reference points; the runner does not choose a threshold.
7. Report patient-level alert burden, forecast-positive-window coverage, and label-relative warning time for the recalibrated Set B scores at the predeclared 0.005 and 0.01 thresholds only. The six-hour refractory interval is a research setting, not a clinical alarm policy.
8. Export aggregate metrics only. Do not export raw rows, patient identifiers, or individual probabilities.

The model uses bounded fitting settings (LBFGS, maximum 100 iterations, tolerance 0.01). The completed nine-run execution captured zero model-fit warnings. The full-cohort run used a locally reconstructed working copy because a clean checkout was unavailable; it is not claimed as byte-identical source reproduction. The committed code and tests passed GitHub Actions. The runner also supports patient-cluster percentile-bootstrap intervals for calibrated Brier score, log loss, mean predicted probability, fixed-bin ECE, Brier difference from the constant-prevalence reference, and paired calibrated-minus-raw Brier difference. It resamples whole patient blocks and stores aggregate intervals only. Completed Set-B results are documented in [the uncertainty report](HORIZON_CALIBRATION_UNCERTAINTY_RESULTS_2026-10-15.md) and [aggregate JSON](../results/horizon_calibration_uncertainty_summary_2026-10-15.json).

## Reproduce

```bash
python scripts/evaluate_horizon_calibration.py \
  --set-a-cache /path/outside/repo/cache_set_a \
  --set-b-cache /path/outside/repo/cache_set_b \
  --horizons 1 3 6 \
  --seeds 42 123 2026 \
  --predict-chunk-rows 50000 \
  --refractory-hours 6 \
  --bootstrap-replicates 200 \
  --output /path/outside/repo/horizon_calibration_operating_points.json
```

The runner validates expected official cohort counts and feature schema and stops if they do not match. Keep local run output outside Git until reviewed for aggregate-only contents.

## Results checkpoint

- All nine seed × horizon combinations completed using the verified local caches; 18 static/temporal model fits, summed elapsed time 217.7 seconds.
- Platt recalibration substantially reduced Brier scores compared with the raw class-weighted probabilities.
- On Set B, calibrated Brier scores were still slightly worse than the constant-prevalence reference for every model/horizon pair, and mean predicted probabilities remained above observed prevalence. The probabilities should not be treated as clinically calibrated risk estimates.
- At the predeclared calibrated threshold of 0.005, 6-hour window coverage was high (approximately 97%–98%) but alert burden was also high (about 4 alerts per at-risk patient-day). Lower coverage at the 1-hour horizon illustrates that no single clinically acceptable operating point has been established.
- No threshold was selected from Set B. Full summary tables and limitations are in [the results report](HORIZON_CALIBRATION_RESULTS_2026-10-15.md).

## Interpretation limits

- Set B is used only for final evaluation. No Set B fitting, recalibration, feature selection, or threshold selection is permitted.
- Do not choose a threshold after inspecting Set B and then report that same Set B result as unbiased evaluation. The threshold grid is predeclared and all points are descriptive.
- Fixed-bin calibration error depends on the stated binning; it is not a complete calibration assessment. Compare Brier score and log loss with the constant-prevalence reference and inspect calibration-bin summaries.
- The Set A holdout is a development diagnostic, not an independent external validation cohort. Seed-to-seed standard deviations are descriptive and are not confidence intervals. The patient-cluster bootstrap intervals quantify conditional uncertainty in this retrospective Set B cohort; they are not prospective or clinical validation. The completed results show consistently lower Brier scores after Platt recalibration than before it, but many intervals for calibrated Brier minus the prevalence-reference score cross zero.
- The Challenge `SepsisLabel` already incorporates a six-hour lead convention. Targets forecast entry into the Challenge-positive label window, not independently observed biological sepsis onset.
- Alerts outside future-positive windows are not verified clinical false alarms. Neither these metrics nor calibration alone establish clinical utility, safety, or patient benefit.

**Research-only:** VITALIS is not a medical device or clinically validated decision-support system. Do not use its outputs to guide patient care.

## Paired static-versus-temporal comparison

The evaluator also compares the two frozen Platt-calibrated Set-B score streams on the exact same eligible target rows. For each horizon and seed, it reports temporal-minus-static differences in AUROC, AUPRC, Brier score, and log loss, with paired patient-cluster percentile intervals. Whole patients are resampled together, preserving within-patient dependence and alignment of the paired predictions. Score ties are grouped once so bootstrap calculations do not repeatedly sort the full cohort.

These intervals are conditional on the fitted models and this retrospective cohort. They are descriptive comparisons, not a new independent validation; the three seeds are not independent cohorts. Set B remains evaluation-only and cannot be used to choose thresholds or model settings. The comparison does not establish clinical utility or patient benefit.



## Utility-based operating-point cost sensitivity (15 October 2026)

The calibration evaluator now computes cost-sensitivity rankings only on the untouched, patient-disjoint Set-A operating-point holdout. Set B does not participate in the cost calculation or threshold ranking. The default CLI scenario grid is missed-window costs of `1, 10, 100, 500, 1000` relative to an alert cost of `1`; these values are **illustrative sensitivity scenarios, not clinically elicited costs**. Override them with `--missed-window-costs` and `--alert-cost` after documenting the rationale.

For each candidate threshold the output includes row-level sensitivity/PPV, alerts per at-risk patient-day, missed/covered future-positive windows, window coverage, and label-relative warning time. Scenario cost is `missed_window_cost × missed windows + alert_cost × all alerts`, reported both as total cost and per at-risk patient-day. A lowest-cost threshold is reported as a Set-A development candidate under that scenario, not as a clinical selection.

Example:

```bash
python scripts/evaluate_horizon_calibration.py \\
  --set-a-cache /path/outside/repo/cache_set_a \\
  --set-b-cache /path/outside/repo/cache_set_b \\
  --horizons 1 3 6 --seeds 42 123 2026 \\
  --missed-window-costs 1 10 100 500 1000 --alert-cost 1 \\
  --output /path/outside/repo/horizon_utility_sensitivity.json
```

The evaluator output must remain aggregate-only. The cost proxy omits treatment harms, alarm fatigue, staffing, delayed treatment, patient preferences, and competing outcomes. Cost ratios need independent clinical/statistical justification. Set A holdout rankings are development evidence only; after a policy is frozen, a **new independent cohort** is needed for final evaluation. Previously inspected Set B results must not be reused to select a threshold.



## Utility-based operating-point cost sensitivity (15 October 2026)

The calibration evaluator computes cost-sensitivity summaries on the **untouched, patient-disjoint Set-A operating-point holdout** using Platt-calibrated probabilities. The CLI's illustrative scenario grid assigns missed forecast-positive-window costs of 1, 10, 100, 500, and 1,000 units relative to an alert cost of 1 unit. Both inputs are configurable through `--missed-window-costs` and `--alert-cost`. These values are sensitivity-analysis assumptions, not clinician-elicited or clinically justified costs.

For each threshold, the aggregate-only output reports row sensitivity/PPV, total alerts, alerts per at-risk patient-day, forecast-positive-window coverage, missed windows, and label-relative warning time. Each scenario ranks candidate thresholds by weighted cost per at-risk patient-day. Any lowest-cost threshold is a **development candidate only**; no threshold is selected from Set B, which remains evaluation-only.

The completed exploratory nine-run analysis is documented in [the utility results report](HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md) and [aggregate-only JSON](../results/horizon_utility_operating_point_aggregate_2026-10-15.json). It used a reconstructed local working copy, not a byte-identically verified clean checkout; ancillary bootstrap summaries used 20 replicates and are preliminary.

The cost ratios need independent clinician/statistician review before they are treated as meaningful. The framework does not model treatment harms, alarm fatigue, staffing constraints, or verified clinical false alarms. A frozen policy needs evaluation on a new independent cohort; Set B has already been inspected and must not be reused for threshold selection.


## Utility-based operating-point cost sensitivity (15 October 2026)

The calibration evaluator now computes cost-sensitivity summaries on the untouched, patient-disjoint Set-A operating-point holdout only. It uses the existing predeclared threshold grid (0.001, 0.005, 0.01, 0.05, 0.5) and default illustrative missed-window cost ratios of 1, 5, 10, and 20 relative to one alert. Both the missed-window cost grid and alert cost can be passed as CLI arguments; they are assumptions for sensitivity analysis, not clinically elicited values.

For each threshold the evaluator reports row sensitivity/PPV, total alerts, alerts per at-risk patient-day, forecast-positive-window coverage, missed forecast-positive windows, and warning time relative to Challenge-label entry. The scenario score is missed-window cost × missed windows + alert cost × all alerts, normalized by eligible at-risk patient-days. It ranks candidate thresholds separately under each scenario and explicitly labels them development candidates, not clinical thresholds.

Set B is not used for the utility ranking. The Set-B result stream remains final retrospective evaluation only and has already been inspected, so it must not be reused for threshold selection. A genuinely new independent cohort is required for final evaluation after any development policy is frozen. The default cost ratios are illustrative pending independent clinical/statistical justification. The implementation and limitations are described in [the utility framework](UTILITY_OPERATING_POINT_FRAMEWORK.md).
