# VITALIS v0.1.0-rc1 — release-candidate readiness

**Candidate branch:** `release/v0.1.0-rc1`  
**Base snapshot:** `511fbac4ea7277086d2317d77c7b0fe4601b976d`  
**Release class:** research software / educational prototype only  
**Decision:** **NOT APPROVED for final release or clinical use**

This document freezes the release-candidate acceptance rules. It does not convert historical results into new evidence and does not claim that open gates have passed.

## 1. What RC1 is

RC1 packages the current VITALIS research code, adaptive physiological twin, synthetic streaming demonstrations, aggregate-only reporting dashboard, experiment protocols, and reproducibility tooling into a reviewable candidate.

The adaptive twin and supervised benchmark model are separate research outputs:

- The twin emits a bounded, unitless deviation/trajectory heuristic. It is not a sepsis probability or clinical risk score.
- The supervised retrospective workflow forecasts entry into the PhysioNet/CinC Challenge 2019 `SepsisLabel` positive window at predeclared horizons. This is not independently adjudicated biological sepsis onset.
- Set B is a held-out partition of the same Challenge benchmark, not an independent external clinical cohort.
- Synthetic demonstrations and software benchmarks do not establish sensor accuracy, clinical performance, or patient benefit.

## 2. Candidate software changes carried into RC1

- Persistent multisystem deviation now requires persistent channels across at least the configured minimum number of distinct physiological systems.
- Persistent channels confined to one system receive the distinct `persistent_channel_deviation` state.
- Regression coverage protects this distinction.
- Dashboard diagnostics expose persistent channel and distinct-system counts.
- The adaptive-twin specification documents the state semantics and the bounded score formula.
- The README labels the work as a research release candidate and links this gate.

## 3. Mandatory acceptance gates

A gate is PASS only when the evidence is linked to the exact candidate commit and can be independently inspected.

| Gate | Acceptance evidence | RC1 status |
|---|---|---|
| Candidate identity | Exact commit SHA, clean source manifest, reviewed diff | Pending final candidate commit |
| Standard software CI | Compile, install, hygiene/history checks, synthetic demos, full test suite all pass on exact candidate SHA | Prior code snapshot passed; exact RC1 check pending |
| Dashboard CI | Dashboard-specific tests/lint pass on exact candidate SHA | Recheck required |
| Full-cohort reproduction | Authorized clean checkout; pinned Python 3.11 environment; exact evaluator blob; fresh Set A/Set B caches; all predeclared analyses; strict historical reconciliation; aggregate-only artifact inspected | Historical evidence exists; exact RC1 run required |
| Baseline integrity | Preserve reference artifacts and unchanged six-decimal acceptance rule; report every mismatch; no silent replacement or relaxed tolerance | Mandatory |
| Set-B isolation | Set B remains evaluation-only; no fitting, calibration, threshold, feature, or model selection on Set B | Mandatory protocol invariant |
| Probability quality | Raw/calibrated proper scores compared with constant-prevalence reference; calibration intercept/slope and uncertainty; no winner claimed unless evidence supports it | Open scientific question |
| Independent methods review | Qualified statistician and clinical-methods reviewer assess endpoint, split, repeated measures, calibration, missingness, subgroup and utility claims | Not obtained |
| Data governance | Written institutional determination, dataset permissions/DUA, approved storage and data-management plan | Not verified / open |
| External validation | Genuinely new independent cohort, pre-registered/frozen model and analysis plan, aggregate-only disclosure-reviewed outputs | Not performed |
| Hardware safety | Bench-only verification, sensor accuracy/synchronization, electrical/biomedical safety and risk review | Not performed |
| Clinical evaluation | Separately approved prospective silent-mode and impact studies | Not performed; outside RC1 |

## 4. Non-negotiable reproducibility protocol

1. Preserve all historical aggregate reports and their provenance. Do not overwrite a historical result because a new run differs.
2. Run from a clean checkout of the exact candidate commit in the authorized data environment.
3. Verify the evaluator source blob against the preserved baseline provenance before data download.
4. Use the pinned Python 3.11 constraints and the baseline-compatible numerical kernel required by the workflow.
5. Keep patient-level files, caches, identifiers, predictions, credentials and restricted logs outside Git and public CI artifacts.
6. Keep Set B strictly evaluation-only.
7. Apply the existing six-decimal reconciliation rule unchanged. A failed comparison is a finding to investigate, not a reason to alter tolerance.
8. Inspect the aggregate artifact schema, cohort counts, source/environment manifests, cache fingerprints, calibration fields, and absence of row-level data before accepting the run.
9. If source identity, environment, or cohort provenance cannot be established, label the result provenance-qualified rather than canonical.

## 5. Allowed claims for RC1

Allowed, if accurately attributed to the cited commit/run:

- VITALIS is an experimental software framework for adaptive physiological deviation modelling and retrospective Challenge-label forecasting.
- The repository contains tested synthetic streaming and aggregate-reporting demonstrations.
- Specific historical benchmark results may be reported as retrospective Challenge-cohort findings with their exact split, seed, commit and limitations.

Not allowed:

- "Clinically validated", "diagnoses sepsis", "predicts biological sepsis onset", "safe for patient monitoring", "reduces mortality", "ready for hospital use", or equivalent claims.
- Treating the twin score as a probability or calibrated risk.
- Calling Set B external validation.
- Claiming the physical wearable, PCB, sensors, or bedside hardware have been built or safety-tested.
- Claiming patentability, clinical superiority, or patient benefit from the current evidence.

## 6. Release decision rule

RC1 may be shared as a **research preview** only after the exact candidate source and CI evidence are linked and the public-facing README/model card accurately state limitations. A final stable research release additionally requires an inspected exact-commit full-cohort artifact, completed source/privacy review, and documented independent methods review or an explicit, transparent statement that review remains outstanding.

No GitHub release tag or "stable" label should be created while mandatory gates are unresolved. Clinical deployment is outside this release and requires separate governance, validation, safety and regulatory processes.

## 7. Current evidence links

- Repository: https://github.com/culprit-k/VITALIS
- Current main snapshot at RC1 branch creation: `511fbac4ea7277086d2317d77c7b0fe4601b976d`
- Verified adaptive-twin code/test snapshot: [tests run #44467431900](https://github.com/culprit-k/VITALIS/actions/runs/44467431900), passed on `01d6845245edf6dfa55e49a4b58993f8eb790213`.
- Earlier full-cohort evidence and limitations: [project status](PROJECT_STATUS.md), [release acceptance matrix](RELEASE_ACCEPTANCE_MATRIX.md), [external validation protocol](EXTERNAL_VALIDATION_PROTOCOL.md), and [model card](MODEL_CARD.md).

**Safety statement:** Research and education only. Do not use VITALIS outputs to diagnose, triage, monitor, or make treatment decisions for any person. Do not connect this prototype to a patient.
