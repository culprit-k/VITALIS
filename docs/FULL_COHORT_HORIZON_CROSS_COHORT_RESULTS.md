# Full-cohort future-label forecasting: Set A → Set B results

**Run date:** 2026-10-14  
**Status:** completed; aggregate-only output retained locally and available as a downloadable artifact from the active conversation.  
**Purpose:** retrospective research evaluation, not a clinical model validation.

## Execution and integrity

- Set A: 20,336 patients, 790,215 hourly rows, 17,136 positive Challenge labels.
- Set B: 20,000 patients, 761,995 hourly rows, 10,780 positive Challenge labels.
- Both caches passed count, group, row, and schema checks. Each cache has 109 features.
- Evaluated 1-, 3-, and 6-hour future-Challenge-label targets with seeds 42, 123, and 2026; static and temporal logistic-regression models for each combination (18 fitted models).
- For each horizon, eligible Set A rows were split by patient into approximately 60% training and 40% unused holdout. The holdout was not used for tuning.
- Set B remained evaluation-only. The fixed threshold was 0.5; refractory interval was six hours. Patient-cluster warning-metric intervals used 200 bootstrap replicates per fitted model.
- Run elapsed time: 384.8 seconds.
- GitHub Actions passed on the performance-optimization commit: [run #513](https://github.com/culprit-k/VITALIS/actions/runs/38616619520), 120 tests passed.
- The aggregate output contains cohort-level and metric summaries only; no patient identifiers, raw records, or individual predictions were exported.

## Row-level metrics

Values are mean ± sample standard deviation across the three predeclared seeds. The across-seed SD is descriptive, not a confidence interval.

| Horizon | Model | AUROC | AUPRC | Brier score | Sensitivity at 0.5 | PPV at 0.5 |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Static | 0.6634 ± 0.0022 | 0.00379 ± 0.00022 | 0.19370 ± 0.00585 | 0.5285 | 0.00248 |
| 1 h | Temporal | 0.6569 ± 0.0110 | 0.00317 ± 0.00015 | 0.13196 ± 0.00883 | 0.4008 | 0.00319 |
| 3 h | Static | 0.6813 ± 0.0043 | 0.01358 ± 0.00017 | 0.18060 ± 0.00546 | 0.5213 | 0.00842 |
| 3 h | Temporal | 0.6800 ± 0.0145 | 0.01264 ± 0.00048 | 0.13134 ± 0.00347 | 0.4151 | 0.01077 |
| 6 h | Static | 0.6868 ± 0.0050 | 0.02859 ± 0.00034 | 0.17455 ± 0.00621 | 0.5147 | 0.01903 |
| 6 h | Temporal | 0.6864 ± 0.0138 | 0.02643 ± 0.00102 | 0.14219 ± 0.00516 | 0.4457 | 0.02237 |

Set B future-positive target prevalence was approximately 0.125% at 1 hour, 0.384% at 3 hours, and 0.806% at 6 hours. AUPRC must be interpreted against these low prevalences.

## Patient-level warning behavior

Mean across the three seeds. These are label-relative warning metrics, not verified clinical event detection or false-alarm rates.

| Horizon | Model | Alerts / at-risk patient-day | Alerts outside future-positive windows / patient-day | Future-positive-window coverage | Mean warning time to challenge-label entry |
|---:|---|---:|---:|---:|---:|
| 1 h | Static | 1.792 | 1.789 | 12.0% | 1.00 h |
| 1 h | Temporal | 1.462 | 1.458 | 11.7% | 1.00 h |
| 3 h | Static | 1.507 | 1.496 | 32.9% | 1.93 h |
| 3 h | Temporal | 1.276 | 1.267 | 29.3% | 1.95 h |
| 6 h | Static | 1.399 | 1.379 | 60.2% | 3.42 h |
| 6 h | Temporal | 1.257 | 1.237 | 56.8% | 3.42 h |

The range of lower-to-upper bounds across the three seed-specific 95% patient-cluster bootstrap intervals was:

| Horizon | Model | Alerts / patient-day interval-bound envelope | Window-coverage interval-bound envelope |
|---:|---|---:|---:|
| 1 h | Static | 1.609–1.925 | 9.8%–14.7% |
| 1 h | Temporal | 1.312–1.548 | 8.9%–15.1% |
| 3 h | Static | 1.457–1.578 | 29.1%–37.1% |
| 3 h | Temporal | 1.173–1.373 | 24.8%–33.6% |
| 6 h | Static | 1.344–1.484 | 55.1%–64.4% |
| 6 h | Temporal | 1.129–1.381 | 52.1%–61.9% |

These envelopes are not pooled confidence intervals; they show the span of bounds from three separate seed-specific intervals.

## Interpretation

1. **Temporal features did not improve ranking consistently.** Across the three seeds, mean AUROC and AUPRC were slightly higher for the static model at all three horizons. Differences are small for AUROC, and the three seeds are not independent cohorts.
2. **Temporal models produced fewer alerts but also lower window coverage.** At the fixed 0.5 threshold, the temporal models generated approximately 1.26–1.46 alerts per at-risk patient-day and covered fewer future-positive windows than the static models.
3. **Positive predictive values were very low.** PPV at the reference threshold ranged from about 0.25% to 1.90% for static models and 0.32% to 2.24% for temporal models. This alert operating point is not clinically acceptable on the evidence here.
4. **Do not interpret Brier scores as clinical calibration.** Models use class-weighted logistic regression, and no calibration procedure was fitted in this experiment. Despite lower Brier scores for temporal models, all Brier scores are far above the score of a constant predictor set to the very low target prevalence. Probability calibration remains poor and requires a separate training-only calibration protocol.
5. **The target is label-relative.** The Challenge label already uses a six-hour lead convention. An H-hour target forecasts entry into the Challenge-positive label window in the next H rows; it does not predict independently observed biological onset within H hours.
6. **No clinical claim follows.** This is retrospective Set A → Set B evaluation on the two Challenge training cohorts, not prospective validation, decision-utility analysis, or evidence of patient benefit.

## Recommended next steps

- Keep the static and temporal models as baselines; do not promote either as a clinical alert model.
- Audit probability calibration against a prevalence-only reference and use a calibration set drawn only from Set A training patients; freeze the procedure before any Set B evaluation.
- Predefine a clinically meaningful operating-point analysis (sensitivity, PPV, alerts per patient-day, and patient-level event metrics) before any further Set B run. Do not select a threshold on Set B and then report those same results as unbiased evaluation.
- Add patient-level bootstrap intervals for row-level discrimination/calibration comparisons and independent statistical review.
- Preserve PR #1 as draft/unmerged pending source-provenance, security, reproducibility, and independent review gates.

**Research-only:** VITALIS is not a medical device or a clinically validated decision-support system. Do not use these outputs to guide patient care.
