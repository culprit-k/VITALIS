# VITALIS cross-cohort feature-coverage sensitivity analysis

Date: 14 October 2026

## Pre-specified protocol

- Eligibility rule: retain a feature only if at least 5% of rows in the Set-A training partition for that seed contain a finite value. Applied independently to static and temporal feature sets, using Set A training rows only.
- Patient-disjoint Set-A split: 60% training / 20% validation / 20% unused. Platt recalibration uses only Set-A validation predictions. Set B is evaluation-only.
- Baseline values below come from the previous byte-identical-source run; filtered values come from this local sensitivity wrapper using the same checked-in split/calibration/metric helpers. Feature counts in the labels are input columns before imputation: the baseline imputer drops the all-missing EtCO2 column for static input and four EtCO2-related columns for temporal input; every feature retained by the 5% rule has observed training values.
- The 5% cutoff is exploratory, not clinically justified. It was not selected by Set-B performance.

## Cohorts

| Cohort | Patients | Hourly rows | Positive hourly labels |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 |
| Set B | 20,000 | 761,995 | 10,780 |

## Static model

| Policy / stream | AUROC mean ± SD | AUPRC mean ± SD | Brier mean ± SD | Log loss mean ± SD | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| baseline (raw; input columns 40/40/40) | 0.675017 ± 0.005824 | 0.045495 ± 0.001793 | 0.165892 ± 0.005734 | 0.522278 ± 0.012058 | 0.367623 ± 0.008949 |
| baseline (recalibrated; input columns 40/40/40) | 0.675017 ± 0.005824 | 0.045495 ± 0.001793 | 0.014071 ± 0.000187 | 0.071721 ± 0.000150 | 0.018862 ± 0.000645 |
| coverage_filtered (raw; feature counts 29/30/30) | 0.668677 ± 0.007490 | 0.043604 ± 0.001773 | 0.164736 ± 0.005059 | 0.519098 ± 0.010465 | 0.366273 ± 0.007983 |
| coverage_filtered (recalibrated; feature counts 29/30/30) | 0.668677 ± 0.007490 | 0.043604 ± 0.001773 | 0.014081 ± 0.000182 | 0.071806 ± 0.000234 | 0.018695 ± 0.000554 |

Feature counts after training-only eligibility rule:
- Seed 42: 29 of 40 features retained.
- Seed 123: 30 of 40 features retained.
- Seed 2026: 30 of 40 features retained.

## Temporal model

| Policy / stream | AUROC mean ± SD | AUPRC mean ± SD | Brier mean ± SD | Log loss mean ± SD | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| baseline (raw; input columns 109/109/109) | 0.731911 ± 0.006419 | 0.058095 ± 0.001481 | 0.097222 ± 0.002160 | 0.352586 ± 0.005239 | 0.263268 ± 0.004877 |
| baseline (recalibrated; input columns 109/109/109) | 0.731911 ± 0.006419 | 0.058095 ± 0.001481 | 0.013830 ± 0.000032 | 0.068996 ± 0.000280 | 0.013361 ± 0.000821 |
| coverage_filtered (raw; feature counts 78/79/79) | 0.733466 ± 0.007082 | 0.058294 ± 0.001622 | 0.096545 ± 0.002642 | 0.350706 ± 0.006447 | 0.262080 ± 0.005814 |
| coverage_filtered (recalibrated; feature counts 78/79/79) | 0.733466 ± 0.007082 | 0.058294 ± 0.001622 | 0.013838 ± 0.000036 | 0.068844 ± 0.000211 | 0.013313 ± 0.000795 |

Feature counts after training-only eligibility rule:
- Seed 42: 78 of 109 features retained.
- Seed 123: 79 of 109 features retained.
- Seed 2026: 79 of 109 features retained.

## Interpretation boundary

Compared with baseline, the 5% rule slightly reduced static ranking metrics (mean AUROC 0.6750 to 0.6687; mean AUPRC 0.0455 to 0.0436) and left temporal ranking metrics similar/slightly higher (mean AUROC 0.7319 to 0.7335; mean AUPRC 0.0581 to 0.0583). Recalibrated probability metrics were also similar. These small descriptive differences do not establish that the threshold is better, and the rule was not selected using Set B.

This is a sensitivity check, not a model-selection exercise. Performance differences describe this benchmark protocol only; they do not establish clinical calibration, lead time, event-level sensitivity, real-world alarm burden, or clinical utility. The 5% rule should not be adopted merely because a metric is better on Set B. Any future eligibility rule needs training-only or external domain justification and must be frozen before final evaluation.

No patient-level data, identifiers, group vectors, caches, or row-level predictions are included in the report or aggregate JSON.
