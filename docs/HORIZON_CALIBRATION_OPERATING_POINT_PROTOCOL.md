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

The model uses bounded fitting settings (LBFGS, maximum 100 iterations, tolerance 0.01). The completed nine-run execution captured zero model-fit warnings.

## Reproduce

```bash
python scripts/evaluate_horizon_calibration.py \
  --set-a-cache /path/outside/repo/cache_set_a \
  --set-b-cache /path/outside/repo/cache_set_b \
  --horizons 1 3 6 \
  --seeds 42 123 2026 \
  --predict-chunk-rows 50000 \
  --refractory-hours 6 \
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
- The Set A holdout is a development diagnostic, not an independent external validation cohort. Seed-to-seed standard deviations are descriptive and are not confidence intervals; calibration-metric patient-cluster intervals remain future work.
- The Challenge `SepsisLabel` already incorporates a six-hour lead convention. Targets forecast entry into the Challenge-positive label window, not independently observed biological sepsis onset.
- Alerts outside future-positive windows are not verified clinical false alarms. Neither these metrics nor calibration alone establish clinical utility, safety, or patient benefit.

**Research-only:** VITALIS is not a medical device or clinically validated decision-support system. Do not use its outputs to guide patient care.
