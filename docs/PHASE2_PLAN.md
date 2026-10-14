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
