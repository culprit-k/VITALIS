# VITALIS independent methods review checklist

**Status:** prepared for independent review; no independent reviewer sign-off is claimed.  
**Date:** 16 October 2026  
**Scope:** retrospective research-code release only. This checklist does not authorize clinical use.

## Reviewer instructions

A qualified statistician, clinical informatician, or critical-care prediction researcher should independently inspect the referenced protocol, implementation, and aggregate outputs. Record each item as `PASS`, `CONCERN`, or `NOT ASSESSED`, with file/line or artifact evidence. Do not use Set B to tune any decision during review.

## Required review questions

### 1. Target and temporal alignment
- [ ] Verify the target is entry into the PhysioNet/CinC Challenge 2019 `SepsisLabel`-positive window within 1, 3, or 6 hours—not independently adjudicated biological sepsis onset.
- [ ] Confirm current-positive rows and each patient's final H rows are excluded, and future labels never cross patient boundaries.
- [ ] Assess whether the Challenge's six-hour lead convention creates target ambiguity or overlap between forecast horizons.

Evidence: `docs/HORIZON_FORECASTING.md`, `scripts/evaluate_horizon_cross_cohort.py`, `src/vitalis/horizon.py`.

### 2. Patient split and leakage
- [ ] Verify patient-level separation for model fitting, calibration, operating-point development, and any uncertainty resampling.
- [ ] Verify feature generation uses only information available at or before the prediction time.
- [ ] Check imputation, missingness indicators, scaling, feature selection, and cache construction for cross-patient or future leakage.
- [ ] Confirm Set B is used only for the frozen final retrospective evaluation; no threshold, calibration, model, or feature selection is based on Set B.

Evidence: `docs/HORIZON_CROSS_COHORT_EXECUTION.md`, `docs/SET_A_PLATT_CALIBRATION_PROTOCOL.md`, source scripts and current aggregate artifacts.

### 3. Probability quality and calibration
- [ ] Interpret AUROC/AUPRC separately from Brier score, log loss, calibration intercept/slope, and reliability bins.
- [ ] Compare against a constant-prevalence predictor using identical eligible rows.
- [ ] Review whether low Brier values are dominated by rare positive labels rather than useful risk ranking.
- [ ] Treat the Platt experiment as unsuccessful for the fixed 0.5 alert reference because sensitivity is near zero; do not describe it as a usable calibration win.
- [ ] Do not promote the physiology-feature candidate solely because AUROC/AUPRC improve: its Brier score worsened at all evaluated horizons.

Evidence: `docs/SET_A_PLATT_CALIBRATION_RESULTS_2026-10-16.md`, `docs/PHYSIOLOGICAL_FEATURE_ABLATION_RESULTS_2026-10-15.md`, `docs/MODEL_CARD.md`.

### 4. Operating point, alert burden, and 5% coverage rule
- [ ] Confirm the 0.5 threshold is labelled a fixed research reference, not a clinically justified threshold.
- [ ] Review sensitivity and PPV alongside patient-level alerts per at-risk patient-day and future-positive-window coverage.
- [ ] Inspect the utility analysis assumptions and ensure illustrative missed-window costs are not presented as clinician-elicited or validated.
- [ ] Treat the 5% Set-A feature-coverage cutoff as exploratory. Require a predeclared development-only rationale and sensitivity analysis before making it a default; do not call it optimal or clinically justified.
- [ ] Verify no operating point was selected or changed after observing Set B results.

Evidence: `docs/UTILITY_OPERATING_POINT_FRAMEWORK.md`, `docs/HORIZON_UTILITY_BOOTSTRAP_RESULTS_2026-10-15.md`, `docs/RELEASE_READINESS_AUDIT.md`.

### 5. Uncertainty and estimand
- [ ] Confirm the bootstrap resampling unit matches the patient-level generalization claim and preserves paired comparisons where required.
- [ ] Assess dependence from repeated hourly rows, patient heterogeneity, event clustering, and the number of independent patients versus rows.
- [ ] Confirm intervals are described as conditional/descriptive where appropriate, not as proof of prospective clinical performance.
- [ ] Verify seed-specific estimates are shown and not misrepresented as a pooled independent replication.

Evidence: paired comparison and utility bootstrap reports; bootstrap implementation and tests.

### 6. Cohort shift, measurement process, and fairness
- [ ] Assess Set A/Set B prevalence and feature-distribution differences and their implications for probability transport.
- [ ] Review measurement-frequency/missingness as possible care-process proxies and sources of bias.
- [ ] Confirm no subgroup safety, fairness, or real-world sensor reliability claims are made without evidence.
- [ ] Identify the external data and prospective silent-mode studies required before any clinical translation.

Evidence: `docs/MODEL_CARD.md` and the aggregate cross-cohort reports.

### 7. Adaptive twin and supervised model interface
- [ ] Confirm the adaptive twin's heuristic deviation/trajectory score is not presented as a probability of sepsis.
- [ ] Verify unavailable, stale, missing, invalid-unit, out-of-order, and reset/patient-isolation states are explicit.
- [ ] Confirm the synthetic demo is clearly identified as generated data and is not evidence of clinical performance.
- [ ] Verify no unfrozen supervised artifact is implied to be wired into the demo.

Evidence: `docs/ADAPTIVE_TWIN_IMPLEMENTATION.md`, `docs/VITALIS_PB_ALGORITHM.md`, `src/vitalis/stream.py`, synthetic demo tests.

### 8. Reproducibility, privacy, and release claims
- [ ] Verify current-head clean-checkout Python 3.11 reconciliation passes all 42 pairs/84 scalars under the immutable six-decimal rule.
- [ ] Review the Python 3.13 diagnostic as a portability check; do not silently substitute it for the pinned acceptance environment.
- [ ] Inspect the full diff and full Git history for raw data, patient-level outputs, caches, secrets, and credentials; a changed-path audit alone is insufficient.
- [ ] Verify aggregate artifacts contain no row-level predictions, patient identifiers, or raw data.
- [ ] Confirm all release claims say retrospective/research-only, and explicitly state that clinical utility, prospective validation, and patient benefit are unestablished.

Evidence: `docs/RELEASE_ACCEPTANCE_MATRIX.md`, `docs/GIT_HISTORY_PRIVACY_AUDIT.md`, current workflow artifacts and PR diff.

## Decision record (reviewer to complete)

- Reviewer role / relevant expertise:
- Date and reviewed commit SHA:
- Items marked PASS:
- Items marked CONCERN, with severity and evidence:
- Items NOT ASSESSED and why:
- Required corrections:
- Recommendation: `REVISE` / `RESEARCH-CODE RELEASE CANDIDATE` / `DO NOT RELEASE`
- Explicit statement: this is not a clinical deployment approval.

## Current known blockers (do not mark complete without evidence)

1. Current-head full-cohort reproduction and cross-runtime diagnostic are pending as of the document's creation.
2. No independent reviewer sign-off has yet been obtained.
3. The full Git-history privacy/secret scan and human triage remain pending.
4. No independent external clinical cohort, prospective silent-mode evaluation, or clinical utility evaluation exists.

**Non-negotiable:** do not modify the historical baseline, acceptance tolerance, fixed evaluation threshold, patient split, seeds, horizons, or Set B isolation rule to obtain a pass. Keep PR #2 draft/open/unmerged until the release decision is explicitly made.
