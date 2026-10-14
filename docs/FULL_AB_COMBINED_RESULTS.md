# Combined-cohort experiment using training sets A and B

Date: 14 October 2026

## Why this experiment exists

Earlier full-cohort results used training_setA alone. This additional run includes **both** official Challenge 2019 training cohorts in one patient-level pool, then separates patients into train, validation, and test partitions. It answers a different question from the separate cross-cohort experiment documented in [FULL_COHORT_CROSS_COHORT_RESULTS.md](FULL_COHORT_CROSS_COHORT_RESULTS.md).

- **training_setA:** 20,336 patients, 790,215 hourly rows, 17,136 positive hourly challenge-label rows.
- **training_setB:** 20,000 patients, 761,995 hourly rows, 10,780 positive hourly challenge-label rows.
- **Combined:** 40,336 patients, 1,552,210 hourly rows, 27,916 positive hourly challenge-label rows.

## Evaluation protocol

Three patient-disjoint split seeds (42, 123, 2026) were used. For each split, 25,814 patients were assigned to training, 6,454 to validation, and 8,068 to test. The training partition had approximately 993,000–996,000 hourly rows; model fitting used a deterministic random subsample capped at 500,000 training rows. The test partition contained approximately 311,000 hourly rows per seed.

We compared a static logistic-regression baseline with a temporal-feature version, using median imputation, missingness indicators, standard scaling, and balanced class weights. The fixed threshold was 0.5 and was not clinically selected. Reported SDs are across the three split seeds, not confidence intervals.

## Mean results across seeds

| Metric | Static | Temporal |
|---|---:|---:|
| AUROC | 0.7590 ± 0.0058 | 0.7963 ± 0.0035 |
| Average precision (AUPRC) | 0.0762 ± 0.0038 | 0.0865 ± 0.0035 |
| Brier score (lower is better) | 0.1894 ± 0.0033 | 0.1754 ± 0.0038 |
| Sensitivity at threshold 0.5 | 0.6351 ± 0.0148 | 0.6837 ± 0.0134 |
| Specificity at threshold 0.5 | 0.7720 ± 0.0077 | 0.7730 ± 0.0058 |
| PPV at threshold 0.5 | 0.0486 ± 0.0027 | 0.0524 ± 0.0025 |
| NPV at threshold 0.5 | 0.9914 ± 0.0007 | 0.9925 ± 0.0006 |

The temporal model's mean AUROC was higher by 0.0373 and mean AUPRC higher by 0.0102; mean Brier score was lower by 0.0140. The direction of these differences was consistent across the three seeds. This is encouraging for further temporal-feature research, but is not evidence of clinical benefit. PPV remained approximately 5.2% at the arbitrary 0.5 threshold.

## How to interpret the two A/B experiments

1. **Combined A+B split:** both cohorts contribute to the train/validation/test pool, with patient-level separation. This measures internal held-out performance when the combined dataset is available.
2. **Train A, test B:** set A supplies training patients and the entire set B is held out for evaluation. This is a stricter cohort-shift check; it is described in [the cross-cohort report](FULL_COHORT_CROSS_COHORT_RESULTS.md).

These are complementary, not interchangeable, experiments. Neither is prospective real-world validation, and both use the benchmark's hourly challenge labels.

## Provenance and limitations

- The local cached evaluator was reconstructed from checked-in logic; byte-for-byte source identity for this run has not been verified.
- Training used at most 500,000 randomly subsampled hourly rows from training patients per seed, not every available training row.
- Rows are assumed to be chronological hourly observations within each patient file.
- The challenge `SepsisLabel` was used as supplied and was not shifted again.
- Hourly-row metrics are not patient-level event sensitivity, lead time, or a clinical false-alarm rate.
- No row-level predictions, patient identifiers, raw records, or local feature caches are stored in this report or the repository.
- VITALIS remains a research prototype. Do not use it for diagnosis, triage, or treatment.

Aggregate-only results: [JSON summary](../results/full_AB_combined_multiseed_2026-10-14.json).
