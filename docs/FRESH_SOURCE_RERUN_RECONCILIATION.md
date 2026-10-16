# Fresh-source rerun reconciliation — release-readiness checkpoint

**Date:** 14 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Pull request:** [#1](https://github.com/culprit-k/VITALIS/pull/1)  
**Branch:** `work/exact-checkout-reproduction`

## Outcome

The checked-in cross-cohort recalibration runner was rerun separately for seeds 42, 123, and 2026 against the available local Set-A/Set-B feature caches. The runner and relevant source files were fetched from the PR branch and their local Git blob hashes matched the GitHub blob hashes. The rerun reproduced the existing source-verified aggregate metrics to floating-point precision.

**Important qualification:** this does **not** close the fresh-clone gate. A new `git clone https://github.com/culprit-k/VITALIS.git` attempt failed because this runtime could not resolve `github.com`. The rerun used existing local feature caches and a source-verification workspace, not a fresh Git checkout or fresh cache build. Do not label it a clean-checkout reproduction.

## Source provenance

The following source blobs match GitHub's PR-branch blob IDs:

- `scripts/build_feature_cache.py`: `eba7dda1532675c2e3f21476b0bba2cead537e78`
- `scripts/evaluate_cross_cohort_recalibration.py`: `fe355c4b7b77b322ae5c134fe7fdc0b9cbb73200`
- `scripts/evaluate_cross_cohort.py`: `dc736ef7a7fe31c477d4626971dd5b0abd255d2f`
- `scripts/bootstrap_heldout_scores_fast.py`: `92b41af5f96f251ce39a222d026c23fd9102a15b`
- `tests/test_cross_cohort_recalibration.py`: `4c368280996cb64a8f58fdba6acdf57026feb71e`
- `tests/test_evaluate_cross_cohort.py`: `77930cd4607653fcef6bdbb290e158f574678ad5`
- `tests/test_bootstrap_heldout_scores_fast.py`: `db529f218e2792932e5064b1c0139fdcedaff367`

Environment recorded for the rerun: Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, with BLAS/OpenMP thread counts limited to one. The source-verification workspace's available tests reported 18 passed; this is not a full test run from a fresh checkout of the current PR branch.

## Cohort and split integrity

- Set A: 20,336 patients, 790,215 hourly rows, 17,136 positive hourly labels.
- Set B: 20,000 patients, 761,995 hourly rows, 10,780 positive hourly labels.
- All patient and row split counts matched the previously recorded source-verified artifact for all three seeds.
- Set B remained evaluation-only. It was not used for model fitting, recalibrator fitting, feature selection, or threshold selection.
- Row-level score archives were written only under a local directory outside the repository and were not committed.

## Reconciliation

Compared with `results/cross_cohort_validation_A_recalibration_test_B_source_verified_2026-10-14.json`:

| Seed | Train rows | Validation rows | Unused rows | Max absolute raw-metric difference | Max absolute recalibrated-metric difference |
|---:|---:|---:|---:|---:|---:|
| 42 | 473,301 | 158,883 | 158,031 | 5.16e-14 | 1.70e-15 |
| 123 | 470,100 | 160,790 | 159,325 | 9.81e-14 | 4.57e-15 |
| 2026 | 474,841 | 157,439 | 157,935 | 1.46e-14 | 1.84e-15 |

AUROC and AUPRC matched exactly at reported floating-point precision; other metric differences were below (1\times10^{-12}). This supports repeatability of the checked-in runner against the existing caches and recorded baseline artifact. It does not establish correctness of the underlying benchmark labels, clinical calibration, or clinical usefulness.

Aggregate-only machine-readable details are in [the reconciliation JSON](../results/fresh_source_rerun_reconciliation_2026-10-14.json).

## Remaining release gates

1. Retry a fresh clone and follow [the exact-checkout runbook](EXACT_CHECKOUT_REPRODUCTION.md) when GitHub DNS/network access works. Verify the checkout commit, clean status, dependencies, tests, source hashes, and cache creation from authorized source data.
2. Obtain independent clinical/statistical review of label timing, patient-level split protocol, calibration/domain shift, the bootstrap estimand, and the exploratory 5% feature-coverage cutoff.
3. Review the full repository history for accidentally committed sensitive data, local artifacts, or secrets; the changed-path audit is not a history-wide scan.
4. Keep PR #1 draft and unmerged until those gates are addressed and a deliberate release decision is made.

**Conclusion:** exact-source rerun reconciliation passed; fresh Git checkout, full current-branch test execution from that checkout, and independent methodological review remain open. VITALIS remains research-only and is not clinically validated.
