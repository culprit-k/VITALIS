# Horizon calibration uncertainty analysis

**Run date:** 15 October 2026  
**Status:** completed across all nine predeclared seed × horizon combinations.  
**Scope:** patient-cluster uncertainty for Set B calibration metrics; retrospective Challenge-label-window prediction only.

## Protocol and data boundary

- Evaluated verified Set A (20,336 patients; 790,215 hourly rows) and Set B (20,000 patients; 761,995 hourly rows).
- Ran seeds 42, 123, 2026 across 1-, 3-, and 6-hour horizons; both static and temporal models. Each Set B model/horizon/seed estimate uses 200 patient-cluster bootstrap replicates (18 model-run combinations, 3,600 bootstrap replicates total).
- Whole patients, not hourly rows, are resampled. The bootstrap resamples per-patient sufficient statistics and calculates uncertainty for calibrated Brier score, Brier score minus a constant-prevalence reference, log loss, fixed-bin expected calibration error (ECE), mean predicted probability, and paired calibrated-minus-raw Brier difference.
- Calibration model is fitted only on the patient-disjoint Set A calibration partition. Set B is evaluation-only and did not influence fitting, calibration, feature selection, or threshold selection.
- Raw patient data, caches, patient identifiers, and row-level predictions remain local. Only aggregate statistics are reported.

## Results on Set B

Each point estimate is the mean ± sample SD across the three predeclared seeds. The “95% interval envelope” is the minimum lower and maximum upper endpoint across the three seed-specific patient-cluster bootstrap intervals. **It is not a pooled 95% confidence interval.**

| Horizon | Model | Calibrated Brier (mean ± SD) | Envelope of 95% CIs for Brier | Envelope for Brier − prevalence reference | Envelope for calibrated − raw Brier | Envelope for ECE |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Static | 0.00126855 ± 1.2e-05 | [0.00118716, 0.00137054] | [2.74683e-06, 5.02364e-05] | [-0.187872, -0.170811] | [0.000635109, 0.00133325] |
| 1 h | Temporal | 0.00126712 ± 1.2e-05 | [0.00118199, 0.00137516] | [-9.09856e-08, 4.68486e-05] | [-0.118331, -0.1038] | [0.00028663, 0.000719086] |
| 3 h | Static | 0.00386345 ± 4.8e-05 | [0.00360294, 0.00417711] | [-4.97146e-06, 0.000162168] | [-0.170945, -0.158691] | [0.00182328, 0.00297108] |
| 3 h | Temporal | 0.00383373 ± 1.7e-05 | [0.0035879, 0.00412082] | [-1.36512e-05, 6.55701e-05] | [-0.120664, -0.101935] | [0.000718875, 0.00161489] |
| 6 h | Static | 0.00809034 ± 0.00012 | [0.00753451, 0.00878207] | [-4.02653e-05, 0.000409899] | [-0.171776, -0.15271] | [0.00335067, 0.00577655] |
| 6 h | Temporal | 0.00803089 ± 7.9e-05 | [0.00749163, 0.00866965] | [-6.00674e-05, 0.000247561] | [-0.125397, -0.103347] | [0.00190322, 0.00345831] |

## Interpretation

- **Platt recalibration greatly improves Brier score relative to raw class-weighted scores.** For every model/horizon/seed combination, the patient-cluster interval for calibrated-minus-raw Brier is below zero. This is evidence of better probability scoring after recalibration on this retrospective cohort, not proof of clinical calibration.
- **The constant-prevalence baseline remains hard to beat.** The Brier-minus-prevalence-reference interval envelope is above zero for 1-hour static; it nearly touches or crosses zero for 1-hour temporal and crosses zero for both models at 3 and 6 hours. Thus the current analysis does not establish a robust Brier improvement over a prevalence-only forecast.
- ECE intervals describe only the chosen fixed bins and should not be interpreted as a complete calibration test. Mean predicted probability also remains above observed target prevalence in the underlying runs.
- These are conditional intervals for fixed fitted models on one benchmark cohort. Seeds are not independent cohorts, and the interval envelope is descriptive rather than pooled inference. A future comparison of static versus temporal models should use paired patient-level bootstrap differences on aligned Set B predictions, declared before looking at the result.

## What this means for VITALIS

The current model is **not ready for clinical alerting**. The next research gate should be a predeclared paired comparison of model variants on patient-level resamples, plus a leakage and target-definition audit; do not select a threshold from Set B. Before clinical translation, an independent cohort with an appropriate onset/event definition, clinical adjudication, workflow utility assessment, and prospective validation would be required.

## Limitations

- The Challenge `SepsisLabel` already incorporates a six-hour lead convention. Targets forecast entry into that label window, not independently observed biological onset.
- Set B is a separate Challenge training cohort, not prospective external clinical validation. The Set A holdout is a development diagnostic, not an independent external validation.
- Patient-cluster bootstrap uncertainty is conditional on the fixed model and observed cohort; it does not include training-data/model-fitting uncertainty.
- ECE depends on the fixed bin boundaries; low prevalence makes probability metrics sensitive to small absolute differences.
- Alerts outside future-positive windows are not verified clinical false alarms; no evidence of patient benefit or clinical safety is established.

**Research-only:** VITALIS is not a medical device or clinically validated decision-support system. Do not use these outputs to guide patient care.
