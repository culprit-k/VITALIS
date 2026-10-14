# Repository-runner reconciliation — full cohort

## Outcome

The cache-backed evaluator completed separately for seeds 42, 123, and 2026 against a local memory-mapped cache built from all 20,336 training_setA patient files. The cache verified 790,215 hourly rows, 17,136 positive challenge-label rows, 109 feature columns, 20,336 patient groups, and four completed cache chunks.

**Important provenance limit:** the local working copies were reconstructed from the checked-in runner logic but are not byte-identical to the GitHub blobs. This run reconciles the algorithm/results; it does not close the strict source-byte identity exception.

## Aggregate metrics

Mean ± sample standard deviation across split seeds; SD is not a confidence interval.

| Metric | Static | Temporal |
|---|---:|---:|
| AUROC | 0.7628 ± 0.0013 | 0.7884 ± 0.0019 |
| AUPRC | 0.0846 ± 0.0085 | 0.0886 ± 0.0059 |
| Brier score | 0.1894 ± 0.0038 | 0.1816 ± 0.0044 |
| Sensitivity at threshold 0.5 | 64.33% | 67.72% |
| PPV at threshold 0.5 | 5.60% | 5.79% |

Temporal features have higher mean AUROC by 0.0256 and higher mean AUPRC by 0.0040, with lower mean Brier score by 0.0078. This is exploratory evidence, not proof of clinical benefit.

## Per-seed metrics

| Seed | Test rows | Positive hourly labels | Static AUROC | Temporal AUROC | Static AUPRC | Temporal AUPRC |
|---:|---:|---:|---:|---:|---:|---:|
| 42 | 159,102 | 3,411 | 0.7623 | 0.7873 | 0.0777 | 0.0842 |
| 123 | 160,217 | 3,557 | 0.7643 | 0.7906 | 0.0941 | 0.0952 |
| 2026 | 155,703 | 3,470 | 0.7619 | 0.7874 | 0.0820 | 0.0863 |

## Remaining work

1. Keep cache files outside Git; they contain derived row-level patient features.
2. Strictly verify checked-in source bytes and ensure this local execution uses those exact files.
3. Add paired patient-cluster uncertainty intervals using matched held-out predictions if needed; current output contains aggregate-only predictions metrics.
4. External validation, prospective evaluation, and clinical/statistical supervision are still required before any clinical claim.
