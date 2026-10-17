# VITALIS four-gate execution plan

## Latest strict full-cohort retry — PASS (17 October 2026)

- **Source commit tested:** `2f14fb556981645d79642ed30a2a964ecadc5ffa` (the documentation-only parent immediately before PR #31 and PR #32; the evaluator and experiment code were unchanged by those later documentation merges).
- **Workflow:** [#39048849550, attempt 3](https://github.com/culprit-k/VITALIS/actions/runs/39048849550), all 30 steps passed after two earlier attempts correctly failed closed because the hosted runner did not expose AVX-512F. Attempt 3 used a compatible runner; no evaluator or tolerance was changed.
- **Standard CI on the tested source commit:** [#39048849554](https://github.com/culprit-k/VITALIS/actions/runs/39048849554), passed.
- **Retained artifact:** [#12109506730](https://github.com/culprit-k/VITALIS/actions/runs/39048849550/artifacts/12109506730), 230,270 bytes, expires 16 November 2026 at 17:51:59 UTC. ZIP SHA-256 verified locally and matches GitHub's digest: `065c56393492c2b549eb6bd6b70663dbef47a157d7dd073ef9b4bb0434fa4948`.
- **Frozen reconciliation:** PASS; 42/42 metric mean/sample-SD pairs and 84/84 scalar values matched after rounding to the unchanged six-decimal rule; zero mismatches.
- **Cohort audits:** Set A 20,336 patients / 790,215 hourly rows / 17,136 positive labels; Set B 20,000 / 761,995 / 10,780. No malformed rows, nonbinary labels, or label reversions.
- **Scope:** 1/3/6-hour horizons, seeds 42/123/2026, static and temporal models, patient-cluster bootstrap (200 replicates), physiology ablation, patient-disjoint Set A calibration, Set A-only threshold sweep, cache integrity, and aggregate-only artifact checks completed. Set B remained evaluation-only.
- **Artifact contents inspected:** aggregate report and metrics, cohort/source manifests, fingerprints, cache-integrity summaries, reconciliation, calibration/threshold aggregate diagnostics, and protocol files; no raw cohort files, feature-cache arrays, patient identifiers, or row-level predictions were included.
- **Interpretation:** Set B is another Challenge training cohort, not external clinical validation. At 1/3/6 hours the temporal model does not outperform the static baseline on AUROC/AUPRC in these results; PPV remains very low. The target is entry into the Challenge `SepsisLabel` positive window, not independently adjudicated sepsis onset. This remains retrospective software reproduction, not clinical validation.

**Current branch note:** PR #31 and PR #32 subsequently merged documentation-only changes into `main`; their standard CI passed. The latest `main` commit is `7c4affe0913d13dadb5a37e1dd35666e9a9dbb97`. A fresh strict reproduction on that exact documentation-only tip has not yet been run, so the run above is not mislabelled as testing that later SHA.

---

## Exact post-merge reproduction — PASS (17 October 2026)

- **Current main commit tested:** `eefad3664019a690c4520986875e05a9c9fe0b6f`.
- **Strict full-cohort run:** [#39041430942](https://github.com/culprit-k/VITALIS/actions/runs/39041430942), all 30 workflow steps passed.
- **Standard CI:** [#39041430943](https://github.com/culprit-k/VITALIS/actions/runs/39041430943), passed on the same commit.
- **Aggregate/provenance artifact:** [#12105668062](https://github.com/culprit-k/VITALIS/actions/runs/39041430942/artifacts/12105668062), 230,276 bytes; expires 16 November 2026 at 15:51:36 UTC. ZIP SHA-256: `df475890f4671b215a1b3fa25e0affa34cd7b078f23c110b20104c974379f245` (matches the GitHub artifact digest).
- **Frozen reconciliation:** PASS; 42/42 mean/sample-SD pairs and 84/84 scalar values matched at the unchanged six-decimal rule, with zero mismatches.
- **Scope:** official Set A/Set B audits, fresh feature caches, nine predeclared 1/3/6-hour × three-seed evaluations, physiology ablation, patient-disjoint Set A calibration, Set A-only threshold sweep, aggregate-only checks, and provenance retention passed. Set B remained evaluation-only.
- **Artifact inspection:** aggregate reports, manifests, fingerprints and protocols only; no raw cohort files, feature-cache files, patient identifiers, or individual predictions found.
- **Scientific boundary:** Set B is a Challenge benchmark cohort, not genuinely external clinical validation. The prediction target is entry into the Challenge `SepsisLabel` positive window, not independently adjudicated sepsis onset. Retrospective reproduction is not clinical validation; independent review, physical bench/safety work, and external-cohort/governance work remain open.

---

**Status date:** 17 October 2026  
**Scope:** research software and non-clinical bench planning only. This document does not certify clinical validity, ethics approval, regulatory status, or hardware safety.

## Evidence checkpoint — 17 October 2026

- **Fresh exact-current-main Gate 1 rerun passed:** [run #39036226875, attempt 2](https://github.com/culprit-k/VITALIS/actions/runs/39036226875) on `0ff7d98e2b83a5b09c78e70f56ec067145f931e1`; all 30 steps passed. [Aggregate/provenance artifact #12104191016](https://github.com/culprit-k/VITALIS/actions/runs/39036226875/artifacts/12104191016), 230,027 bytes, SHA-256 `7239edbab428cd0efb90cef4044566a516ce0923cc126e949ad4fc71f6217940`. Reconciliation passed: 42/42 pairs, 84/84 scalar values, zero mismatches under the unchanged six-decimal rule. Evaluator baseline blob preserved; Set B evaluation-only. This is still retrospective Challenge-label evidence, not clinical validation.


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
