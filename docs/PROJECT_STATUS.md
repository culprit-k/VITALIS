# VITALIS — project status in plain language

**Status date:** 14 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Working branch:** `work/exact-checkout-reproduction`  
**Pull request:** [#1 — Source-verify cross-cohort recalibration and document reproduction](https://github.com/culprit-k/VITALIS/pull/1)  
**Last verified branch head before this status document:** `ce824a6d01bc463600ba2ef65b73bce23bc43647`
**Latest branch head checked during this update:** `e01751ddc81c5c000db4b1a29d76a45f0347fe35` (documentation-only commits after the successful code-bearing CI run).

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
