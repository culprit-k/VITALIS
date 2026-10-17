# VITALIS software research prototype: release gate

**Purpose:** a time-boxed checklist for producing a reproducible, auditable research prototype. A deadline does not waive evidence requirements.

## Release definition

The software research prototype is releasable only when the following are true:

- [ ] Latest-main strict full-cohort run [#39024691664](https://github.com/culprit-k/VITALIS/actions/runs/39024691664) is queued for main commit `51168b4c1a1978d8505c2db14657a4ba0cf0ba62`, which includes the patient-ID argument fix and main-branch trigger update. The prior run [#39019018791](https://github.com/culprit-k/VITALIS/actions/runs/39019018791) failed at Set A Platt calibration because the evaluator omitted the required patient IDs; this was corrected in [PR #24](https://github.com/culprit-k/VITALIS/pull/24), merged as `d59291a4a63a610eb6d7223109a56c246acaa19b`. Standard CI passed on the fix (249 tests, [#39024588465](https://github.com/culprit-k/VITALIS/actions/runs/39024588465)). Do not mark reproduction complete until the new run passes through calibration, threshold sweep, aggregate-only assertions, and six-decimal baseline reconciliation.
- [x] Standard CI passed on main commit `4eb3d15c024b2a1d295f657c2cb96e7eb9ff16bd`: [run #39018965402](https://github.com/culprit-k/VITALIS/actions/runs/39018965402) passed all 16 steps, including **249 tests**. Its [source/history audit artifact #12094949533](https://github.com/culprit-k/VITALIS/actions/runs/39018965402/artifacts/12094949533) (SHA-256 `37ad247aa2dc3b4f6c29287447f1fe2898bf33a79fad29b470e04fb2252aea07`) records a verified manifest, clean working tree, seven matching checked source blobs, and 0 heuristic findings across 858 reachable commits / 822 unique blobs. The limited scanner does not prove that sensitive data was never exposed. PR #21's branch CI also passed 249 tests and verified the calibration uncertainty code; full-cohort artifact validation remains pending. PR #22, merged as `4ce19fd6cdab24a2081474f41fba515220b24101`, adds strict checks that the full-cohort aggregate artifact includes valid or explicitly undefined calibration-coefficient intervals, keeps Set B evaluation-only and excludes row-level predictions. Its standard and dashboard branch CI both passed (16/16 steps each: [#39019540766](https://github.com/culprit-k/VITALIS/actions/runs/39019540766), [#39019558153](https://github.com/culprit-k/VITALIS/actions/runs/39019558153)). PR #23, merged as `b8cf6320317f90f156a0fa24100e781df2f3ef8f`, extends calibration-interval checks to all three declared models; standard/dashboard CI both passed 16/16 steps ([#39020467567](https://github.com/culprit-k/VITALIS/actions/runs/39020467567), [#39020476558](https://github.com/culprit-k/VITALIS/actions/runs/39020476558)). The active run #39019018791 started before both guards and requires manual artifact review.
- [x] Full Set A/Set B workflow completed on PR head `e2e14a6665f9c76c9f83e12f0147cabbd91f4eb1` (subsequently merged in PR #17): [run #39008672530](https://github.com/culprit-k/VITALIS/actions/runs/39008672530); inspected [aggregate-only artifact](https://github.com/culprit-k/VITALIS/actions/runs/39008672530/artifacts/12093581980) (`vitalis-clean-checkout-reproduction-e2e14a6665f9c76c9f83e12f0147cabbd91f4eb1`, 216,801 bytes; SHA-256 `70131b576e82da3493edf87099f04fca3f20492ad5dab2ed3535435288bab660`). Artifact includes aggregate metrics, cohort/source fingerprints, cache-integrity summaries, environment/source manifests, calibration, physiology ablation, threshold sweep, and reconciliation; no raw cohort files, feature caches, patient identifiers, or row-level predictions are reported as included. This is not a rerun on the latest `main` documentation commit.
- [x] Cohort-count and cache-integrity audits passed in run #39008672530: Set A 20,336 patients / 790,215 rows; Set B 20,000 / 761,995; zero malformed rows, nonbinary labels, or label reversions; patient blocks contiguous and lengths consistent. Set B remained evaluation-only; see the artifact and [execution report](https://github.com/culprit-k/VITALIS/blob/main/docs/MAIN_BRANCH_FULL_COHORT_REPRODUCTION_2026-10-16.md).
- [x] Frozen-baseline reconciliation passed in run #39008672530: 42/42 metric mean/sample-SD pairs and 84/84 scalar values matched at six decimal places; zero mismatches. Independent review is still required; the historical baseline was not overwritten.
- [ ] Probability-quality gate remains partial. Existing retrospective reports compare Brier/log loss with a constant-prevalence reference, report reliability bins/ECE, and patient-cluster uncertainty for Brier/log loss/ECE. PR #19 added calibration intercept/slope point diagnostics; PR #21 added patient-cluster sandwich standard errors and asymptotic 95% intervals with explicit undefined states for non-identifiable fits. The new fields are now in `main`, but the latest full-cohort artifact has not yet been produced and inspected with them; no clinically usable probability model is established, and independent review remains required.
- [ ] New operating-point development must use patient-disjoint Set A development data only. Set B has already been examined in historical exploratory analyses and must never be reused for further threshold, calibration, feature, or model selection. Any final frozen policy needs evaluation on a genuinely new independent cohort; Set B is not prospective validation.
- [x] The adaptive twin and supervised forecast are separate outputs: `src/vitalis/integrated_inference.py` keeps their contracts distinct, and `tests/test_integrated_inference.py` verifies that the twin heuristic is not the supervised probability and that missing predictors remain unavailable.
- [x] Synthetic-stream and input-validation coverage is present in `tests/test_stream.py` and `tests/test_adaptive_twin.py`: units, timezone-aware timestamps, stale/future/out-of-order samples, reset and patient-state isolation, flatlines, and gradual shifts have regression tests. This is software-level synthetic coverage, not sensor/device validation.
- [x] Aggregate-only dashboard behavior is implemented in `dashboard/app.py` and covered by `tests/test_reporting.py`; the inspected full-cohort artifact contains aggregate metrics and provenance, not raw cohort files, feature caches, patient identifiers, or row-level predictions.
- [x] Model card, data provenance, limitations, reproducible run commands, and artifact checksums are documented in `docs/MODEL_CARD.md`, the clean-checkout report/runbook, the README, and this gate.
- [ ] PR review completed; release tag only after the checks above pass.

## What the prototype can output

1. **Supervised retrospective forecast:** estimates the probability of entering the PhysioNet/CinC Challenge 2019 SepsisLabel-positive window within 1, 3, or 6 hours, conditional on the trained model and observed features. This is not an independently adjudicated biological sepsis-onset probability.
2. **Adaptive physiological twin:** per-channel robust deviations, multisystem deviation heuristic, persistence/CUSUM state, coverage, data-quality flags, and trajectory direction/score after warm-up. It is not calibrated and does not provide clinical risk probability or time-to-deterioration.
3. **Research evaluation:** discrimination, proper scoring rules, calibration diagnostics, fixed-reference threshold metrics, patient-level alert burden, and patient-cluster uncertainty where implemented.

## Explicitly not part of software completion

- Real sensor/hardware integration or device validation.
- Independent external cohort validation, prospective silent-mode validation, clinical-impact testing, or regulatory clearance.
- A claim that VITALIS diagnoses sepsis or safely guides patient care.
- A claim of patentability or clinical superiority.

## Fast, safe execution order

1. Run unit tests and lint/hygiene checks first; fix cheap failures before expensive cohort runs.
2. Run the full pinned Python 3.11 cohort experiment once; retain aggregate logs and artifact checksums.
3. Inspect failures from the first failing step; do not rerun the full cohort for a syntax/import/unit-test error.
4. Once it completes, validate artifact schema, counts, splits, aggregate-only output, and baseline provenance.
5. Resolve probability quality using development-only data and the frozen Set B protocol.
6. Publish a release candidate with a complete runbook and remaining evidence gaps. If a gate fails, label the candidate unreleased rather than changing the gate.

## Research safety

VITALIS is a research prototype, not a medical device or clinically validated decision-support system. Do not use its outputs for diagnosis, triage, treatment, or patient-care decisions.
