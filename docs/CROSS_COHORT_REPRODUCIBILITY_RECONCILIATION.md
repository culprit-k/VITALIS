# Cross-cohort reproducibility reconciliation

Date: 14 October 2026

## Purpose

This note reconciles the older reconstructed-harness cross-cohort model comparison with the exact-source execution of the checked-in evaluator, and records an independent rerun of the checked-in validation-only recalibration runner. The historical artifact is preserved unchanged.

## Source verification and rerun

The exact-source evaluator `scripts/evaluate_cross_cohort.py` was fetched from GitHub and its local Git blob SHA matched the checked-in source (`f700bf0848cd718301d9693c3dae13444a9bfe8b`). It was executed for Set-A training seeds 42, 123, and 2026; aggregate-only results are in [the exact-source reproduction JSON](../results/cross_cohort_exact_source_reproduction_2026-10-14.json).

The recalibration runner, cache builder, and focused tests were also retrieved from the verified source version. Their local Git blob SHAs match the source blobs recorded in [the reconciliation JSON](../results/cross_cohort_reproducibility_reconciliation_2026-10-14.json). The focused test suite passed (**7 passed**). The recalibration runner was rerun against the existing local memory-mapped caches for all three seeds. Its raw and recalibrated metrics matched the previously recorded source-verified outputs exactly for seeds 42 and 123, and within (1.5\times10^{-14}) for seed 2026. The tiny latter difference is floating-point precision, not a meaningful metric discrepancy.

The rerun confirmed that the calibration protocol partitions Set A into patient-disjoint training, validation, and unused groups (60/20/20), fits Platt recalibration on Set-A validation predictions only, and applies the frozen calibrator to Set B. Set B is not used for model fitting, recalibrator fitting, feature selection, or threshold selection.

## Historical artifact versus exact-source evaluator

The earlier [historical cross-cohort JSON](../results/cross_cohort_train_A_test_B_2026-10-14.json) came from a reconstructed local harness and reported different metrics. The checked-in exact-source values are now the canonical results for `scripts/evaluate_cross_cohort.py`.

| Metric (mean across seeds) | Historical static | Exact-source static | Historical temporal | Exact-source temporal |
|---|---:|---:|---:|---:|
| AUROC | 0.67809 | 0.67502 | 0.73569 | 0.73191 |
| AUPRC | 0.04639 | 0.04549 | 0.05974 | 0.05809 |
| Brier score | 0.16490 | 0.16589 | 0.09688 | 0.09722 |
| Sensitivity at 0.5 | 0.47777 | 0.47653 | 0.38485 | 0.38287 |
| Specificity at 0.5 | 0.79961 | 0.79707 | 0.92503 | 0.92299 |
| PPV at 0.5 | 0.03309 | 0.03264 | 0.06864 | 0.06662 |
| NPV at 0.5 | 0.99072 | 0.99067 | 0.99055 | 0.99050 |

These are small but material enough to retain as separate experiment records rather than treating the artifacts as interchangeable. The historical artifact is not deleted or overwritten.

## What is and is not known about the discrepancy

**Established:**
- The checked-in evaluator's source bytes were verified by Git blob SHA before execution.
- The checked-in recalibration runner's raw Set-B metrics agree with the exact-source evaluator's raw metrics to floating-point precision under the shared Set-A training split.
- The historical cross-cohort artifact does not include sufficient source provenance or training-split detail to reconstruct its original harness exactly.

**Not established:** whether the historical difference came from a different split, feature-cache build, model configuration, library/runtime setting, or another difference in the reconstructed harness. The existing historical artifact does not contain enough information to distinguish these explanations. We therefore do **not** attribute the discrepancy to a specific cause.

## Feature availability and interpretation

Set A has no observed EtCO2 values. The Set-A-fitted median imputer therefore skips EtCO2 and its derived temporal features, even though EtCO2 appears in Set B. The model does not benefit from Set-B EtCO2 values. This is a documented cohort-availability limitation, not evidence that the feature should be added or that imputation corrects the shift.

The temporal model has higher AUROC/AUPRC than the static model in the exact-source cross-cohort experiment, but lower sensitivity at the fixed 0.5 threshold. That threshold is a fixed research comparison, not a clinically selected operating point. Across-seed standard deviations are not confidence intervals. The results concern retrospective hourly challenge labels, not patient-level event sensitivity, lead time, clinical calibration, real-world false-alarm burden, or clinical utility.

## Reproducibility boundary

A full Git checkout remains unverified because this runtime could not resolve GitHub DNS. The checked-in source-byte identity was verified using Git blob hashes, and the exact source files were executed against local caches. Raw patient records, caches, patient-group vectors, and row-level predictions remain outside Git.

VITALIS remains research-only. No diagnosis, triage, treatment, or patient-care claim follows from these analyses.
