# VITALIS — project status in plain language

**Status date:** 14 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Working branch:** `work/exact-checkout-reproduction`  
**Pull request:** [#1 — Source-verify cross-cohort recalibration and document reproduction](https://github.com/culprit-k/VITALIS/pull/1)  
**Last verified branch head before this status document:** `ce824a6d01bc463600ba2ef65b73bce23bc43647`
**Latest branch head checked during this update:** `b4b7e66e12caeca693b0a145c2d58223fbde9637` (result provenance and report links recorded). GitHub Actions run #540 passed with 120 tests: https://github.com/culprit-k/VITALIS/actions/runs/38618088465.

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
- Paired calibrated-minus-raw Brier intervals were below zero in every run. Many intervals for calibrated Brier minus the prevalence-reference score crossed zero, so adequate calibration or improvement over a prevalence-only reference is not established.
- Next: define a utility-based operating-point framework on development data with explicit costs for missed forecast windows and alerts. Do not select thresholds on Set B; any selected policy needs a new independent evaluation cohort.

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
