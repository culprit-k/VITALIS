# VITALIS software research prototype: release gate

**Purpose:** a time-boxed checklist for producing a reproducible, auditable research prototype. A deadline does not waive evidence requirements.

## Release definition

The software research prototype is releasable only when the following are true:

- [ ] Clean-checkout installation works from the documented pinned environment.
- [x] Unit, integration, and repository-hygiene tests pass on commit `f21e0563ca4ee4cdb961ca4f4950de400437ac47` (GitHub Actions `tests #1376`, successful; [workflow page](https://github.com/culprit-k/VITALIS/actions/workflows/tests.yml)). This check does not establish that the later documentation-only commit has its own CI run.
- [ ] The full Set A/Set B workflow completes and emits a validated aggregate artifact.
- [ ] Cohort counts, patient-disjoint splits, label/horizon alignment, and data leakage checks pass.
- [ ] Historical baseline discrepancies are resolved by source-level evidence, or explicitly remain open while a separately versioned clean-checkout reference is independently repeated and reviewed. The historical baseline is never overwritten.
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
