# VITALIS manuscript — working draft

**Status:** initial manuscript scaffold; not submitted or independently reviewed  
**Evidence cut-off:** VITALIS RC1 candidate, 19 November 2026  
**Candidate commit:** `a4d4d2641ffe13383960d5094ca6791e55befe1c`  
**Exact full-cohort run:** [#44467873336](https://github.com/culprit-k/VITALIS/actions/runs/44467873336)  
**Research-only:** no clinical validation or patient-care use is claimed.

## Working title

**VITALIS: An Adaptive Physiological Digital-Twin Framework for Longitudinal Deviation Modelling and Retrospective Deterioration Research**

## Draft abstract

### Background
Physiological observations are longitudinal, noisy, intermittently missing and strongly dependent on an individual's prior state. A single measurement may therefore be difficult to interpret without its temporal context. VITALIS is a research software framework designed to explore adaptive physiological reference states and longitudinal deviation patterns while keeping heuristic state estimation separate from supervised prediction.

### Objective
To describe the architecture, software safeguards and retrospective evaluation workflow of VITALIS, and to report the current evidence and limitations of its adaptive physiological and benchmark-forecasting components.

### Methods
VITALIS combines a timestamped observation contract, data-quality and freshness checks, robust personal-reference calculations, deviation and persistence summaries, and a separate supervised time-series modelling workflow. The retrospective forecasting experiments use the PhysioNet/CinC Challenge 2019 Set A and Set B cohorts and define 1-, 3- and 6-hour targets as future entry into the Challenge `SepsisLabel`-positive window. Patient-level partitioning, training-only preprocessing, Set B evaluation-only isolation, pinned runtime provenance and a predeclared six-decimal aggregate reconciliation rule are maintained. The adaptive twin emits a bounded unitless heuristic; it does not emit a calibrated sepsis probability.

### Results
The exact RC1 full-cohort clean-checkout reproduction completed successfully on commit `a4d4d2641ffe13383960d5094ca6791e55befe1c`. The source audit covered Set A (20,336 patients; 790,215 rows) and Set B (20,000 patients; 761,995 rows). Fresh 109-feature cache-integrity checks passed. Historical reconciliation matched 42/42 mean/standard-deviation pairs and 84/84 scalar values under the unchanged six-decimal rule, with zero mismatches. Patient-relative physiology ablation did not improve Brier score relative to the temporal baseline in any of the nine horizon/seed comparisons. Calibration and a Set A-only threshold sweep were conducted, but no operating threshold was selected because an independently reviewed alert-budget/utility objective has not been approved.

### Conclusions
VITALIS provides a reproducible research framework for exploring adaptive physiological deviation modelling and retrospective Challenge-label forecasting. Current evidence supports software reproducibility for the specified candidate and benchmark workflow, not clinical validity, useful operating thresholds, independent external validation, or patient benefit. The artifact's patient-derived deterministic fingerprints require privacy review before broader distribution. Independent methods review, genuinely independent cohort evaluation, governance approval and physical bench testing remain necessary.

## Research question and contribution

**Primary question:** Can a modular, quality-aware adaptive physiological software framework represent within-person longitudinal deviations in a reproducible way, and how should such a framework be evaluated separately from retrospective supervised forecasting?

**Contribution claims to test, not assume:**
1. A hardware-independent observation contract can make time, units, freshness, quality and session boundaries explicit.
2. A robust adaptive reference can produce interpretable, unitless deviation and persistence summaries on synthetic/replay streams.
3. Separating adaptive heuristics from supervised predictions prevents an uncalibrated twin score from being misrepresented as probability.
4. Exact-source reproducibility and aggregate reconciliation can be audited independently.
5. Retrospective benchmark results expose important limitations that constrain further model development.

Do not claim novelty, superiority, clinical utility or patentability without a dedicated evidence review.

## Methods outline

1. **Framework architecture:** canonical observation contract, stream validator, adaptive state, feature pipeline, separate supervised predictor interface, dashboard and audit/provenance.
2. **Adaptive twin:** prior-only personal reference, median/MAD robust scale, bounded deviation, EWMA/CUSUM, persistence and multisystem semantics; document warm-up and missing-data rules.
3. **Retrospective cohorts:** official Challenge 2019 Set A and Set B, cohort provenance and exact inclusion/row counts; verify dataset terms and cite the official source.
4. **Target:** future entry into the Challenge `SepsisLabel`-positive window at 1, 3 and 6 hourly rows. Explicitly distinguish this proxy target from biological onset.
5. **Splits and leakage control:** patient-level partitioning, training-only preprocessing, patient-disjoint calibration/threshold-development partitions, and Set B evaluation-only.
6. **Models and baselines:** static and temporal logistic-regression baselines plus experimental patient-relative features; report model/configuration hashes and all seeds.
7. **Metrics:** AUROC, AUPRC, prevalence, Brier score, log loss, calibration diagnostics, threshold-specific metrics, alert burden and patient-cluster uncertainty where available.
8. **Reproducibility:** exact commit, clean source manifests, Python/dependency/BLAS environment, fresh cache audit, artifact manifest and immutable reconciliation rule.
9. **Privacy and governance:** artifact-level inventory, fingerprint risk review, dataset permissions, storage boundaries and disclosure review.

## Results tables to complete from inspected aggregate reports

| Table | Required contents | Status |
|---|---|---|
| 1 | Cohort flow, patients, rows, positive labels, source provenance | Counts verified in exact RC1 record; add source citations |
| 2 | 1/3/6-hour model discrimination and uncertainty by seed | Populate from inspected aggregate artifact |
| 3 | Brier/log loss and calibration diagnostics vs prevalence reference | Populate from inspected aggregate artifact |
| 4 | Alert-burden/threshold sweep development-only results | Populate; no threshold selected |
| 5 | Patient-relative physiology ablation vs temporal baseline | Negative direction verified; add exact estimates and intervals |
| 6 | Reproduction environment, source identity and reconciliation | 42/42 and 84/84 matched; add artifact provenance |
| 7 | Adaptive-twin software tests and synthetic replay performance | Distinguish synthetic software measurements from device evidence |

Do not fill missing values from memory or infer them from plots. Each table row must point to the exact run artifact and analysis script.

## Limitations that must remain visible

- Set B is a held-out Challenge cohort, not independent external clinical validation.
- The Challenge label is not independently adjudicated biological sepsis onset.
- Row-level observations are repeated within patients; uncertainty must respect patient clustering.
- No clinically justified operating threshold has been selected.
- The tested patient-relative physiology ablation had unfavorable Brier-score differences.
- Adaptive-twin scores are unitless heuristics, not calibrated probabilities.
- Synthetic demos do not validate sensors, hardware, clinical performance or patient benefit.
- RC1 aggregate artifact contains deterministic patient-derived fingerprints; privacy acceptability is unresolved.
- Independent methods review, governance, licensing, external validation and prospective evaluation are incomplete.

## Reporting and submission checklist

- [ ] Confirm all authors meet authorship criteria and approve the final manuscript.
- [ ] Obtain independent clinical and statistical review.
- [ ] Verify every reported number against the retained exact-run artifact.
- [ ] Add official dataset citations and verify dataset use/redistribution terms.
- [ ] Add software availability, version, commit, environment and reproducibility statement.
- [ ] Add ethics/data-governance statement appropriate to retrospective public benchmark data and institutional requirements.
- [ ] Complete relevant prediction-model/software reporting checklists with a qualified reviewer.
- [ ] Select journal only after checking scope, peer review, indexing, fees, preprint policy and data/code requirements.
- [ ] Do not submit until privacy review and all co-author approvals are complete.

## Evidence references

- Exact candidate full-cohort workflow: https://github.com/culprit-k/VITALIS/actions/runs/44467873336
- Exact candidate artifact: https://github.com/culprit-k/VITALIS/actions/runs/44467873336/artifacts/14509017475
- RC1 release candidate: https://github.com/culprit-k/VITALIS/pull/48
- Independent review package: https://github.com/culprit-k/VITALIS/pull/56
- Independent evaluation protocol: https://github.com/culprit-k/VITALIS/blob/release/v0.1.0-rc1/docs/INDEPENDENT_EVALUATION_PROTOCOL.md
- Model card: https://github.com/culprit-k/VITALIS/blob/release/v0.1.0-rc1/docs/MODEL_CARD.md

**Safety:** VITALIS is research and education software only. It must not be used to diagnose, triage, monitor or treat any person.
