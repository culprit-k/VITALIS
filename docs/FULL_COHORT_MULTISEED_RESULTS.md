# Full-cohort multi-seed comparison (14 October 2026)

## Scope

Exploratory comparison of static and temporal logistic-regression models on all of PhysioNet/CinC Challenge 2019 training_setA. The dataset contains 20,336 patient files, 790,215 hourly rows, and 17,136 positive hourly challenge-label rows.

This is a three-split-seed aggregation from local optimized/cached-feature harnesses, **not** a byte-verified run of the checked-in full-cohort CLI. Seed 42 comes from the existing full-cohort rerun; seeds 123 and 2026 were executed with the cached feature-matrix evaluator. The runs use patient-disjoint two-stage GroupShuffleSplit partitions and the same stated model family and feature definitions.

## Mean metrics across split seeds

Mean ± sample SD across seeds 42, 123, and 2026; SD is not a confidence interval.

| Metric | Static | Temporal |
|---|---:|---:|
| AUROC | 0.7628 ± 0.0013 | 0.7884 ± 0.0019 |
| Average precision (AUPRC) | 0.0846 ± 0.0085 | 0.0886 ± 0.0059 |
| Brier score | 0.1894 ± 0.0038 | 0.1816 ± 0.0044 |
| Sensitivity at fixed 0.5 threshold | 0.6433 ± 0.0127 | 0.6772 ± 0.0137 |
| Specificity at fixed 0.5 threshold | 0.7560 ± 0.0069 | 0.7524 ± 0.0084 |
| PPV at fixed 0.5 threshold | 0.0560 ± 0.0019 | 0.0579 ± 0.0010 |

## Per-seed results

| Seed | Test rows | Positive label rows | Static AUROC / AUPRC / Brier | Temporal AUROC / AUPRC / Brier |
|---:|---:|---:|---:|---:|
| 42 | 159,102 | 3,411 | 0.7623 / 0.0777 / 0.1903 | 0.7873 / 0.0842 / 0.1814 |
| 123 | 160,217 | 3,557 | 0.7643 / 0.0941 / 0.1928 | 0.7906 / 0.0952 / 0.1862 |
| 2026 | 155,703 | 3,470 | 0.7619 / 0.0820 / 0.1853 | 0.7874 / 0.0863 / 0.1773 |

## Interpretation

Temporal features had a higher mean AUROC by 0.0256 and a higher mean AUPRC by 0.0040; mean Brier score was lower by 0.0078. This supports continuing to investigate temporal features, but does not prove clinical utility. AUPRC remains low, PPV at threshold 0.5 is about 5.8% on average for the temporal model, and the threshold was not clinically selected.

## Limitations and required next steps

- The reported metrics are hourly-row challenge-label metrics, not patient-level event sensitivity, lead time, or real-world clinical false-alarm rates.
- No external or prospective validation has been performed. Do not use for diagnosis, triage, or treatment.
- The threshold 0.5 is for a fixed research comparison, not a clinical operating point.
- Temporal features assume that rows in each patient file are chronological hourly observations.
- Some variables/derived features are entirely missing and are skipped by median imputation.
- The cached local harness has not been byte-verified against the checked-in full-cohort CLI. Strict source identity and a reproducible repository-native multi-seed command remain outstanding.
- No patient-level predictions or raw patient records were exported.
