# VITALIS software research prototype: release gate

**Purpose:** a time-boxed checklist for producing a reproducible, auditable research prototype. A deadline does not waive evidence requirements.

## Release definition

The software research prototype is releasable only when the following are true:

- [x] Clean-checkout installation and pinned dependency assertions passed on attempt 3 of the current-main code-snapshot rerun [#39016343505](https://github.com/culprit-k/VITALIS/actions/runs/39016343505), source commit `3667c9983f7e2a78951a824d6c4a5f4df5694ee5`; the full-cohort run is still in progress, so this does not mark the reproduction gate passed.
- [x] Standard CI passed on main commit `efd2f5c526ad47bda2ea186bed0e4335d650906e`: [run #39017827225](https://github.com/culprit-k/VITALIS/actions/runs/39017827225) succeeded with 243 tests passed and installation, source-manifest, repository/history hygiene, and synthetic smoke steps passing. On the immediately preceding code-bearing main snapshot, [standard CI #39017440249](https://github.com/culprit-k/VITALIS/actions/runs/39017440249) and [dashboard CI #39017440309](https://github.com/culprit-k/VITALIS/actions/runs/39017440309) both passed using Actions v7; dashboard compile, lint, and 243 tests passed. Its [source/history audit artifact #12095516040](https://github.com/culprit-k/VITALIS/actions/runs/39017440249/artifacts/12095516040) has SHA-256 `d2899ee1a1a06428fa1dd1809ca69d688ba07721c3eb3729ba06afd107f0c60f`; the source manifest says `verified: true`, clean working tree and seven checked source blobs matched, while the heuristic history scanner reported 0 findings across 842 commits / 809 unique blobs. This scanner does not prove that sensitive data was never exposed.
- [x] Full Set A/Set B workflow completed on PR head `e2e14a6665f9c76c9f83e12f0147cabbd91f4eb1` (subsequently merged in PR #17): [run #39008672530](https://github.com/culprit-k/VITALIS/actions/runs/39008672530); inspected [aggregate-only artifact](https://github.com/culprit-k/VITALIS/actions/runs/39008672530/artifacts/12093581980) (`vitalis-clean-checkout-reproduction-e2e14a6665f9c76c9f83e12f0147cabbd91f4eb1`, 216,801 bytes; SHA-256 `70131b576e82da3493edf87099f04fca3f20492ad5dab2ed3535435288bab660`). Artifact includes aggregate metrics, cohort/source fingerprints, cache-integrity summaries, environment/source manifests, calibration, physiology ablation, threshold sweep, and reconciliation; no raw cohort files, feature caches, patient identifiers, or row-level predictions are reported as included. This is not a rerun on the latest `main` documentation commit.
- [x] Cohort-count and cache-integrity audits passed in run #39008672530: Set A 20,336 patients / 790,215 rows; Set B 20,000 / 761,995; zero malformed rows, nonbinary labels, or label reversions; patient blocks contiguous and lengths consistent. Set B remained evaluation-only; see the artifact and [execution report](https://github.com/culprit-k/VITALIS/blob/main/docs/MAIN_BRANCH_FULL_COHORT_REPRODUCTION_2026-10-16.md).
- [x] Frozen-baseline reconciliation passed in run #39008672530: 42/42 metric mean/sample-SD pairs and 84/84 scalar values matched at six decimal places; zero mismatches. Independent review is still required; the historical baseline was not overwritten.
- [ ] All probability models are compared to prevalence-only baselines; calibration is reported with Brier score, log loss, calibration intercept/slope, reliability bins, and uncertainty.
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
