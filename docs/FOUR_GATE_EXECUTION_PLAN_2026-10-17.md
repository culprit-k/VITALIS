# VITALIS four-gate execution plan

**Status date:** 17 October 2026  
**Scope:** research software and non-clinical bench planning only. This document does not certify clinical validity, ethics approval, regulatory status, or hardware safety.

## Evidence checkpoint — 17 October 2026

- **Gate 1 extended evaluation:** passed on source commit `df99be7b1400c508e75b7e1e8e66077d6dabe6f7` in [run #39029868475, attempt 2](https://github.com/culprit-k/VITALIS/actions/runs/39029868475). The workflow verified the preserved evaluator blob, ran the full predeclared 1/3/6-hour × three-seed evaluation, physiology ablation, patient-disjoint Set A calibration, Set A-only threshold sweep, aggregate-only checks, and strict reconciliation. The result was 42/42 mean/sample-SD pairs and 84/84 scalar matches, zero mismatches, using the unchanged six-decimal rule. Artifact: [#12102345008](https://github.com/culprit-k/VITALIS/actions/runs/39029868475/artifacts/12102345008), SHA-256 `ea8312843827ee875371f92020deb7275d677ebc2dd36864d86bcb437f2e0fa5`. The later main commit `ef22ef2` adds the synthetic bench harness and docs/tests only; the evaluator and cohort-analysis implementation were not changed.
- **Gate 3 software replay:** [PR #27](https://github.com/culprit-k/VITALIS/pull/27) merged as `ef22ef2da4c1680da75bca2161043ce9b72fb45c`. [CI run #39035622219](https://github.com/culprit-k/VITALIS/actions/runs/39035622219) passed all 10 synthetic functional checks on 1,000 frames; p95 latency 0.3571 ms and throughput 4,917.8 frames/s on a GitHub-hosted runner. This is software replay only, not physical hardware-in-the-loop testing.
- **Gate 2 remains open** until a qualified independent clinician/statistician/methods reviewer provides written findings.
- **Gate 3 remains open** until the intended bench computer is measured and the physical dummy-load/disconnect/recovery and applicable engineering-safety reviews are completed.
- **Gate 4 remains open** until external-cohort access and protocol, institutional/ethics/privacy/security determinations, and relevant safety/regulatory governance are documented.

Do not infer clinical utility from these retrospective benchmark or synthetic software results.

## Gate 1 — Extended full-cohort evaluation on the current source

The strict clean-checkout run #39024691664 passed the core Set A-to-Set B reproduction and the unchanged 42-pair / 84-scalar six-decimal reconciliation. That workflow explicitly skipped physiology ablation, Set A Platt calibration, threshold sweep, and the probability-quality artifact checks. Do not describe those extended analyses as verified by the core run.

### Required execution
1. Run `.github/workflows/full-cohort-reproduction.yml` with `run_extended_analyses=true` against the exact current `main` commit. Use the workflow dispatch input, not a modified threshold, baseline, or tolerance.
2. Confirm the run source SHA is the reviewed `main` SHA and the evaluator source blob still matches the preserved baseline provenance.
3. Require all existing source/environment checks, official cohort counts, fresh caches, all nine horizon × seed evaluations, physiology ablation, Set A-only Platt calibration, Set A-only threshold sweep, calibration point/cluster uncertainty diagnostics, aggregate-only assertions, and the six-decimal baseline reconciliation to pass.
4. Inspect the retained artifact. It must contain aggregate metrics and provenance only, with no raw records, caches, patient identifiers, or row-level predictions.
5. If any step fails, preserve the artifact/logs, record the exact failing step and commit, and investigate without relaxing checks or using Set B for model/threshold/calibrator selection.

### Acceptance evidence
- Run URL, source SHA, workflow conclusion, artifact ID and SHA-256.
- 42/42 baseline mean/sample-SD pairs and 84/84 scalar matches for the core reproduction.
- Extended analyses and artifact guards all passed on that same source snapshot.
- Explicit Set B evaluation-only declaration and no patient-level output.
- Interpretation report with no claim of clinical utility or independently observed onset.

## Gate 2 — Independent scientific review

This gate cannot be self-certified by the project author or by the person who produced the run. Invite an independent clinician/statistician or methods reviewer who has not authored the analysis. Obtain written findings and permission before publishing their identity or affiliation.

Reviewer checklist:
- Dataset provenance, source hashes, environment and fresh-cache reproducibility.
- Patient-disjoint fitting/calibration/threshold partitions; preprocessing fit only on training partitions.
- Set B never used for feature/model/calibrator/threshold selection.
- Challenge label semantics and the six-hour lead convention; targets are entry into the challenge-positive window, not independently adjudicated biological onset.
- Discrimination, calibration intercept/slope and uncertainty, prevalence/domain shift, warning burden, alert refractory rules, missingness, and patient-cluster uncertainty estimands.
- Reconciliation against the frozen baseline and whether any proposed new baseline requires a separately reviewed, provenance-complete process.
- Limitations and acceptable wording for a research-only release.

Record the reviewer’s scope, date, conflicts/independence statement, written sign-off or blocking findings, and any remediation. Do not record personal details without consent. A passing CI run is not a substitute for this review.

## Gate 3 — Synthetic/replay hardware bench only

No human connection, clinical sensor deployment, treatment influence, or patient-care use is authorized by this plan. Start with generated/replayed signals and an electrical dummy load; do not purchase components until the architecture and data dictionary are explicitly frozen.

### Bench test sequence
1. Freeze a versioned interface contract: channel names, units, allowed ranges, timestamp/timebase, source identifier, quality flags, missingness semantics, and schema version.
2. Use synthetic signals with known timestamps and planted cases: stable baseline, gradual drift, abrupt step, isolated spike, channel dropout, stale samples, out-of-order samples, unit mismatch, non-finite values, reset/reconnect, and source replacement.
3. Verify invalid/stale/out-of-order data are rejected or flagged; reset prevents state leakage across sessions; poor-quality or missing channels do not silently become normal measurements.
4. Measure end-to-end ingestion-to-output latency, throughput, memory use, restart recovery, and deterministic replay consistency. Report measured values and test conditions rather than assumed specifications.
5. Test alarms/notifications only as simulated outputs. Document rate limiting, duplicate suppression, fault behavior, and safe default behavior when inputs or inference are unavailable.
6. For any future physical electronics, obtain qualified biomedical/electrical safety review for isolation, leakage, power, enclosure, EMC, cybersecurity, and applicable regulatory requirements before human contact.

### Bench acceptance evidence
- Frozen architecture/data dictionary revision and reviewer.
- Synthetic/replay test cases and expected outputs.
- Test log with pass/fail, latency measurements, dropout/recovery results, and known limitations.
- No patient data and no claims that synthetic tests establish clinical performance.

## Gate 4 — Independent-cohort and governance plan

The current Challenge Set B is not an external clinical cohort. Before any new cohort is accessed or any prospective activity begins, obtain written institutional and competent-authority determinations covering research ethics, data access, privacy/data protection, security, and device/regulatory classification as applicable. This plan is not legal advice or approval.

### Staged path
1. Define intended research use, population, setting, data elements, event definition, primary endpoint, exclusions, missing-data handling, and analysis plan before data access.
2. Identify a genuinely independent retrospective cohort with an independently defined/adjudicated event time. Confirm lawful access, data-controller/processor roles, de-identification/pseudonymization, transfer/storage controls, retention, and permitted uses in writing.
3. Freeze code, features, model, calibration, threshold policy, and statistical analysis plan before evaluating the external cohort. Keep the external cohort untouched until the protocol is approved.
4. Predefine performance and uncertainty reporting: discrimination, calibration, sensitivity/PPV, alert burden, lead-time definition, subgroup/missingness analysis, failure handling, and go/no-go criteria agreed by independent clinical/statistical reviewers.
5. Consider prospective silent-mode evaluation only after all required ethics, privacy, institutional, safety and regulatory approvals. No output may influence care during silent mode.
6. Require separate approval and evidence before any clinician-facing use, interventional study, or marketing claim.

### Gate closure
Gate 4 remains open until the required approvals and independent-cohort protocol are documented. Do not imply that a plan equals permission, that Set B is independent clinical validation, or that retrospective benchmark results demonstrate patient benefit.

## Overall release rule

All four gates are separate. Passing software CI or reproducing benchmark aggregates does not close independent review, hardware safety, external validation, or governance. VITALIS remains a research prototype and must not be used to guide diagnosis, triage, treatment, or patient care.
