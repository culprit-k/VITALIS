# Horizon calibration and operating-point results

**Run date:** 15 October 2026  
**Status:** all nine predeclared seed × horizon combinations completed on verified local official-cohort caches; aggregate-only results committed.  
**Scope:** retrospective prediction of future Challenge-label-window entry; not prediction of independently observed sepsis onset or clinical validation.

## Execution and leakage controls

- Set A: 20,336 patients, 790,215 hourly rows, 17,136 positive Challenge labels. Set B: 20,000 patients, 761,995 rows, 10,780 positive labels. Both caches passed the runner’s official count/schema checks.
- Seeds 42, 123, 2026 × horizons 1, 3, 6 hours; static and temporal logistic-regression baselines: 18 fitted models across the nine runs.
- Each run uses patient-disjoint Set A partitions: approximately 60% train, 20% Platt calibration, 20% untouched Set A holdout. The model and preprocessing are fit on train only; Platt calibration is fit on the calibration partition only.
- Set B is final evaluation only; no fitting, calibration, feature selection, or threshold selection on Set B. Thresholds 0.001, 0.005, 0.01, 0.05, 0.5 were predeclared descriptive points. Patient alert metrics are reported at calibrated thresholds 0.005 and 0.01.
- Run time summed across nine independent invocations: 217.7 seconds. Captured model-fit warnings: 0.
- Raw data, caches, row-level predictions, and per-patient scores remain local. The committed JSON contains aggregate metrics only.

## Set B probability calibration

Values are mean ± sample SD across the three predeclared seeds. Constant-prevalence Brier reference is shown for context; it is not a trained comparator. Calibration is assessed with Brier score, log loss, mean predicted probability, and fixed-bin expected calibration error (ECE). ECE depends on the chosen bins.

| Horizon | Model | Mean predicted probability (calibrated) | Brier raw | Brier calibrated | Constant-prevalence Brier | ECE calibrated | AUROC calibrated | AUPRC calibrated |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 h | Static | 0.00221372 ± 0.00025 | 0.179526 ± 0.0055 | 0.00126855 ± 1.2e-05 | 0.00125328 | 0.000958865 ± 0.00025 | 0.670788 ± 0.0074 | 0.00390015 ± 0.00018 |
| 1 h | Temporal | 0.00175024 ± 0.00015 | 0.113132 ± 0.0044 | 0.00126712 ± 1.2e-05 | 0.00125328 | 0.000510198 ± 0.00012 | 0.686454 ± 0.0068 | 0.00380181 ± 0.00025 |
| 3 h | Static | 0.00605211 ± 0.00037 | 0.168106 ± 0.0028 | 0.00386345 ± 4.8e-05 | 0.00382187 | 0.00237687 ± 0.00026 | 0.688959 ± 0.0045 | 0.0138985 ± 0.00026 |
| 3 h | Temporal | 0.00485469 ± 0.00015 | 0.113624 ± 0.0066 | 0.00383373 ± 1.7e-05 | 0.00382187 | 0.00121073 ± 0.00016 | 0.700722 ± 0.0072 | 0.01365 ± 0.00043 |
| 6 h | Static | 0.0125357 ± 0.0006 | 0.168652 ± 0.0064 | 0.00809034 ± 0.00012 | 0.00799737 | 0.00452654 ± 0.00062 | 0.688186 ± 0.0025 | 0.0287225 ± 0.00011 |
| 6 h | Temporal | 0.0104461 ± 0.00046 | 0.123337 ± 0.0078 | 0.00803089 ± 7.9e-05 | 0.00799737 | 0.00254608 ± 0.00026 | 0.704816 ± 0.0088 | 0.0286642 ± 0.00078 |

### Interpretation

- Platt recalibration dramatically reduced the raw class-weighted probability scale and Brier score on both the untouched Set A holdout and Set B. This is expected when class weighting distorts the raw probability scale; it is not evidence that the model is clinically calibrated.
- On Set B, calibrated Brier scores remained slightly **worse** than the constant-prevalence reference at every horizon/model pair. Mean predicted probabilities were also above the observed prevalence. Thus, recalibration improved scores substantially but did not establish adequate calibration or added value over a prevalence-only probability.
- AUROC and AUPRC are unchanged by the monotonic Platt transform (up to ties/numerics); calibration should not be described as improving discrimination. Across seeds, temporal models had somewhat higher AUROC at 1/3/6 h in this run, while AUPRC differences were small and inconsistent. These seed-level differences are not independent cohort replications.

## Set B calibrated patient-level warning behavior

Mean across seeds. Alert rates are per at-risk patient-day. “Outside window” means outside a future-positive Challenge-label window and is not a verified clinical false-alarm rate.

| Horizon | Model | Threshold | Alerts / patient-day | Outside-window alerts / patient-day | Future-positive-window coverage | Mean lead to Challenge-label entry |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Static | 0.005 | 0.381 | 0.380 | 5.1% | 1.00 h |
| 1 h | Static | 0.01 | 0.177 | 0.177 | 2.2% | 1.00 h |
| 1 h | Temporal | 0.005 | 0.288 | 0.287 | 4.1% | 1.00 h |
| 1 h | Temporal | 0.01 | 0.131 | 0.131 | 2.7% | 1.00 h |
| 3 h | Static | 0.005 | 2.456 | 2.444 | 38.9% | 1.98 h |
| 3 h | Static | 0.01 | 0.470 | 0.463 | 20.2% | 1.99 h |
| 3 h | Temporal | 0.005 | 1.841 | 1.830 | 35.5% | 1.95 h |
| 3 h | Temporal | 0.01 | 0.312 | 0.307 | 15.7% | 1.89 h |
| 6 h | Static | 0.005 | 4.145 | 4.111 | 97.8% | 3.43 h |
| 6 h | Static | 0.01 | 2.642 | 2.615 | 78.1% | 3.47 h |
| 6 h | Temporal | 0.005 | 3.985 | 3.952 | 96.8% | 3.49 h |
| 6 h | Temporal | 0.01 | 1.984 | 1.959 | 72.9% | 3.46 h |

## Threshold-grid note

At lower thresholds the row-level sensitivity rises while specificity and PPV remain constrained by very low target prevalence. The threshold grid is descriptive only; no threshold was selected from Set B. Even thresholds producing more coverage can yield substantial alert burden. A clinically meaningful operating point cannot be inferred without event adjudication, an explicit utility/cost framework, and prospective workflow evidence.

## Target and study limitations

- The target is current `SepsisLabel=0` plus any positive Challenge label in the next H rows; current-positive rows and incomplete future tails are excluded.
- The Challenge `SepsisLabel` already incorporates a six-hour lead convention. These forecasts are relative to Challenge-label entry, not independently observed biological onset.
- Set B is a second Challenge training cohort, not prospective external clinical validation. The Set A holdout is a development diagnostic, not an independent external validation.
- Fixed-bin ECE depends on bin boundaries; the three seeds are not independent cohorts. This analysis does not include patient-cluster confidence intervals for calibration metrics.
- Alert burden and window coverage are not clinical event sensitivity or verified false-alarm rates. No evidence of patient benefit or clinical safety is established.

**Research-only:** VITALIS is not a medical device or clinically validated decision-support system. Do not use these outputs to guide patient care.
