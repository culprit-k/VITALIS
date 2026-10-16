# VITALIS full-cohort reconciliation acceptance rule

**Applies to:** the next dependency-pinned clean-checkout Set A → Set B horizon reproduction.

## Predeclared acceptance criteria

1. Set A and Set B patient counts, hourly row counts, positive hourly Challenge-label counts, feature schema, and target-eligible row counts must match the preserved baseline exactly.
2. Compare the mean and sample standard deviation across seeds 42, 123, and 2026 for each of these metrics: AUROC, AUPRC, Brier score, sensitivity, specificity, alerts per at-risk patient-day, and future-positive-window coverage.
3. There are 42 metric/model/horizon mean–SD pairs: 7 metrics × 2 models × 3 horizons.
4. Each mean and SD must round to the same six decimal places as the preserved aggregate in `results/horizon_cross_cohort_2026-10-14.json` (equivalent to an absolute difference below 0.0000005 before rounding-boundary effects). The automated check must fail closed if any pair differs.
5. No threshold, seed, horizon, model, metric, or tolerance may be changed after inspecting the new Set B results to obtain a pass. If reconciliation fails, preserve both outputs, record all differences, and investigate the environment or implementation rather than changing the acceptance rule.

## Environment control

The clean-checkout workflow uses `constraints/reproduction-py311.txt` to pin the scientific Python stack and sets BLAS/OpenMP thread counts to one. The exact resolved environment and source manifests are retained with the aggregate-only workflow artifact. Any dependency-pin change requires a new run and explicit explanation.

## Interpretation boundary

A successful reconciliation establishes computational reproducibility of this retrospective benchmark under the recorded source and environment. It does not establish independent clinical validity, clinical utility, safe alarm thresholds, or prediction of independently observed biological sepsis onset. Set B remains evaluation-only and is not an independent prospective validation cohort.
