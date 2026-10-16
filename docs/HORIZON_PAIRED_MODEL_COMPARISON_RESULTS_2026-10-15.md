# Paired static-versus-temporal horizon model comparison

**Run date:** 15 October 2026  
**Status:** all nine predeclared seed × horizon runs completed with paired patient-cluster bootstrap intervals.  
**Scope:** descriptive comparison of frozen Platt-calibrated predictions on Set B; not clinical validation.

## Protocol

- For each horizon (1, 3, 6 hours) and seed (42, 123, 2026), compared static and temporal Platt-calibrated probability streams on the same eligible Set B rows.
- Resampled whole patients 200 times per seed/horizon (1,800 paired bootstrap replicates total). The bootstrap reports temporal minus static differences in AUROC, AUPRC, Brier score, and log loss.
- Patient-cluster bootstrap intervals preserve repeated hourly observations within a patient. Score ties are grouped once to avoid re-sorting the full cohort on every replicate.
- Set B remained evaluation-only. No threshold was selected, and these results must not be used to tune model architecture or claim unbiased model selection. All raw data, caches, patient identifiers, and individual predictions remain local.
- Full calibration runner completed 9 runs in 319.0 seconds; zero model-fit warnings were captured.

## Results

Point differences are temporal minus static. Values are mean ± sample SD across three seeds. The bracketed 95% interval envelope is the minimum lower to maximum upper endpoint across three separate seed-specific patient-cluster intervals; **it is not a pooled confidence interval**.

| Horizon | AUROC difference | AUPRC difference | Brier difference | Log-loss difference |
|---:|---:|---:|---:|---:|
| 1 h | 0.0156659 ± 0.0059 [0.000546524, 0.0327357] | -9.83387e-05 ± 0.00011 [-0.000572522, 0.000230718] | -1.43294e-06 ± 2.4e-06 [-1.57151e-05, 1.54319e-05] | -0.000186174 ± 4.7e-05 [-0.000306219, -0.000118202] |
| 3 h | 0.0117639 ± 0.0091 [-0.00192196, 0.0309285] | -0.000248548 ± 0.00054 [-0.00111261, 0.00106874] | -2.97219e-05 ± 3.1e-05 [-0.000101044, 6.32893e-06] | -0.000424258 ± 7.1e-05 [-0.000651727, -0.000292487] |
| 6 h | 0.0166293 ± 0.0069 [0.00423847, 0.030675] | -5.83229e-05 ± 0.00086 [-0.00181054, 0.00163496] | -5.94498e-05 ± 4.2e-05 [-0.000153115, -6.67869e-06] | -0.000802942 ± 0.00014 [-0.00114629, -0.000531725] |

## Interpretation

- **AUROC:** temporal scores had a positive paired difference with seed-specific intervals consistently above zero at 1 and 6 hours. At 3 hours, intervals were mixed/overlapping zero.
- **AUPRC:** the interval envelopes crossed zero at all three horizons. The experiment does not establish a reliable AUPRC advantage for either model.
- **Brier score:** differences were inconclusive at 1 and 3 hours. At 6 hours, the temporal model had a lower Brier score in all seed-specific intervals.
- **Log loss:** temporal-minus-static intervals were below zero at all horizons, favoring the temporal probabilities on this retrospective scoring metric.
- These are comparisons of fixed predictions on one retrospective cohort. The three seeds are not independent cohorts, and the interval envelope is descriptive rather than pooled inference.
- AUROC/AUPRC ranking and probability losses answer different questions; do not collapse them into one claim that a model is “best.” Model choice would require a predeclared utility framework on development data and a new independent evaluation cohort.

## Next research gate

Define a utility-based operating-point protocol on a patient-disjoint development partition. It must state the relative costs of missed forecast windows and alert burden before threshold selection, and report sensitivity, PPV, alerts per at-risk patient-day, and forecast-window coverage together. Do not select a threshold using Set B; reserve a new independent cohort for final evaluation.

## Provenance note

The official-cohort analysis was executed in the available local reconstructed working copy because a clean Git checkout could not be verified in the runtime due to network/DNS limitations. The checked-in code-bearing PR head passed GitHub Actions (137 tests), but this full-cohort run is **not claimed as byte-identically verified exact-source reproduction**. Raw data, caches, and individual predictions stayed local.

## Limitations

- The target forecasts entry into the Challenge SepsisLabel-positive window, not independently observed biological onset; the Challenge label already incorporates a six-hour lead convention.
- Set B is a second Challenge training cohort, not prospective external clinical validation.
- Patient-cluster intervals are conditional on fitted models and observed cohort; they do not include model-fitting uncertainty.
- Alerts outside forecast-positive windows are not verified clinical false alarms. No clinical safety, utility, or patient benefit is established.

**Research-only:** VITALIS is not a medical device or clinically validated decision-support system. Do not use its outputs to guide patient care.
