# Full-cohort rerun — 14 October 2026

This aggregate report records a fresh local evaluation on all of training_setA. Raw patient records and patient-level predictions were not exported.

## Cohort and protocol

- 20,336 patient files, 790,215 hourly rows, 17,136 positive hourly challenge labels.
- Patient-level split, seed 42: 13,014 train, 3,254 validation, 4,068 test patients.
- Fixed threshold 0.5; LogisticRegression with median imputation, missingness indicators, standard scaling, class weighting, and max_iter=500.
- Static model: 40 features. Temporal model: 109 features, adding one-row lag, one-row difference, and trailing six-row mean for physiological measurements.
- The optimized local harness was algorithm-aligned with repository commit `fc5008f8009fea68a6197b5b3fb66d866210f4c7`, but was not launched through the repository CLI or GitHub Actions. A direct CLI reproduction remains required.

## Held-out test metrics

| Metric | Static baseline | Temporal features |
|---|---:|---:|
| AUROC | 0.7623 | 0.7873 |
| Average precision (AUPRC) | 0.0777 | 0.0842 |
| Brier score (lower is better) | 0.1903 | 0.1814 |
| Sensitivity at 0.5 | 0.6341 | 0.6845 |
| Specificity at 0.5 | 0.7564 | 0.7538 |
| PPV at 0.5 | 0.0540 | 0.0574 |
| NPV at 0.5 | 0.9895 | 0.9909 |

At this fixed threshold, the temporal variant has higher point estimates for AUROC, AUPRC, sensitivity, and NPV, with a slightly lower specificity. Positive predictive value is approximately 5.7%, so most positive hourly alerts at this threshold are not positive challenge-label rows. This is not a clinical false-alarm rate.

## Warnings and limitations

- `EtCO2` and its temporal derivatives were entirely missing and were skipped by imputation.
- No patient-cluster bootstrap intervals were computed for this run.
- The threshold was fixed at 0.5, not clinically optimized.
- Metrics are hourly-row metrics; they are not event-level clinical metrics.
- The challenge's `SepsisLabel` was used as supplied and was not shifted again.
- This is retrospective evaluation on one dataset, not external or prospective validation. Do not claim clinical readiness, novelty, or patentability from these results.

See [structured JSON results](../results/full_cohort_rerun_2026-10-14.json) and the [local experiment history](LOCAL_EXPERIMENTS.md).
