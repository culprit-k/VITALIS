# VITALIS research-release readiness audit

**Audit date:** 14 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Pull request:** [#1 — Source-verify cross-cohort recalibration and document reproduction](https://github.com/culprit-k/VITALIS/pull/1)  
**Audited head at time of review:** `b12adb5a52784633e21de24a208a0164c97faf25`

## Purpose and release boundary

This checklist assesses readiness for a **research-code release**, not for clinical deployment. VITALIS remains a research prototype. The benchmark results do not establish prospective clinical validity, clinical utility, patient benefit, or a clinically appropriate alert threshold.

## Findings

| Gate | Status | Evidence / remaining work |
|---|---|---|
| Pull request state | Open draft; unmerged | PR #1 is mergeable according to GitHub, but has 90 commits and 34 changed files relative to `main`. Keep it draft until the remaining review gates are satisfied. |
| Automated tests | Pass on audited head | GitHub Actions run [38606955158](https://github.com/culprit-k/VITALIS/actions/runs/38606955158) completed successfully; install and test steps both passed. This confirms the workflow on GitHub's clean runner, not a local full-cohort reproduction. |
| Bootstrap implementation | Pass within documented scope | The accelerated runner has focused tests and synthetic tied-score comparisons; the 1,000-replicate aggregate report documents comparison against the baseline implementation. |
| Set-B isolation | Documented | The protocol states Set B is evaluation-only. No Set-B fitting, feature selection, calibration fitting, or threshold tuning is claimed. Keep this restriction explicit in future experiments. |
| Data/privacy boundary | Path-level review passed | The 34-file PR diff consists of source, tests, docs, workflow configuration, and aggregate JSON. No raw patient files, local cache arrays, or row-level NPZ score archives appear in the changed-file list. This is a changed-path audit, not a substitute for a full repository history/secret scan. |
| Exact source identity | Partial pass | Relevant checked-in source blobs were compared by SHA. The documented full clean-clone/reproduction procedure has **not** been completed in the runtime because GitHub DNS resolution failed. |
| Historical metric discrepancy | Explicitly unresolved | The reconstructed-harness artifact differs from the exact-source evaluator. Historical results are preserved; available provenance is insufficient to assign a root cause. Do not guess or silently overwrite either artifact. |
| Feature-coverage policy | Review required | The 5% Set-A training coverage rule is exploratory, not clinically justified or established as optimal. Do not promote it to the default without an independently justified, frozen protocol. |
| Independent statistical/clinical review | Pending | No submitted PR reviews or inline review threads were present at audit time. Request a qualified independent review of split/label semantics, calibration interpretation, feature-availability/domain shift, bootstrap estimand, and release claims. |
| Final merge/release decision | Not ready yet | Finish the clean-checkout reproduction and independent review, address review findings, rerun CI on any code changes, and re-audit the diff before deciding whether to mark the PR ready or merge. No merge is authorized by this checklist. |

## Required next actions

1. **Clean-checkout reproduction:** On a machine with GitHub network access and authorized local copies of the benchmark data, follow [the reproduction runbook](EXACT_CHECKOUT_REPRODUCTION.md) from a fresh clone. Record checkout SHA, source blob SHAs, Python/dependency versions, test summary, commands, cohort totals, and per-seed metric reconciliation. Keep caches, logs containing row-level information, and score archives outside Git.
2. **Independent methods review:** Ask a statistician/clinical informatician familiar with retrospective ICU prediction to review the protocol and reports. At minimum, ask them to assess patient-level splitting, repeated hourly labels and within-patient dependence, calibration claims, cohort/domain shift, the exploratory feature threshold, and what can/cannot be inferred from the bootstrap intervals.
3. **Historical discrepancy:** Keep the discrepancy labelled unresolved unless the original harness/environment/split provenance can be recovered.
4. **Privacy/security check:** Before release, review the full proposed diff and repository history for accidentally committed sensitive data, credentials, or local artifacts. The current changed-path audit alone does not prove the full history is clean.
5. **Final PR gate:** Resolve review comments, run CI on the final code-bearing commit, update the PR summary if evidence changes, then make an explicit ready-for-review/merge decision. Keep the PR draft and unmerged until that decision.

## Release claims permitted at this stage

- A retrospective, patient-cluster bootstrap analysis has been recorded for three Set-A split seeds and raw/Platt-recalibrated scores on the fixed Set-B benchmark cohort.
- Temporal features had higher AUROC and AUPRC than static features in the reported split-specific comparisons; this is benchmark evidence, not clinical validation.
- Reproducibility is improved through source-hash records, tests, aggregate reports, and a documented clean-checkout procedure.

## Claims not supported

- Prospective or independent real-world clinical validation.
- Clinical utility, patient benefit, or readiness for diagnosis, triage, treatment, or patient-care decisions.
- An optimal/clinically justified 5% feature-coverage cutoff.
- A known cause for the historical metric discrepancy.
- A completed clean full-cohort reproduction from a fresh clone.

**Decision:** Continue toward a research-code release after the two principal blockers—clean-checkout reproduction and independent review—are addressed. Do not merge this draft pull request based on CI success alone.

## Follow-up checkpoint: utility operating-point analysis (15 October 2026)

- [x] Reviewed the checked-in utility function and its integration in `scripts/evaluate_horizon_calibration.py`. Candidate rankings are computed on the patient-disjoint Set-A operating-point holdout; Set B is not passed to the utility ranking function.
- [x] Confirmed the framework reports row-level sensitivity/PPV alongside patient-level alerts per at-risk patient-day, covered/missed future-positive windows, window coverage, and label-relative warning time.
- [x] Reviewed the cost formula: each missed future-positive window and each generated alert is assigned an explicit relative cost, with the total normalized by eligible at-risk patient-days. The ratios remain illustrative assumptions, not clinician- or patient-elicited costs. They do not account for alarm fatigue, treatment harms, staffing, delayed treatment, patient preferences, or competing outcomes.
- [x] Reviewed the aggregate report and provenance statement. Full-cohort utility results came from a reconstructed local working copy; they are **not** claimed as byte-identically verified execution of the current GitHub source. The utility-focused reruns used 20 bootstrap replicates for ancillary uncertainty summaries; the deterministic cost ranking does not use those intervals.
- [x] GitHub Actions passed on the current post-cleanup PR head `a179ed437868a92ad89b4b74a1177c899f492cf2` (run [38629062663](https://github.com/culprit-k/VITALIS/actions/runs/38629062663)). This is code/test validation, not a clean full-cohort reproduction or external validation.
- [x] Prepared an [independent utility-cost review checklist](UTILITY_COST_REVIEW_CHECKLIST.md) covering label semantics, split discipline, cost elicitation, burden metrics, uncertainty, and governance.
- [ ] Obtain an independent qualified clinical/statistical review using that checklist before any policy choice. No threshold or model is endorsed.
- [ ] Complete the clean-checkout reproduction and history-wide privacy/security review; neither is closed by this follow-up.
- [ ] Any frozen policy needs evaluation on a new independent cohort. Set B has already been inspected and must not be reused for threshold selection.
- [ ] Keep PR #1 draft and unmerged until the outstanding reproduction and independent-review gates are addressed.

**Conclusion:** the utility framework is implemented and tested as a research sensitivity-analysis tool. Clinical utility, an appropriate cost ratio, and a clinically acceptable alert threshold remain unestablished.


## Follow-up checkpoint: automated history audit (15 October 2026)

- [x] Verified the current workflow checks out full history, runs current-tree artifact hygiene, and executes the reachable-history scanner. The current PR-head run [38634604467](https://github.com/culprit-k/VITALIS/actions/runs/38634604467) passed, including **164 tests**.
- [x] The history-audit step returned success with no matches for the scanner's configured forbidden data-artifact paths, oversized blobs, or high-confidence credential patterns across the refs scanned by CI.
- [x] The run validates the automation and current scanned history only. It does not prove that no sensitive information was ever exposed, does not replace provider secret scanning, and depends on which refs were fetched.
- [ ] Complete a clean local checkout and fresh-cache full-cohort reproduction. An attempted clone in the current runtime failed because github.com could not be resolved; the CI checkout is not a substitute for reproducing the official-cohort analysis from a fresh local cache.
- [ ] Obtain independent clinical/statistical review of label semantics, cost scenarios, calibration interpretation, and any proposed frozen policy. A new independent cohort and applicable governance/ethics approvals are required before external or prospective evaluation.

**Decision remains unchanged:** research-code gates are improving, but clean-checkout reproduction and independent review remain open. Keep PR #1 draft and unmerged; do not interpret CI success as clinical validation.


## Follow-up checkpoint: utility bootstrap and current CI (15 October 2026)

- [x] Completed the Set-A-only utility-bootstrap uncertainty run: 9 seed × horizon runs, 18 static/temporal model fits, 200 patient-cluster replicates per fit (3,600 total), 151.741 seconds summed runtime, and zero captured fit warnings.
- [x] Added [utility bootstrap results](HORIZON_UTILITY_BOOTSTRAP_RESULTS_2026-10-15.md) and [aggregate-only summary](../results/horizon_utility_bootstrap_summary_2026-10-15.json). Set B was not loaded or used in this run; no row-level predictions were committed.
- [x] Recorded the reconstructed local runner/module/cache-metadata SHA-256 values and environment versions. This improves traceability but does **not** establish byte-identical execution of checked-in source.
- [x] Verified GitHub Actions on code-bearing PR head 86776762479dd450e20821da8e6f0b50c482e21d (run [38639673606](https://github.com/culprit-k/VITALIS/actions/runs/38639673606)): 170 tests passed, compile succeeded, repository-artifact hygiene passed, and the synthetic stream smoke test passed.
- [x] The reachable-history scanner reported zero configured-pattern findings across 563 commits and 544 unique blobs in the refs fetched by that CI run. This is a heuristic scan of fetched refs, not proof that sensitive data was never exposed; independent provider secret scanning and manual triage remain appropriate.
- [x] The available reconstructed local suite passed 28 tests with \`PYTHONPATH=src\`; the aggregate-only output was schema-checked and verified to contain 9 runs, 18 fits, 3,600 replicates, zero fit warnings, and no Set-B use.
- [ ] Complete a clean local checkout and fresh-cache full-cohort reproduction. Runtime DNS/network failure still prevents this; the CI checkout does not substitute for reproducing official-cohort results from fresh local caches.
- [ ] Obtain independent qualified clinical/statistical review of target semantics, cost assumptions, calibration, and alert burden. No clinical threshold is approved.
- [ ] Obtain applicable governance/ethics and data-protection determinations and a genuinely new independent cohort with independently defined/adjudicated event timing before external or prospective evaluation.

**Decision:** the software and automated repository gates have advanced, but clean-checkout reproducibility, independent review, independent-cohort evaluation, and governance remain open. Keep PR #1 draft and unmerged. VITALIS remains research-only and must not guide patient care.
