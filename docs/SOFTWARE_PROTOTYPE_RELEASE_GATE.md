# VITALIS software research prototype: release gate

**Purpose:** a time-boxed checklist for producing a reproducible, auditable research prototype. A deadline does not waive evidence requirements.

## Release definition

The software research prototype is releasable only when the following are true:

- [ ] Clean-checkout installation works from the documented pinned environment.
- [x] Unit, integration, and repository-hygiene tests pass on commit `f21e0563ca4ee4cdb961ca4f4950de400437ac47`: [GitHub Actions run #39014090824](https://github.com/culprit-k/VITALIS/actions/runs/39014090824) succeeded; all 243 tests passed. The run uploaded [source/history audit artifact](https://github.com/culprit-k/VITALIS/actions/runs/39014090824/artifacts/12093623017) (`vitalis-source-audit-f21e0563ca4ee4cdb961ca4f4950de400437ac47`, 1,715 bytes; SHA-256 `c60823982f5e90619ca48f768c1fc732827825b4204ecffe669a9c5bd2b8610c`). This is an audit-manifest artifact, not the full-cohort aggregate-results artifact. It does not establish CI for later documentation-only commits.
- [x] Full Set A/Set B workflow completed on PR head `e2e14a6665f9c76c9f83e12f0147cabbd91f4eb1` (subsequently merged in PR #17): [run #39008672530](https://github.com/culprit-k/VITALIS/actions/runs/39008672530); inspected [aggregate-only artifact](https://github.com/culprit-k/VITALIS/actions/runs/39008672530/artifacts/12093581980) (`vitalis-clean-checkout-reproduction-e2e14a6665f9c76c9f83e12f0147cabbd91f4eb1`, 216,801 bytes; SHA-256 `70131b576e82da3493edf87099f04fca3f20492ad5dab2ed3535435288bab660`). Artifact includes aggregate metrics, cohort/source fingerprints, cache-integrity summaries, environment/source manifests, calibration, physiology ablation, threshold sweep, and reconciliation; no raw cohort files, feature caches, patient identifiers, or row-level predictions are reported as included. This is not a rerun on the latest `main` documentation commit.
- [x] Cohort-count and cache-integrity audits passed in run #39008672530: Set A 20,336 patients / 790,215 rows; Set B 20,000 / 761,995; zero malformed rows, nonbinary labels, or label reversions; patient blocks contiguous and lengths consistent. Set B remained evaluation-only; see the artifact and [execution report](https://github.com/culprit-k/VITALIS/blob/main/docs/MAIN_BRANCH_FULL_COHORT_REPRODUCTION_2026-10-16.md).
- [x] Frozen-baseline reconciliation passed in run #39008672530: 42/42 metric mean/sample-SD pairs and 84/84 scalar values matched at six decimal places; zero mismatches. Independent review is still required; the historical baseline was not overwritten.
- [ ] All probability models are compared to prevalence-only baselines; calibration is reported with Brier score, log loss, calibration intercept/slope, reliability bins, and uncertainty.
- [ ] Operating-point selection uses Set A development patients only. Set B is evaluated once after decisions are frozen; no Set B threshold, calibration, or model selection.
- [ ] The adaptive twin and the supervised forecast are shown as separate outputs. A twin deviation score is not a probability of sepsis.
- [ ] Synthetic-stream and input-validation tests cover units, timestamps, missing/stale data, out-of-order samples, reset/patient isolation, flatlines, and gradual shifts.
- [ ] Dashboard accepts aggregate metrics only; no raw patient data, patient IDs, row-level predictions, or caches are included in release artifacts.
- [ ] Model card, data provenance, limitations, run commands, and artifact checksums are included.
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
