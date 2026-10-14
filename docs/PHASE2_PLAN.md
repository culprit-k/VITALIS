# VITALIS Phase 2: calibration and robustness

## Purpose

Phase 2 investigates whether the Phase 1 ranking is stable and whether model probabilities are descriptively calibrated under the challenge-label setup. The first implementation step adds reusable calibration and predictor-missingness summaries. These are aggregate research diagnostics only.

## Prespecified work packages

1. **Calibration diagnostics:** report Brier score, log loss, calibration intercept and slope, and reliability bins on held-out patients. Fit any recalibration mapping on validation patients only; never fit it on test outcomes.
2. **Missingness audit:** report feature-level and overall missingness on training, validation, and test partitions. Keep imputation and feature selection fitted on training data only.
3. **Robustness checks:** compare the static baseline against temporal and personal-baseline variants on matched patient-disjoint splits. Treat subgroup analyses as exploratory and suppress tiny cells; avoid interpreting demographic group differences as causal.
4. **Protocol integrity:** preserve the supplied Challenge 2019 SepsisLabel without shifting it again. Distinguish row-level challenge-label metrics from event-level clinical outcomes.
5. **Reproducibility:** execute the canonical repository runner on the same deterministic sample, compare it with the recorded local artifact, and record any discrepancy before increasing cohort size.

## Guardrails

- Do not select thresholds or recalibration settings from test data.
- Do not publish patient-level predictions, identifiers, or row-level records.
- Do not describe challenge-positive label windows as independently observed clinical onset.
- No patient-facing use, clinical benefit claims, patentability claims, or hardware purchase is justified by Phase 2 diagnostics alone.

## Initial implementation

- Added `src/vitalis/calibration.py` with aggregate calibration and missingness summaries.
- Added unit tests for valid output, invalid probabilities, single-class samples, and aggregate missingness ordering.
- Added `scripts/evaluate_calibration_robustness.py` to generate matched patient-disjoint splits, train the three feature variants, fit optional recalibration on validation patients only, and export aggregate test calibration and split-specific missingness summaries.
- GitHub Actions passed after correcting a numerical edge case where logistic recalibration could round probabilities to exactly 0 or 1.
- The full local dataset run is still pending; CI tests validate code behavior, not empirical calibration.


## Expanded exploratory checks (completed locally)

- [x] Compared median imputation with and without missingness indicators on matched patient-disjoint splits.
- [x] Compared raw probabilities with Platt/logistic and isotonic recalibration, with calibration fitted on validation patients only.
- [x] Ran exploratory age/gender subgroup and missingness-stratified checks with small-cell suppression.
- [x] Added an aggregate-only summary: [Phase 2 robustness grid](../results/phase2_robustness_grid_summary.json).
- [x] Documented results and limitations in [Phase 2 calibration/robustness report](PHASE2_CALIBRATION_ROBUSTNESS_RESULTS.md).

## Phase 2 completion status

The exploratory analyses and unit-tested helper implementation are complete. **The phase is not fully closed for reproducibility** until the canonical checked-in runner is executed in the same runtime as the local dataset and its output is reconciled with the local equivalent. The current local container cannot resolve GitHub source hosts, so that exact step could not be executed here. Full-cohort, external, and prospective validation are separate future phases, not Phase 2 claims.

The results do not establish clinical calibration or utility. Platt recalibration's lower row-level Brier/log loss is compatible with compressing probabilities toward the low row-level prevalence; AUROC did not improve. No model is selected for patient care.
