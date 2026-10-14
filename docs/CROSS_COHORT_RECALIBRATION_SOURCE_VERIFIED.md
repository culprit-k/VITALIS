# VITALIS cross-cohort recalibration — source-verified run

Date: 14 October 2026

## Execution and provenance

- Repository main commit: `90ce87677b1e1692c3a6f04f7394f9ce59cf7481`.
- The exact checked-in source blobs for the cache builder, recalibration runner, and focused test file were fetched from `main`; local `git hash-object` values matched the GitHub blob SHAs exactly.
- A full `git clone` was attempted but could not resolve `github.com` DNS in this runtime. Accordingly, this is a byte-identical-source run, not a verified full Git checkout.
- Environment: Python 3.13.5; NumPy 2.3.5; pandas 2.2.3; scikit-learn 1.8.0.
- Focused tests: **7 passed**. GitHub Actions tests workflow run [38589529596](https://github.com/culprit-k/VITALIS/actions/runs/38589529596) also completed successfully.
- Local input archive contained 40,336 patient `.psv` files. Aggregate integrity checks matched both cohort totals; schemas had 41 columns and no mismatched or empty patient files.

## Cohort and protocol

| Cohort | Patients | Hourly rows | Positive hourly challenge-label rows |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 |
| Set B | 20,000 | 761,995 | 10,780 |

For each seed (42, 123, 2026), set A was partitioned by patient into 60% model training, 20% validation for Platt recalibration, and 20% unused. Static and temporal logistic-regression models were fitted on the training partition. Recalibration used only set-A validation predictions; set B was held out for evaluation and not used for fitting or threshold selection. The runner emitted aggregate metrics only.

## Results: mean ± sample SD across three split seeds

| Model / stream | AUROC | Average precision | Brier score | Log loss | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| Static, raw | 0.675017 ± 0.005824 | 0.045495 ± 0.001793 | 0.165892 ± 0.005734 | 0.522278 ± 0.012058 | 0.367623 ± 0.008949 |
| Static, recalibrated | 0.675017 ± 0.005824 | 0.045495 ± 0.001793 | 0.014071 ± 0.000187 | 0.071721 ± 0.000150 | 0.018862 ± 0.000645 |
| Temporal, raw | 0.731911 ± 0.006419 | 0.058095 ± 0.001481 | 0.097222 ± 0.002160 | 0.352586 ± 0.005239 | 0.263268 ± 0.004877 |
| Temporal, recalibrated | 0.731911 ± 0.006419 | 0.058095 ± 0.001481 | 0.013830 ± 0.000032 | 0.068996 ± 0.000280 | 0.013361 ± 0.000821 |

These standard deviations describe variation across three split seeds; they are not confidence intervals. See the [aggregate JSON](../results/cross_cohort_validation_A_recalibration_test_B_source_verified_2026-10-14.json) for per-seed metrics, patient/row split counts, source hashes, and environment.

## Reconciliation with the prior exploratory artifact

The raw Set-B metrics reproduce to floating-point precision; the largest absolute delta was about 1.9e-7 in AUROC. Recalibrated AUROC/AUPRC are essentially unchanged, but the recalibrated probability metrics are not numerically identical: the largest absolute delta was about 8.31e-4 in mean predicted probability, with smaller but nonzero Brier/log-loss differences.

The historical artifact came from a reconstructed harness and did not record enough environment/provenance detail to attribute the calibration discrepancy conclusively. The new source-verified run should be treated as the canonical result for these checked-in source files; the historical artifact is retained unchanged. This discrepancy should not be hidden or described as exact numerical agreement.

## Warnings and limitations

`SimpleImputer` reported all-missing EtCO2 and derived EtCO2 features (static feature index 7; temporal indices 7, 61–63). The runs completed, but these warnings remain visible and feature handling should be reviewed before future model changes.

This remains retrospective evaluation against hourly challenge labels from the same benchmark. It does not establish clinical calibration, event-level sensitivity, lead time, real-world false-alarm burden, external validity, or clinical utility. VITALIS remains research-only. Raw patient records, local caches, group vectors, and row-level predictions were not committed.
