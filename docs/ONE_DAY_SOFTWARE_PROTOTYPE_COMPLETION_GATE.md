# VITALIS 1-day software prototype completion gate

**Purpose:** time-box the remaining software work without pretending that a retrospective research prototype is clinically validated.

## Definition of done for the one-day target

The deliverable is a reproducible, runnable research prototype, not a medical device or clinical decision system.

### Required in this sprint

1. **Reproducible environment**
   - One documented Python environment and dependency lock/constraints.
   - Unit, integration and dashboard tests pass.
   - A full-cohort workflow finishes or records a specific, actionable failure.
   - Preserve the historical 2026-10-14 baseline. Do not weaken its six-decimal acceptance rule.
   - If the historical baseline cannot be reproduced from its recorded provenance, explicitly mark historical reconciliation unresolved and produce a separate clean-checkout reference only after a clean run and an independent repeat.

2. **Cohort and leakage integrity**
   - Validate patient counts, label counts, feature schema, time ordering and missingness.
   - Split by patient, not by row.
   - Ensure Set B is never used for model fitting, feature selection, calibration fitting or threshold selection.
   - Keep raw cohort data, patient identifiers, row-level predictions and caches out of Git and release artifacts.

3. **Models**
   - Static logistic-regression baseline.
   - Causal temporal feature model.
   - Patient-relative physiology deviation features using strictly prior observations.
   - Streaming adaptive twin with robust reference, rolling baseline, two-sided CUSUM, persistence, missingness/coverage gating and multisystem deviation state.
   - Keep the twin's unitless deviation score separate from supervised probabilities. Do not describe the twin heuristic as a calibrated probability or time-to-sepsis prediction.

4. **Probability and alert evaluation**
   - AUROC, AUPRC, Brier score and log loss.
   - Calibration intercept/slope and reliability summaries.
   - Sensitivity, specificity, PPV, alert burden and lead-time/coverage definitions with explicit denominators.
   - Patient-cluster uncertainty intervals.
   - Compare balanced and unweighted training, and Set-A-only calibration, as predeclared experiments. Report negative results; do not tune on Set B.

5. **Runnable handoff**
   - One documented command to run unit tests and one to run a small synthetic demo.
   - One documented command to run the full cohort workflow.
   - Model card, protocol, known limitations, data access notes and artifact inventory.
   - Release candidate stays draft until the complete run and artifact audit pass.

## Current known blockers

- The historical baseline reconciliation has previously matched 37/42 metric mean/sample-SD pairs (75/84 scalar values), with five temporal-model mismatches at 1h/3h. Keep the gate strict and investigate provenance; do not silently replace the baseline.
- The full-cohort pipeline is expensive and downloads official Challenge cohorts into ephemeral runner storage. Unit-test success does not imply full-cohort success.
- Probability calibration previously drove Brier score down while sensitivity at the fixed 0.5 threshold became effectively zero. Brier score must not be interpreted alone as a successful alerting system.
- The physiology twin is an algorithmic research layer. Its scores are heuristic and do not establish diagnosis, prognosis, clinical benefit or safe treatment decisions.

## Explicit exclusions from the one-day claim

The one-day goal cannot responsibly include external prospective validation, clinical-grade safety assurance, regulatory clearance, hospital integration or a finished hardware device. These require separate milestones.

## Completion report template

The release report must state:
- exact commit SHA and environment;
- test results and full-cohort workflow URL;
- cohort counts and artifact integrity checks;
- baseline reconciliation result (pass/fail, never omitted);
- metrics with uncertainty and alert burden;
- known failures and limitations;
- a clear statement that this is research-only and not for patient care.
