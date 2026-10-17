# VITALIS — project status in plain language

**Status date:** 17 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Verified threshold-sweep merge commit:** `8c5d7b75a653dff7b1af4773a55b663b43c7740f`  
**Latest main CI verification:** [standard tests #39019917810](https://github.com/culprit-k/VITALIS/actions/runs/39019917810) succeeded on main commit `3b9171cbd5a3f3321cb5e6581f4ce6fe3ec9e7df`; all 16 job steps passed. This checks the release-gate progress documentation only. The latest model/code snapshot still has successful standard CI on `4eb3d15c024b2a1d295f657c2cb96e7eb9ff16bd` ([run #39018965402](https://github.com/culprit-k/VITALIS/actions/runs/39018965402), 249 tests). These software checks are not full-cohort validation or clinical validation.

> **Safety boundary:** VITALIS is a research prototype only. It is not a medical device or a clinically validated sepsis warning system. Do not use outputs to guide diagnosis, triage, treatment, or patient care.

## Current verified state

- **Local software demo:** installation diagnostics and synthetic-only twin / integrated interface smoke tests are included in CI. See the [fast-start guide](FAST_START_RESEARCH_DEMO.md).
- **Input contract:** PR #12 merged as `34cc3620b19db06a4eb60733d68aefb93318fe3a`; the supervised inference interface validates horizon, feature, and predictor output types.
- **Research utility contract:** PR #13 merged as `86bc4732f7ec883c97df0678f5e5690092529adb`; threshold/cost, probability, patient-time, and patient-block validation was tightened. Its CI passed: [PR #13 checks](https://github.com/culprit-k/VITALIS/actions/runs/38906330539).
- **Calibration, workflow guard, and bench architecture (17 October 2026):** PR [#19](https://github.com/culprit-k/VITALIS/pull/19) merged as `cd5dab09b338c2e5bf7dfb926b783ed7e53bfdd6`, adding calibration intercept/slope point diagnostics. PR [#21](https://github.com/culprit-k/VITALIS/pull/21) merged as `4eb3d15c024b2a1d295f657c2cb96e7eb9ff16bd`, adding patient-cluster sandwich standard errors and asymptotic 95% intervals for calibration coefficients, with explicit undefined states for non-identifiable fits; its branch CI passed 249 tests. PR [#22](https://github.com/culprit-k/VITALIS/pull/22) merged as `4ce19fd6cdab24a2081474f41fba515220b24101`, adding full-cohort artifact assertions for these fields, Set B isolation, and absence of row-level prediction fields. PR [#20](https://github.com/culprit-k/VITALIS/pull/20) merged as `7458b1ad7f523ecf7d4b240518528199d7ecb127`, aligning the hardware blueprint to the real stream contract and adding bench-only verification criteria. Calibration diagnostics do not change predictions or thresholds; the latest full-cohort output still needs validation. Hardware remains a proposal, not a frozen BOM or permission to connect to a person.
- **Set A operating-threshold sweep (17 October 2026):** PR [#17](https://github.com/culprit-k/VITALIS/pull/17) was merged as `8c5d7b75a653dff7b1af4773a55b663b43c7740f` after full-cohort run [#39008672530](https://github.com/culprit-k/VITALIS/actions/runs/39008672530) completed the 1/3/6-hour three-seed evaluation, physiology ablation, Set A-only Platt calibration, threshold sweep, aggregate-only integrity checks, and baseline reconciliation. The run matched 42/42 metric mean/sample-SD pairs (84/84 scalar values). This is retrospective research evidence, not clinical validation. The artifact was inspected: [download artifact](https://github.com/culprit-k/VITALIS/actions/runs/39008672530/artifacts/12093581980), 216,801 bytes, SHA-256 `70131b576e82da3493edf87099f04fca3f20492ad5dab2ed3535435288bab660`; its reports show cohort/cache fingerprints, environment/source manifests, calibration, ablation, threshold-sweep outputs, and zero reconciliation mismatches. It reports no raw cohort files, caches, patient identifiers, or row-level predictions. This run was on the PR head later merged as #17, not the latest documentation commit on `main`.
- **Full-cohort reproduction evidence:** the pinned Set A/Set B workflow completed on source commit `426ac5dd2a8076fb192bcebd0b1c8f838bf72906`, with 42/42 metric mean/sample-SD pairs and 84/84 scalar values matching the preserved six-decimal baseline. See [the execution report](MAIN_BRANCH_FULL_COHORT_REPRODUCTION_2026-10-16.md) and [aggregate-only artifact](https://github.com/culprit-k/VITALIS/actions/runs/38889950689/artifacts/12042469450). **This full-cohort result is not yet a run on the current main commit above.**
- **Probability quality:** current calibration analysis does not identify a clinically usable threshold or a model that wins across discrimination, calibration, and alert burden. No Set B tuning is permitted.
- **Privacy:** raw cohort files, caches, patient identifiers, and row-level predictions must stay out of Git and published artifacts.

## Remaining release blockers

1. Latest-code-snapshot full-cohort run [#39019018791](https://github.com/culprit-k/VITALIS/actions/runs/39019018791) is running on temporary trigger-branch commit `424365d0823e58df4d5c6715149cbce26406dc2a`, whose analysis source is based on code commit `4eb3d15c024b2a1d295f657c2cb96e7eb9ff16bd` (PR #21 calibration uncertainty included). Checkout, CPU/backend preflight, pinned dependencies, source manifest, tests, cohort audits, fresh Set A/Set B caches, and the core nine-run horizon evaluation passed; patient-relative physiology ablation is now running. The Set A calibration experiment, threshold sweep, full artifact checks, and strict reconciliation remain pending. The active run predates PR #22's workflow guard, so its retained artifact must be inspected manually.
2. Confirm the run's calibration-uncertainty fields, aggregate-only/privacy checks, and strict 42-pair/84-scalar six-decimal reconciliation. Preserve the historical baseline and tolerance; do not waive any failure. The older snapshot run [#39016343505](https://github.com/culprit-k/VITALIS/actions/runs/39016343505) remains active but does not include the newest calibration uncertainty code.
3. Obtain an independent reviewer’s written assessment of provenance, patient-disjoint splits, endpoint semantics, calibration/uncertainty, alert metrics and the baseline reconciliation. This cannot be self-certified.
4. Keep the software release research-only. External cohort validation, prospective silent-mode study, institutional/ethics/privacy approvals, and clinical safety/regulatory review are separate requirements.
5. Hardware work is limited to a non-clinical synthetic/replay and dummy-load bench prototype until sensor interfaces, synchronization, signal quality, isolation, power, cybersecurity, verification and expert safety review are specified.

## How to use the project now

Follow [FAST_START_RESEARCH_DEMO.md](FAST_START_RESEARCH_DEMO.md) to install the package, run diagnostics and tests, launch the synthetic twin demo, and inspect aggregate reports. The synthetic demo is a heuristic visualization, **not a trained sepsis predictor**. The supervised probability remains unavailable unless a frozen predictor with matching model/calibration/schema metadata is explicitly supplied.

---

**Historical snapshot below:** the remainder of this file records earlier status and results and is retained for traceability. Where its dates, branches, or PR states differ from the current verified state above, use the dated evidence linked in the current section rather than treating the older status text as current.

**Status date:** 15 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Working branch:** `work/exact-checkout-reproduction`  
**Pull request:** [#1 — Source-verify cross-cohort recalibration and document reproduction](https://github.com/culprit-k/VITALIS/pull/1)  
**Verified branch head at this status update:** `7c468f47d3054f4287765f162d5c675474f84a55`. GitHub Actions passed on this head (144 tests): https://github.com/culprit-k/VITALIS/actions/runs/38630587074. The PR remains open, draft, and unmerged.

> **Safety boundary:** VITALIS is a research prototype only. It is not a medical device or a clinically validated sepsis warning system. Do not use its predictions to guide patient care.

## 1. What are we building?

VITALIS explores whether longitudinal vital signs and laboratory observations can help identify retrospective sepsis-related deterioration labels earlier or more reliably than a simple baseline model. The current model is a research baseline, not a deployable clinical system.

The current work uses the PhysioNet/CinC Challenge 2019 benchmark. The benchmark's hourly `SepsisLabel` already incorporates a six-hour lead convention; it must not be shifted a second time. These labels are not the same as independently adjudicated real-world onset times.

## 2. Where are we now?

**Current stage: retrospective model evaluation and research-release verification.**

The project already has a baseline pipeline, static and temporal feature experiments, tests, aggregate results, cross-cohort evaluation scripts, calibration analysis, and patient-cluster bootstrap uncertainty summaries. The immediate task is to verify and document the existing evidence carefully—not to claim the model is ready for clinical use.

PR #1 remains **open, draft, and unmerged**. It should stay that way until the outstanding verification and review gates are addressed.

## 3. What has been done?

- Implemented research scripts, reusable code, documentation, and tests for static and temporal feature models.
- Evaluated patient-disjoint splits using seeds 42, 123, and 2026.
- Compared Set-A-trained models on held-out Set B, keeping Set B evaluation-only.
- Added an opt-in local-only score-archive path with a guard against writing row-level archives inside the repository.
- Completed 1,000-replicate paired patient-cluster bootstrap summaries for static-versus-temporal comparisons, for all three seeds and both raw and Set-A-validation-Platt-recalibrated probabilities.
- Re-ran the checked-in recalibration runner against existing local feature caches and reconciled its aggregate metrics with the previous source-verified artifact to floating-point precision.
- Added reports explaining the experiment, uncertainty, provenance, privacy boundary, and remaining release blockers.
- Added an initial streaming adaptive physiological twin (`src/vitalis/adaptive_twin.py`) with causal rolling and frozen-reference baselines, two-sided CUSUM for gradual drift, multisystem deviation aggregation, an EWMA trajectory score and direction, coverage checks, persistence, channel-specific scale floors, and suppression of baseline updates for large deviations. Added a timestamped/unit-checked stream adapter (`src/vitalis/stream.py`), a deterministic CLI demo, an interactive synthetic-only Streamlit sandbox (`dashboard/twin_demo.py`), focused tests, and algorithm documentation. CI now compiles Python source/demo files before running tests. These are software components for research, not clinical prediction or a validated digital twin.
- GitHub Actions passed on commit `4b3aa798af04a0819ce1523cb9bae672dcc9dddf`: [workflow run](https://github.com/culprit-k/VITALIS/actions/runs/38612764680). This includes Python compilation, the synthetic timestamped-stream smoke test, and the full test suite including CUSUM and stream-to-twin integration tests. The latest commit is documentation-only. Clean-checkout reproduction from the user's local authorized dataset remains pending.
- Verified a successful GitHub Actions test run on code-bearing commit `a0103df503a574f097045a34062e5f3abf229b60`: [workflow run](https://github.com/culprit-k/VITALIS/actions/runs/38608383356). A later documentation-only commit (`ce824a6d01bc463600ba2ef65b73bce23bc43647`) recorded that result. This does **not** mean CI has been verified on every subsequent documentation commit.

## 4. What do the results mean?

### Benchmark cohort sizes

| Cohort | Patients | Hourly rows | Positive hourly labels |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 |
| Set B | 20,000 | 761,995 | 10,780 |

Set B is a separate cohort within the same challenge benchmark. It is useful for retrospective cross-cohort evaluation, but it is **not** prospective validation in a real clinical workflow or independent evidence of patient benefit.

### Static versus temporal baseline

Across the three split seeds, the reported mean AUROC was approximately **0.6750 for static features** and **0.7319 for temporal features**. Mean AUPRC was approximately **0.0455** and **0.0581**, respectively.

Temporal features improved ranking metrics in these experiments. However, at the fixed probability threshold of 0.5, temporal sensitivity was lower (about **0.383**) than static sensitivity (about **0.477**). The 0.5 threshold is a fixed experimental setting, **not a clinically selected threshold**.

These are retrospective benchmark metrics. They do not establish prospective performance, clinical calibration, decision utility, or safety.

### Uncertainty analysis

The checked-in aggregate report records 1,000 paired patient-cluster bootstrap replicates per seed and probability stream. For each of the three seeds, temporal-minus-static AUROC and AUPRC intervals were above zero, and Brier-score differences were below zero. Interpret these as conditional uncertainty summaries on the fixed held-out benchmark cohort—not as prospective clinical validation or a pooled confidence interval.

### Known unresolved historical discrepancy

An older reconstructed evaluation harness produced different metrics from the checked-in exact-source runner. The older artifact lacks enough source, split, and environment provenance to identify the cause confidently. The discrepancy is documented and the historical artifact is preserved; its cause remains unresolved. Do not silently overwrite either result or guess the explanation.

## 5. What has *not* been verified?

- **Fresh clean checkout and fresh cache build:** not completed. The runtime's clone attempt failed because it could not resolve `github.com`. The successful rerun used existing local caches and verified source blob hashes; it was not a clean-checkout reproduction.
- **Full current-branch test run from a clean checkout:** still pending.
- **History-wide secret and sensitive-artifact audit:** not completed. A changed-file/path review is not a full repository-history scan.
- **Independent clinical/statistical review:** not obtained. No submitted PR reviews or inline review threads were present at the latest review check.
- **Clinical validation:** not performed. There is no basis to claim patient benefit, safe alert thresholds, or readiness for patient care.

## New software milestone: supervised future-label forecasting (2026-10-14)

- Added `src/vitalis/horizon.py` to build leakage-conscious 1-, 3-, and 6-hour future Challenge SepsisLabel targets. It excludes rows already carrying a positive current label, excludes each patient's incomplete future tail, and never shifts labels across patient boundaries.
- Added `scripts/train_horizon_model.py` to train separate patient-disjoint logistic models with causal temporal features, training-only preprocessing, fixed reference threshold, aggregate-only output, patient-level alert burden, challenge-label forecast-window coverage, label-relative warning time, and patient-cluster bootstrap intervals.
- Added `tests/test_horizon.py` for target alignment, patient boundary isolation, time eligibility, alert refractory logic, forecast-window coverage, and uncertainty intervals.
- Added [Horizon forecasting protocol](HORIZON_FORECASTING.md) and documented the CLI in the README.
- GitHub Actions passed on code-bearing commit `2b56ad2a91ede9081ae56e51ed72b9dcfaf4aa6e`: [workflow run](https://github.com/culprit-k/VITALIS/actions/runs/38614183618). All 118 tests passed, including an end-to-end synthetic-PSV training run for the horizon model. An earlier test run exposed one incorrect expected alert count in a test fixture; the fixture was corrected and the suite passed.
- This reflected the initial software-only milestone and is superseded by the completed full-cohort Set A→Set B run documented below. Raw data and feature caches remained local; only aggregate results and provenance were committed.

**Interpretation boundary:** these targets forecast entry into the Challenge SepsisLabel-positive window. The source label already uses a six-hour lead convention, so the new 1/3/6-hour targets are not independent predictions of biological onset. Alert rates are relative to eligible at-risk hours; alerts outside forecast-positive windows are not verified clinical false alarms. Threshold and refractory settings remain research defaults.

## New software milestone: Set A → Set B horizon evaluation (2026-10-14)

- Added `scripts/evaluate_horizon_cross_cohort.py` to compare static and temporal models for future Challenge SepsisLabel entry at 1-, 3-, and 6-hour horizons.
- The runner builds targets within patient blocks, excludes current-positive rows and incomplete future tails, verifies official Set A/Set B row/patient/label counts and feature schema, and uses a patient-disjoint Set A 60/40 training/unused-holdout split.
- Set B is evaluation-only. No fitting, feature selection, calibration, or threshold tuning is performed on Set B.
- Added `tests/test_horizon_cross_cohort.py` for patient-boundary target alignment and synthetic-cache cross-cohort evaluation.
- GitHub Actions passed on commit `013d7fe5050eb0424b51b139e408b05df490a8f2`: [workflow run](https://github.com/culprit-k/VITALIS/actions/runs/38614840411). **120 tests passed.**
- Added [full-cohort execution protocol](HORIZON_CROSS_COHORT_EXECUTION.md), including cache construction and a reproducible command for all nine seed × horizon combinations.
- At the time this software milestone was first recorded, full-cohort execution was pending. It is now complete; see the results section below and the aggregate-only JSON artifact.

**Interpretation boundary:** the targets forecast entry into the Challenge SepsisLabel-positive window; the source label already incorporates a six-hour lead convention. These metrics are not independent sepsis-onset predictions, verified clinical false-alarm rates, or clinical validation. Raw data, caches, and row-level predictions must remain outside Git.

## Full-cohort horizon evaluation completed (2026-10-14)

- Verified and processed all official Set A and Set B rows using local caches; no raw records, caches, or individual predictions were committed.
- Completed 9 seed × horizon runs (seeds 42, 123, 2026; horizons 1, 3, 6 hours) comparing static and temporal logistic regression. Set B was evaluation-only.
- Full results and limitations are in [Full-cohort horizon cross-cohort results](FULL_COHORT_HORIZON_CROSS_COHORT_RESULTS.md).
- Mean AUROC was 0.663/0.681/0.687 for static and 0.657/0.680/0.686 for temporal across the 1/3/6-hour horizons. Static AUPRC was also slightly higher at each horizon.
- Temporal models had lower Brier scores and somewhat fewer alerts, but probabilities remain poorly calibrated, PPV at the fixed 0.5 threshold was very low, and window coverage was lower than static models. Neither is suitable for clinical use.
- Fixed threshold 0.5 and six-hour refractory interval are exploratory reference settings, not clinical operating points.
- Performance fix: patient-level warning metrics now iterate contiguous patient blocks instead of rescanning the full Set B vector for every patient. [CI run #513](https://github.com/culprit-k/VITALIS/actions/runs/38616619520) passed with 120 tests.

**Interpretation boundary:** targets forecast entry into the Challenge SepsisLabel-positive window, not independent biological onset. The source label already incorporates a six-hour lead convention. No clinical validation or patient benefit is established.

## Horizon calibration milestone completed (2026-10-15)

- Completed all nine horizon × seed combinations (1/3/6 h; seeds 42, 123, 2026), fitting 18 static/temporal models on verified local full-cohort caches. Summed runtime was 217.7 seconds; no model-fit warnings were captured.
- Added the patient-disjoint Set A 60/20/20 train/calibration/untouched-holdout protocol. Platt recalibration was fit only on Set A calibration patients; Set B remained final evaluation-only.
- Results: [calibration and operating-point report](HORIZON_CALIBRATION_RESULTS_2026-10-15.md), [aggregate-only summary JSON](../results/horizon_calibration_summary_2026-10-15.json), and [protocol](HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md).
- Platt recalibration substantially reduced Brier scores versus raw class-weighted scores, but Set-B calibrated Brier scores remained slightly worse than the constant-prevalence reference for all six model/horizon combinations. Adequate calibration is not established.
- At a calibrated threshold of 0.005, 6-hour forecast-window coverage was approximately 97–98% with about 4 alerts per at-risk patient-day. This trade-off is descriptive and does not establish a clinical alarm policy.
- Focused calibration tests passed (9/9); GitHub Actions run #564 passed: https://github.com/culprit-k/VITALIS/actions/runs/38622090252.
- Added `src/vitalis/calibration_uncertainty.py` and integrated patient-cluster percentile-bootstrap intervals into the horizon calibration runner for Brier score, log loss, mean predicted probability, fixed-bin ECE, Brier-minus-prevalence-reference, and paired calibrated-minus-raw Brier difference. The default is 200 patient-cluster replicates.
- Added four focused tests for reproducibility, metric parity, invalid inputs, patient-block boundaries, and aggregate-only output. Local available suite: 13 tests passed; GitHub Actions run #570 passed: https://github.com/culprit-k/VITALIS/actions/runs/38622483322.
- Completed the full-cohort uncertainty workflow in nine bounded invocations: 200 patient-cluster replicates per model/horizon/seed, 235.5 seconds summed runtime, zero fit warnings. Results: [uncertainty report](HORIZON_CALIBRATION_UNCERTAINTY_RESULTS_2026-10-15.md) and [aggregate-only JSON](../results/horizon_calibration_uncertainty_summary_2026-10-15.json).
- Provenance caveat: the runtime could not complete a clean Git checkout due to DNS/network unavailability. The local full-cohort run used a reconstructed working copy, not a byte-identically verified checkout; the run is not claimed as exact-source reproduction. The checked-in runner/tests passed CI.
- Paired calibrated-minus-raw Brier intervals were below zero in every run. Many intervals for calibrated Brier minus the prevalence-reference score crossed zero, so adequate calibration or improvement over a prevalence-only reference is not established.
- Added paired patient-cluster bootstrap comparison of static versus temporal Platt-calibrated probabilities on the same eligible Set-B rows, covering AUROC, AUPRC, Brier score, and log loss. All nine seed × horizon runs completed with 200 paired replicates each; zero fit warnings. GitHub Actions run [38624758705](https://github.com/culprit-k/VITALIS/actions/runs/38624758705) passed the full suite: 137 tests.
- Results: [paired comparison report](HORIZON_PAIRED_MODEL_COMPARISON_RESULTS_2026-10-15.md) and [aggregate-only JSON](../results/horizon_paired_model_comparison_aggregate_2026-10-15.json). Temporal AUROC differences had seed-specific intervals above zero at 1 h and 6 h but not consistently at 3 h; AUPRC intervals overlapped zero at all horizons; log loss was lower for temporal at all horizons; Brier differences favored temporal only at 6 h. This is descriptive retrospective comparison, not model selection or clinical validation.
- Completed: utility cost sensitivity plus a 200-replicate-per-fit patient-cluster bootstrap on the untouched Set-A development holdout. See [utility bootstrap results](HORIZON_UTILITY_BOOTSTRAP_RESULTS_2026-10-15.md) and [aggregate-only summary](../results/horizon_utility_bootstrap_summary_2026-10-15.json). Next blockers are independent cost/endpoint review, clean-checkout reproduction, and a new independent cohort; Set B must not be reused for threshold selection.

**Interpretation boundary:** the Challenge label uses a six-hour lead convention, so forecasts concern Challenge-label-window entry rather than independently observed biological sepsis onset. VITALIS remains research-only, not clinically validated, and not for patient care.

## 6. Next steps, in order

1. **Obtain a clean checkout** of the exact PR head once network/DNS works; record the checkout SHA and clean working-tree status.
2. **Rebuild the feature caches** from authorized local challenge data using the checked-in pipeline. Keep all raw patient data, caches, row-level predictions, and NPZ score archives outside Git.
3. **Run the full test suite** from that checkout and rerun the documented reproduction workflow. Save only aggregate results and provenance in the repository.
4. **Reconcile outputs** against the committed source-verified aggregate artifacts; document any differences without guessing at causes.
5. **Complete a history-wide security/privacy audit** using a full local Git history, including secrets and accidentally committed sensitive artifacts. A patch-only scan is not enough.
6. **Request independent statistical and clinical review** of label timing, patient split design, calibration, domain shift, bootstrap estimand, missingness, and the exploratory 5% feature-coverage rule.
7. **Update the release-readiness report** with evidence from the actual checks. Keep PR #1 draft and unmerged until the gates are resolved and an explicit merge decision is made.

## 7. Non-negotiable data and claims rules

- Never commit raw patient records, patient-level derived tables, individual predictions, row-level score archives, cache arrays, credentials, or tokens.
- Set B remains evaluation-only: no fitting, feature selection, recalibrator fitting, or threshold selection on Set B.
- Do not describe retrospective challenge labels as independently observed clinical onset.
- Do not call the exploratory 5% feature-coverage cutoff optimal or clinically justified.
- Do not describe VITALIS as clinically validated or use its output for patient care.

## Related documents

- [Next steps and detailed checklist](NEXT_STEPS.md)
- [Release-readiness audit](RELEASE_READINESS_AUDIT.md)
- [Exact-source rerun reconciliation](FRESH_SOURCE_RERUN_RECONCILIATION.md)
- [1,000-replicate paired patient-cluster bootstrap report](CROSS_COHORT_BOOTSTRAP_RAW_AND_RECALIBRATED_1000.md)
- [Full-cohort cross-cohort results](FULL_COHORT_CROSS_COHORT_RESULTS.md)
- [Utility operating-point framework](UTILITY_OPERATING_POINT_FRAMEWORK.md)
- [Utility operating-point results](HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md)


## 8. Utility-based operating-point milestone (15 October 2026)

- Added a configurable cost-sensitivity framework to compare missed forecast-positive windows against alert burden on the untouched, patient-disjoint Set-A development holdout.
- The evaluator reports row-level sensitivity/PPV, alerts per at-risk patient-day, missed and covered windows, window coverage, and label-relative warning time for static and temporal models at 1/3/6-hour horizons.
- Completed nine seed × horizon runs using available local caches (18 model fits; 249.7 seconds summed; zero captured fit warnings). Aggregate-only report: [utility operating-point results](HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md); machine-readable aggregate: [JSON](../results/horizon_utility_operating_point_aggregate_2026-10-15.json).
- Cost ratios are illustrative scenarios (1, 10, 100, 500, 1,000 missed-window cost units per alert-cost unit), not clinically elicited values. The cost-sensitive candidate threshold varies with assumed cost and sometimes across split seeds; no clinically appropriate threshold has been established.
- Provenance caveat: the full-cohort run used a reconstructed local working copy and is not claimed as byte-identically verified execution of checked-in source. Utility-focused reruns used 20 bootstrap replicates for ancillary uncertainty summaries. Set B remained evaluation-only, and no raw data or row-level predictions were committed.
- Remaining gates: independent clinician/statistician review, verified clean-checkout reproduction, a new independent evaluation cohort for any frozen policy, and prospective/governance validation. VITALIS remains research-only.


## 9. Independent-evaluation readiness (15 October 2026)

- Added [the independent-cohort evaluation protocol](INDEPENDENT_EVALUATION_PROTOCOL.md) and [utility-cost review checklist](UTILITY_COST_REVIEW_CHECKLIST.md). These documents define review and governance gates; they do not indicate that approvals, independent data, or clinical validation have been obtained.
- The Set-A utility framework is integrated and has aggregate-only exploratory results. Its cost ratios are illustrative and threshold candidates are development-only. Set B has already been inspected and must not be reused for threshold selection.
- The next actionable external dependency is independent clinical/statistical review, alongside clean-checkout/pinned-environment reproduction and a history-wide privacy/secret audit.
- A genuinely new cohort with independently defined/adjudicated event timing, governance/ethics approvals, and a frozen model/policy is required before final external evaluation. Prospective studies need separate approvals.
- No clinical operating point is approved. VITALIS remains research-only and must not guide patient care.


## 10. Utility uncertainty and threshold-selection stability (15 October 2026)

- Completed nine seed × horizon runs (18 static/temporal model fits) with 200 patient-cluster bootstrap replicates per fit, 3,600 replicates total, and zero captured model-fit warnings.
- The analysis ran on Set A only; Set B was not loaded or used. The 4,027-patient holdout was patient-disjoint from model training and Platt calibration for each split.
- Results report row sensitivity/PPV, alert burden per at-risk patient-day, forecast-window coverage, run-specific interval envelopes, and selection stability across illustrative missed-window cost ratios. High coverage at low thresholds is paired with high alert burden and low PPV; the cost ratio changes which threshold minimizes the research proxy.
- Report: [utility bootstrap results](HORIZON_UTILITY_BOOTSTRAP_RESULTS_2026-10-15.md). Aggregate-only JSON: [utility bootstrap summary](../results/horizon_utility_bootstrap_summary_2026-10-15.json).
- Provenance remains qualified: the run used a reconstructed local working copy, not a byte-identically verified clean checkout. Local environment versions and source SHA-256 values are recorded in the report. The available reconstructed local test suite passed 28 tests; GitHub Actions passed on PR head `86776762479dd450e20821da8e6f0b50c482e21d` (run [38639673606](https://github.com/culprit-k/VITALIS/actions/runs/38639673606)) before these documentation/result-only additions.
- This does not establish clinical utility. Cost ratios need independent justification; intervals are conditional on fitted models, development splits, and assumptions; a genuinely new independent cohort with independently defined/adjudicated event timing remains necessary. Keep PR #1 draft/unmerged and VITALIS research-only.
