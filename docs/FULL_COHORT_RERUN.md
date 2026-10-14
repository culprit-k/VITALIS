# Full-cohort rerun — 14 October 2026

This aggregate report records a fresh local evaluation on all of training_setA. Raw patient records and patient-level predictions were not exported. The final rerun includes 200 whole-patient bootstrap resamples per model for AUROC, AUPRC, and Brier score.

## Cohort and protocol

- 20,336 patient files, 790,215 hourly rows, 17,136 positive hourly challenge labels.
- Patient-level split, seed 42: 13,014 train, 3,254 validation, 4,068 test patients.
- Fixed threshold 0.5; LogisticRegression with median imputation, missingness indicators, standard scaling, class weighting, and max_iter=500.
- Static model: 40 features. Temporal model: 109 features, adding one-row lag, one-row difference, and trailing six-row mean for physiological measurements.
- The optimized local harness was algorithm-aligned with repository commit `fc5008f8009fea68a6197b5b3fb66d866210f4c7`, but was not launched through the repository CLI or GitHub Actions. A direct CLI reproduction remains required.

## Held-out test metrics

| Metric | Static baseline | Temporal features |
|---|---:|---:|
| AUROC | 0.7623 (95% patient-bootstrap interval 0.7435–0.7774) | 0.7873 (0.7694–0.8062) |
| Average precision (AUPRC) | 0.0777 (0.0665–0.0956) | 0.0842 (0.0720–0.1029) |
| Brier score (lower is better) | 0.1903 (0.1826–0.1975) | 0.1814 (0.1729–0.1893) |
| Sensitivity at 0.5 | 0.6341 | 0.6845 |
| Specificity at 0.5 | 0.7564 | 0.7538 |
| PPV at 0.5 | 0.0540 | 0.0574 |
| NPV at 0.5 | 0.9895 | 0.9909 |

At this fixed threshold, the temporal variant has higher point estimates for AUROC, AUPRC, sensitivity, and NPV, with a slightly lower specificity. Positive predictive value is approximately 5.7%, so most positive hourly alerts at this threshold are not positive challenge-label rows. This is not a clinical false-alarm rate.

A paired patient-cluster bootstrap using the same 200 resampled test-patient sets for both models produced the following temporal-minus-static differences (95% percentile intervals): AUROC +0.0249 (0.0155 to 0.0331), AUPRC +0.00652 (0.00257 to 0.01446), and Brier score −0.00889 (−0.01068 to −0.00704). These intervals are conditional on this single held-out split and the challenge dataset; they do not establish external validity or clinical benefit.

## Warnings and limitations

- `EtCO2` and its temporal derivatives were entirely missing and were skipped by imputation.
- Patient-cluster intervals are percentile intervals based on 200 resamples; only the AUROC, AUPRC, and Brier score intervals are included.
- The threshold was fixed at 0.5, not clinically optimized.
- Metrics are hourly-row metrics; they are not event-level clinical metrics.
- The challenge's `SepsisLabel` was used as supplied and was not shifted again.
- This is retrospective evaluation on one dataset, not external or prospective validation. Do not claim clinical readiness, novelty, or patentability from these results.

See [structured JSON results](../results/full_cohort_rerun_2026-10-14.json) and the [local experiment history](LOCAL_EXPERIMENTS.md).


## Independent dataset integrity audit (2026-10-14)

The full `training_setA` partition was independently re-read file-by-file using the new aggregate integrity checker. The checker completed in approximately 31 seconds in the local environment and reported:

- 20,336 patient files and 790,215 hourly rows.
- 17,136 positive challenge-label rows across 1,790 files.
- Zero invalid/missing/non-binary target rows and zero empty files.
- Zero files with a mismatched column set; 41 columns in the union.
- 22,102,799 missing cells across the input tables.
- Patient files ranged from 8 to 336 rows.

Aggregate-only artifact: [training_setA integrity audit](../results/phase3_training_setA_integrity_audit.json). The checker does not export file names, patient rows, or predictions. This validates basic input integrity only; it does not resolve the separate direct canonical-CLI/source-identity limitation or establish model performance.
