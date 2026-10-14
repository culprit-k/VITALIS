# VITALIS next steps and current status

> For a plain-language overview of the current stage, findings, limitations, and ordered release gates, see [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Phase 1 status: completed within exploratory scope

- [x] Established research repository, dataset protocol, model card, baseline pipeline, tests, and reproducible workflow.
- [x] Implemented and tested static, temporal, and first patient-baseline deviation feature sets.
- [x] Added the Phase 1 closeout report and aggregate-only three-seed evaluation: [Phase 1 report](PHASE1_CLOSEOUT.md), [summary JSON](../results/phase1_500_patient_three_seed_summary.json).
- [x] Evaluated a deterministic 500-patient sample using three patient-disjoint split seeds and paired patient-cluster bootstrap comparisons.
- [x] Repeated the local evaluation and verified byte-for-byte reproducibility of the aggregate output; see [reproducibility manifest](../results/phase1_local_reproducibility_manifest.json).
- [x] Documented negative/mixed findings without claiming that VITALIS-PB improves the baseline.
- [x] Latest main-branch GitHub Actions checks passed.
- [x] Reconcile aggregate outputs from a locally mirrored checked-in runner against the previous local artifact; strict source-byte identity remains open.
- [x] Run exploratory held-out calibration and split-specific missingness diagnostics on a deterministic 500-patient local sample; see [Phase 2 results](PHASE2_CALIBRATION_ROBUSTNESS_RESULTS.md).
- [x] Full-cohort internal exploratory evaluation is now documented across three patient-disjoint split seeds; external validation remains future work.

## Main finding

In the 500-patient exploratory sample, the static model had the best mean AUROC (0.7244) and average precision (0.1018). The temporal model had lower discrimination, while the personalized model had the lowest mean AUROC (0.5847) and average precision (0.0525). The personalized model's lower Brier score but higher log loss is mixed evidence, not proof of good calibration. These results do not justify advancing the personalized model as the default or claiming clinical benefit.

## Phase 2 status: exploratory analysis and aggregate reconciliation complete; strict source-byte identity open

Formal closeout: [Phase 2 closeout report](PHASE2_CLOSEOUT.md). Aggregate-metric reconciliation is complete; strict byte-for-byte source identity remains a documented reproducibility exception.

- [x] Added aggregate calibration and predictor-missingness helper functions with unit tests: [Phase 2 plan](PHASE2_PLAN.md).
- [x] GitHub Actions passed for the Phase 2 helper tests and runner (latest verified run: https://github.com/culprit-k/VITALIS/actions/runs/38549292731).
- [x] Execute runner logic mirrored from checked-in source on the local dataset and reconcile aggregate outputs; split counts and feature counts match, with small metric differences documented in the closeout report. The repository helper assigns reliability bins using original probabilities; the corrected local aggregate artifact records that convention. Strict byte-for-byte source verification remains blocked by local DNS.
- [x] Run held-out calibration and split-specific missingness diagnostics; recalibration was fit on validation data only. Results are exploratory and show unstable recalibration.
- [x] Run an exploratory age/gender and missingness-stratified audit with small-cell suppression; see the Phase 2 results report. Results are unstable and not fairness/safety evidence.
- [x] Full-cohort cache-backed evaluation completed locally across three split seeds; aggregate reconciliation is documented. Strict source-byte identity remains open; external validation remains separate.
- [ ] Obtain clinical/statistical supervision and governance review before prospective or patient-facing research.

## Leakage/evaluation audit (2026-10-14)

- [x] Reviewed patient-level split isolation, training-only preprocessing/feature selection, fixed threshold handling, label timing, temporal feature assumptions, and alert-burden interpretation. See [leakage and evaluation audit](LEAKAGE_EVALUATION_AUDIT.md).
- [x] Added regression tests for overlapping patient splits and threshold/alert-burden calculations; CI passed for the relevant commits.
- [ ] Revisit the chronological-row assumption if any new data loader or dataset format is introduced.

## Full-cohort data-integrity gate (2026-10-14)

- [x] Added an aggregate-only dataset integrity checker and unit tests: `scripts/check_dataset_integrity.py` and `tests/test_dataset_integrity.py`.
- [x] Ran the checker over all 20,336 `training_setA` patient files: 790,215 rows; 17,136 positive challenge-label rows; zero invalid target rows, empty files, or column-set mismatches. See [integrity audit JSON](../results/phase3_training_setA_integrity_audit.json).
- [x] Full-cohort static/temporal evaluation completed for seeds 42, 123, and 2026 with a cache-backed local harness; see [repository-runner reconciliation](REPOSITORY_RUNNER_RECONCILIATION.md). [ ] Strict source-byte verification remains open: local working copies were reconstructed from checked-in logic and were not byte-identical to GitHub blobs.

## Next software/research actions

1. Make the full-cohort model runner operational within a bounded runtime, with cached feature matrices or incremental processing and explicit CLI arguments for split seed/output path; then rerun matched static/temporal models on multiple patient-disjoint seeds.
2. Finish strict source/blob identity verification for the Phase 2 mirrored runner; aggregate-metric reconciliation is recorded.
3. Review the [Phase 2 calibration/missingness results](PHASE2_CALIBRATION_ROBUSTNESS_RESULTS.md); aggregate-metric reconciliation is documented, while strict byte-for-byte source identity remains open.
4. Expanded robustness grid completed locally: median imputation with/without missingness indicators and raw/Platt/isotonic calibration. See [aggregate summary](../results/phase2_robustness_grid_summary.json). Do not interpret lower Brier/log loss after Platt scaling as proof of clinical calibration.
5. Obtain clinical/statistical supervision and governance review before any prospective or patient-facing research.

## Hardware gate

No custom hardware purchases are recommended from these results alone. Sensor selection and interface planning can be drafted, but hardware prototyping should follow a clearer software signal specification and research justification. VITALIS remains research-only, not a medical device or clinical decision tool.

## Innovation and IP

- [x] Defined and implemented a mathematical patient-baseline deviation hypothesis as an experimental feature generator.
- [x] Evaluated it against static and temporal feature sets on matched patient-level splits with paired patient-cluster uncertainty estimates.
- [ ] Improve or reject the hypothesis based on further analysis; no novelty or patentability claim is supported without separate prior-art and IP review.

## Safety boundary

VITALIS is not validated for diagnosis, triage, treatment, or real patient-care decisions. No patient-level records or predictions belong in this public repository.


## Full-cohort multi-seed exploratory comparison (2026-10-14)

- [x] Evaluated static and temporal logistic-regression models on all of training_setA using local optimized/cached-feature harnesses for split seeds 42, 123, and 2026. Aggregate report: [full-cohort multi-seed results](FULL_COHORT_MULTISEED_RESULTS.md), [aggregate JSON](../results/full_cohort_multiseed_summary_2026-10-14.json).
- [x] Recorded the mean and sample standard deviation across three split seeds; these SDs are not confidence intervals.
- [x] Recorded the source-provenance caveat: these are not byte-verified executions of the checked-in full-cohort CLI.
- [x] Built and tested a repository-native, cache-backed multi-seed runner with explicit seed/output arguments, bounded memory, and aggregate-only output; local results are reconciled in [the runner report](REPOSITORY_RUNNER_RECONCILIATION.md).
- [ ] Add paired patient-cluster uncertainty intervals across matched test predictions from each seed; current multi-seed summary cannot estimate paired differences because only aggregate outputs were retained for seeds 123 and 2026.
- [ ] Perform external validation and obtain clinical/statistical supervision before any prospective or patient-facing study.


## Cache-backed reproducible multi-seed runner

- [x] Added `scripts/build_feature_cache.py` to build a local memory-mapped feature cache in patient-index chunks; raw dataset and cache must remain outside Git.
- [x] Added `scripts/evaluate_cached_multiseed.py` to evaluate patient-disjoint splits and write aggregate-only results for multiple seeds.
- [x] Added metric tests for the cached evaluator: `tests/test_cached_multiseed.py`; GitHub Actions passed for the test and runner commits (runs 38558602303, 38558586454, and 38558571408).
- [x] Ran the cache-backed evaluator locally against the full dataset for seeds 42, 123, and 2026 and compared aggregate outputs with [the prior exploratory summary](FULL_COHORT_MULTISEED_RESULTS.md). Source-byte identity is still not verified.
- [x] Verified all four cache chunks, dimensions, and patient group vectors before evaluation. Cache files remain outside Git; no row-level predictions or patient identifiers were committed.


## Repository-runner full-cohort reconciliation (2026-10-14)

- [x] Built the local memory-mapped feature cache in four patient chunks and verified 20,336 patient groups, 790,215 rows, 17,136 positive hourly labels, and 109 feature columns.
- [x] Ran the cache-backed evaluator separately for split seeds 42, 123, and 2026; each seed completed and wrote aggregate-only output locally.
- [x] Recorded the reconciliation summary and per-seed results: [runner reconciliation report](REPOSITORY_RUNNER_RECONCILIATION.md), [aggregate JSON](../results/repository_runner_full_cohort_reconciliation_2026-10-14.json).
- [x] The results reproduce the earlier aggregate AUROC/AUPRC/Brier metrics to displayed precision. Temporal features have higher mean AUROC/AUPRC and lower mean Brier score in these exploratory splits.
- [ ] Strict byte-for-byte identity between local working copies and GitHub checked-in source blobs remains open. The local scripts were reconstructed from checked-in logic, not verified as identical bytes.
- [ ] Paired patient-cluster uncertainty intervals from matched held-out predictions remain outstanding; existing three-seed SDs are not confidence intervals.
- [ ] External/prospective validation and clinical/statistical governance review remain required before clinical claims.


## Cache-backed full-cohort reconciliation (2026-10-14)

- [x] Built all four local feature-cache chunks for training_setA outside the Git repository; verified the dataset totals against the integrity audit (20,336 patients, 790,215 rows, 17,136 positive hourly labels).
- [x] Ran the cached evaluator in separate processes for seeds 42, 123, and 2026. Per-seed split counts and AUROC/AUPRC/Brier metrics matched the earlier aggregate results to displayed precision. See [reconciliation report](FULL_COHORT_MULTISEED_RESULTS.md) and [aggregate JSON](../results/full_cohort_repository_native_reconciliation_2026-10-14.json).
- [x] Confirmed the cache builder and evaluator implementation commits passed GitHub Actions tests; the latest documentation CI passed in run https://github.com/culprit-k/VITALIS/actions/runs/38558803433.
- [ ] Strict byte-for-byte source identity remains open: the local evaluator used for this run was reconstructed from the checked-in script logic. It was not verified as an unchanged checkout of the GitHub blob.
- [ ] Future evaluation should retain only aggregate outputs in Git and use paired patient-cluster uncertainty intervals where matched predictions can be retained securely outside the public repository.


## Current next milestone: paired uncertainty for full-cohort model comparison

- [x] Added paired patient-cluster bootstrap intervals for temporal-minus-static AUROC, AUPRC, and Brier score to the cache-backed evaluator; intervals resample patients, not hourly rows. Full-cohort interval execution is pending.
- [x] Bootstrap probabilities and group vectors remain in memory; the runner writes aggregate intervals only.
- [x] Added deterministic tests for paired bootstrap reproducibility, input validation, and aggregate-only output. CI result is pending: https://github.com/culprit-k/VITALIS/actions/runs/38560507472.
- [x] Preserved the initial 20-replicate pilot as preliminary. The follow-up exact-source raw and recalibrated analyses now use 1,000 paired patient-cluster replicates per seed; see [the final aggregate JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_raw_and_recalibrated_exact_source_1000x3_2026-10-14.json).


## Preliminary full-cohort uncertainty results

- [x] Committed aggregate-only paired patient-cluster bootstrap results for seeds 42, 123, and 2026. Temporal AUROC differences were positive across all three seeds; Brier differences were negative; AUPRC interval crossed zero for seed 123. See [report](FULL_COHORT_PAIRED_BOOTSTRAP.md).
- [x] Increased exact-source cross-cohort bootstrap to 1,000 replicates per seed and probability stream; checked-in source hashes and accelerated-runner parity checks are recorded in the final [aggregate JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_raw_and_recalibrated_exact_source_1000x3_2026-10-14.json) and [report](CROSS_COHORT_BOOTSTRAP_RAW_AND_RECALIBRATED_1000.md).


## 200-replicate paired bootstrap milestone (2026-10-14)

- [x] Completed 200 paired patient-cluster bootstrap replicates for each held-out split seed 42, 123, and 2026 using an optimized local working copy and the full-cohort feature cache.
- [x] Updated [the bootstrap report](FULL_COHORT_PAIRED_BOOTSTRAP.md) and [aggregate JSON](../results/full_cohort_paired_patient_cluster_bootstrap_2026-10-14.json). Temporal-minus-static AUROC intervals were above zero for all three seeds; Brier differences were below zero; AUPRC interval crossed zero for seed 123.
- [ ] The exact checked-in evaluator source was not byte-identically executed; local implementation used a performance-optimized weighted-metric implementation. Source-byte identity remains open.
- [ ] Port and test the optimized tie-aware weighted metrics in the checked-in evaluator, then run CI and verify numerical agreement against this aggregate artifact before claiming repository-native reproducibility.
- [ ] These are retrospective hourly challenge-label metrics only; external validation and clinical/statistical governance review remain required.


## Weighted-bootstrap implementation and CI (2026-10-14)

- [x] Ported pre-sorted, tie-aware weighted AUROC/AUPRC and weighted Brier calculations into the checked-in evaluator to reduce bootstrap runtime.
- [x] Added randomized tied-score parity tests against scikit-learn; corrected a zero-weight score-threshold edge case discovered by CI.
- [x] GitHub Actions passed after the fix: https://github.com/culprit-k/VITALIS/actions/runs/38562541833.
- [x] Re-ran the 200-replicate analysis for each split seed in separate local processes; aggregate intervals are documented in [the report](FULL_COHORT_PAIRED_BOOTSTRAP.md).
- [x] The initial full-cohort 1,000-replicate attempt exceeded the local execution window. This was resolved by running the accelerated, tie-aware bootstrap over retained local score vectors in deterministic chunks; the final 1,000-replicate aggregate is committed.
- [ ] Strict byte-for-byte source execution remains unverified; local evaluation files were reconstructed and are not an unchanged checkout of the repository blobs.


## Batched higher-replicate bootstrap (2026-10-14)

- [x] Saved held-out score vectors outside Git for split seed 42 and ran 1,000 paired patient-cluster bootstrap replicates in batches. The bootstrap-only calculation completed in ~28 seconds after scores were prepared.
- [x] Added aggregate-only result artifact: [seed 42, 1,000 replicates](../results/full_cohort_paired_patient_cluster_bootstrap_seed42_1000_2026-10-14.json).
- [x] Added checked-in reusable bootstrap runner: [scripts/bootstrap_heldout_scores.py](../scripts/bootstrap_heldout_scores.py). It accepts a local NPZ score archive and writes aggregate JSON only; do not commit score archives.
- [x] Added randomized tied-score parity tests against scikit-learn and deterministic/privacy tests in [test_cached_multiseed.py](../tests/test_cached_multiseed.py). CI runs: runner https://github.com/culprit-k/VITALIS/actions/runs/38563789399 and tests https://github.com/culprit-k/VITALIS/actions/runs/38563811238 (check current status before calling them green).
- [x] Prepared score archives separately and completed 1,000 replicates for seeds 42, 123, and 2026. Aggregate-only artifact: [1,000 × 3 seed results](../results/full_cohort_paired_patient_cluster_bootstrap_1000x3_2026-10-14.json); interpretation in [the report](FULL_COHORT_PAIRED_BOOTSTRAP.md).
- [ ] Strict source-byte identity for held-out score generation remains open. The current seed-42 score archive came from a reconstructed local evaluator, not a byte-identical checkout of the repository model runner.
- [ ] Execute the exact checked-in bootstrap-only script against each retained local score archive and reconcile its output numerically against the aggregate artifact. The checked-in implementation's CI tests passed, but the committed local results were produced by a reconstructed implementation.


## Bootstrap output reconciliation (2026-10-14)

- [x] Re-ran the local batched bootstrap runner on each retained local score archive: seeds 42, 123, and 2026, with 1,000 replicates each.
- [x] Reconciled the means and both interval endpoints for AUROC, AUPRC, and Brier score against the committed 1,000 × 3 aggregate artifact; all nine comparisons match within 1e-12. See [reconciliation JSON](../results/full_cohort_bootstrap_output_reconciliation_2026-10-14.json).
- [x] Updated the [bootstrap report](FULL_COHORT_PAIRED_BOOTSTRAP.md). Score archives remain outside Git.
- [ ] Exact source-byte identity for model fitting and held-out score generation remains open. Numerical agreement of a reconstructed local runner is not equivalent to execution from an exact repository checkout.


## Both-cohort cross-cohort evaluation (2026-10-14)

- [x] Verified both local official cohorts: training_setA (20,336 patients; 790,215 rows; 17,136 positive hourly challenge-label rows) and training_setB (20,000 patients; 761,995 rows; 10,780 positive hourly challenge-label rows).
- [x] Ran a patient-disjoint cross-cohort experiment: train on a 60% patient subset of set A and evaluate on every patient in set B, across seeds 42, 123, and 2026. Aggregate-only results: [cross-cohort report](FULL_COHORT_CROSS_COHORT_RESULTS.md), [summary JSON](../results/cross_cohort_train_A_test_B_2026-10-14.json).
- [x] Added `scripts/evaluate_cross_cohort.py` and regression tests. This experiment evaluates both static and temporal feature sets; row-level predictions and raw patient data remain local.
- [x] Retrieved `scripts/evaluate_cross_cohort.py` from the current branch, verified the local Git blob SHA against GitHub (`f700bf0848cd718301d9693c3dae13444a9bfe8b`), and executed the exact script against both local caches for seeds 42, 123, and 2026 (one seed per invocation). Aggregate-only exact-source results are in [the reproduction JSON](../results/cross_cohort_exact_source_reproduction_2026-10-14.json). A full Git checkout was not verified because local GitHub DNS was unavailable.
- [ ] Investigate calibration and cohort shift before drawing probability or clinical conclusions. Temporal features improved AUROC/AUPRC here but had lower sensitivity at the fixed 0.5 threshold; no operating point is clinically selected.
- [ ] External/prospective validation, clinical/statistical supervision, and governance review remain required before any patient-facing research.


## Combined A+B cohort evaluation (2026-10-14)

- [x] Ran a patient-disjoint, three-seed static-versus-temporal comparison using both official training cohorts pooled together: 40,336 patients, 1,552,210 hourly rows, and 27,916 positive hourly challenge-label rows. See [combined A+B report](FULL_AB_COMBINED_RESULTS.md) and [aggregate JSON](../results/full_AB_combined_multiseed_2026-10-14.json).
- [x] Kept the combined-cohort experiment distinct from the [train-A/test-B cross-cohort experiment](FULL_COHORT_CROSS_COHORT_RESULTS.md); the latter is the stronger cohort-shift check.
- [x] Documented that model fitting capped training data at 500,000 sampled hourly rows per split and that the local evaluator was not byte-verified against the exact GitHub source.
- [ ] Execute both-cohort and cross-cohort experiments from an exact repository checkout and reconcile aggregate metrics against these reports.
- [x] Added paired patient-cluster percentile-bootstrap intervals (200 replicates per split) for combined A+B held-out comparisons; aggregate-only artifact and interpretation are in [the combined-cohort report](FULL_AB_COMBINED_RESULTS.md) and [bootstrap JSON](../results/full_AB_combined_paired_bootstrap_200x3_2026-10-14.json). Score archives remain outside Git.
- [ ] Investigate calibration, subgroup robustness, alert burden at clinically justified thresholds, and cohort shift under statistical/clinical supervision. No patient-facing use before external/prospective validation and governance review.


## Combined A+B paired uncertainty analysis (2026-10-14)

- [x] Regenerated held-out static and temporal scores for the three combined-cohort split seeds from local caches; retained score archives locally only.
- [x] Completed 200 paired patient-cluster bootstrap replicates per seed and committed aggregate-only intervals in [results/full_AB_combined_paired_bootstrap_200x3_2026-10-14.json](../results/full_AB_combined_paired_bootstrap_200x3_2026-10-14.json).
- [x] Documented conditional intervals in [the combined-cohort report](FULL_AB_COMBINED_RESULTS.md): AUROC and AUPRC differences were positive and Brier differences negative across all three splits.
- [ ] Exact source-byte identity for model fitting and held-out score generation remains unresolved; local runner copies were reconstructed from checked-in logic. Do not describe these as exact-checkout reproductions.
- [ ] Run the full combined-cohort and train-A/test-B analyses from an exact repository checkout with local data, then reconcile aggregate outputs.
- [ ] Investigate calibration, cohort shift, subgroup robustness, and alert burden under clinical/statistical supervision. No patient-facing use before external/prospective validation and governance review.


## Cross-cohort calibration audit (2026-10-14)

- [x] Added reusable descriptive calibration runner: scripts/evaluate_cross_cohort_calibration.py; CI unit tests passed for the diagnostic helper.
- [x] Audited raw static and temporal probabilities on all set B patients across training-subset seeds 42, 123, and 2026; see docs/CROSS_COHORT_CALIBRATION_AUDIT.md and results/cross_cohort_calibration_diagnostics_2026-10-14.json.
- [x] Recorded that mean predicted probabilities were 36.8% static and 26.3% temporal versus 1.415% positive hourly-label prevalence. The temporal model ranked labels better, but neither raw probability stream is calibrated for use as risk estimates.
- [x] Added a descriptive constant-prevalence reference to contextualize Brier score and log loss. It uses set B prevalence only as a scale reference, not as a deployable model.
- [ ] The analysis runner was reconstructed locally and exact source-byte identity for model fitting remains unverified; rerun from an exact repository checkout before treating the aggregate artifact as a strict reproduction.
- [ ] Next calibration experiment: fit a pre-specified recalibrator using only a patient-disjoint validation subset of set A, freeze it, and evaluate once on set B. Do not tune on set B.
- [ ] External/prospective validation and clinical/statistical governance review remain required before patient-facing research.


## Cross-cohort recalibration (2026-10-14)

- [x] Completed validation-only Platt recalibration on patient-disjoint set A validation partitions and evaluated frozen recalibrators on all set B patients for seeds 42, 123, and 2026.
- [x] Committed aggregate-only three-seed results: [JSON](../results/cross_cohort_validation_A_recalibration_test_B_3seed_2026-10-14.json) and [report](CROSS_COHORT_RECALIBRATION_PILOT.md).
- [x] Kept set B out of model fitting, recalibrator fitting, and threshold selection.
- [x] Recalibrated Brier score and log loss were substantially lower across all three seeds; AUROC/AUPRC were essentially unchanged. These are benchmark results, not proof of clinical calibration.
- [ ] Add a parameterized checked-in runner for the exact train/validation/test protocol and regression tests proving patient separation and that set B is never used to fit calibration.
- [ ] Run that committed runner from an exact repository checkout and reconcile aggregate results; current local harness source identity is unverified.
- [ ] Obtain clinical/statistical supervision and governance review before prospective or patient-facing research.



## Cross-cohort recalibration runner implementation (14 October 2026)

- [x] Added `scripts/evaluate_cross_cohort_recalibration.py` with explicit cache/seed/output arguments, patient-disjoint 60/20/20 set-A partitions, validation-only Platt fitting, chunked set-B scoring, and aggregate-only output.
- [x] Added `tests/test_cross_cohort_recalibration.py` for patient isolation, deterministic splits, validation-only recalibrator inputs, invalid-input handling, and aggregate-only metrics.
- [x] Documented the reproduction command in [the cross-cohort recalibration report](CROSS_COHORT_RECALIBRATION_PILOT.md).
- [x] GitHub Actions passed for the checked-in runner and regression tests (run https://github.com/culprit-k/VITALIS/actions/runs/38583831584). This verifies the software tests, not exact reproduction of the local aggregate results.
- [x] Executed the byte-identical checked-in recalibration runner against local Set-A/Set-B caches for seeds 42, 123, and 2026; the seven focused tests passed and reruns matched the stored source-verified outputs (exactly for seeds 42/123, within 1.5e-14 for seed 2026). The runtime could not verify a full Git checkout because GitHub DNS resolution failed. See [reproducibility reconciliation](CROSS_COHORT_REPRODUCIBILITY_RECONCILIATION.md) and [JSON](../results/cross_cohort_reproducibility_reconciliation_2026-10-14.json).


## Current handover checkpoint — cross-cohort recalibration (14 October 2026)

- [x] Confirmed the latest main-branch workflow run for `Track checked-in cross-cohort recalibration runner` completed successfully: https://github.com/culprit-k/VITALIS/actions/runs/38583831584.
- [x] Confirmed the preceding documentation update workflow also passed: https://github.com/culprit-k/VITALIS/actions/runs/38583816179.
- [x] The checked-in runner uses patient-disjoint 60/20/20 partitions in set A, fits Platt recalibration on set-A validation predictions only, scores set B in chunks, and writes aggregate-only results. Set B is not used for fitting or threshold selection.
- [x] Retrieved the cache builder, recalibration runner, and focused test source from `main` commit `90ce87677b1e1692c3a6f04f7394f9ce59cf7481`; each local blob hash matched the GitHub blob SHA. Built local-only caches and ran seeds 42, 123, and 2026 against all 20,000 set-B patients. Focused tests passed (7/7); aggregate-only output is in [the source-verified JSON](../results/cross_cohort_validation_A_recalibration_test_B_source_verified_2026-10-14.json) and [report](CROSS_COHORT_RECALIBRATION_SOURCE_VERIFIED.md). A full `git clone` still could not resolve `github.com` DNS, so this is byte-identical-source execution, not a verified full checkout. Raw metrics reconcile to floating-point precision; recalibrated probability metrics have small but nonzero discrepancies versus the historical reconstructed-harness artifact, which is retained unchanged.
- [x] Independently reran the exact-source recalibration CLI for each seed; stored aggregate outputs matched to floating-point precision and the focused test suite passed again. See the [cross-cohort reproducibility reconciliation](CROSS_COHORT_REPRODUCIBILITY_RECONCILIATION.md).
- [x] Added exact-source paired patient-cluster bootstrap intervals for raw Set-B static-versus-temporal scores (200 replicates per training split); row-level score archives remain local-only. Aggregate-only results: [exact-source bootstrap JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_exact_source_200x3_2026-10-14.json) and [cross-cohort report](FULL_COHORT_CROSS_COHORT_RESULTS.md). A 1,000-replicate attempt exceeded the runtime window; 200-replicate intervals remain preliminary.
- [ ] Audit subgroup performance and calibration without using set B to tune model or recalibrator. Suppress small cells and frame results as exploratory.
- [ ] Document the final pre-specified evaluation protocol and obtain statistical/clinical governance review before any prospective or patient-facing study. VITALIS remains research-only.


## Cross-cohort paired uncertainty pilot (14 October 2026)

- [x] Generated local-only held-out Set B score archives for seeds 42, 123, and 2026; archives include labels, patient groups, and raw/recalibrated model scores and remain outside Git.
- [x] Ran an exploratory paired patient-cluster bootstrap comparing temporal vs static models for raw and Set-A-validation-recalibrated probabilities (20 replicates per seed/stream).
- [x] Committed aggregate-only pilot intervals: [JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_20x3_2026-10-14.json) and [report](CROSS_COHORT_RECALIBRATION_PILOT.md).
- [x] Generated raw Set-B score archives using the exact checked-in evaluator (source blob verified) and ran the checked-in bootstrap script for 200 replicates per seed. See [exact-source bootstrap results](../results/cross_cohort_paired_patient_cluster_bootstrap_exact_source_200x3_2026-10-14.json). A 1,000-replicate attempt did not complete within the execution window.
- [x] Optimized the cross-cohort bootstrap and completed 1,000 exact-source replicates per seed for raw and Set-A-validation-Platt-recalibrated scores. See [the 1,000-replicate aggregate JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_raw_and_recalibrated_exact_source_1000x3_2026-10-14.json) and [report](CROSS_COHORT_BOOTSTRAP_RAW_AND_RECALIBRATED_1000.md). The earlier reconstructed-harness 20-replicate pilot remains distinct and is not treated as source-verified.
- [ ] Run score generation from an exact repository checkout and reconcile the aggregate results; current score-generation source identity remains unverified.
- [ ] Continue with a pre-specified subgroup robustness audit, suppress small cells, and keep Set B out of all model/recalibrator/threshold tuning.

## Cross-cohort 1,000-replicate uncertainty work — partial checkpoint (14 October 2026)

- [x] Started upgrading the Set-B paired patient-cluster bootstrap beyond the 20-replicate pilot. A Numba-accelerated local implementation completed 1,000 valid patient-cluster replicates for seed 42 using raw probabilities.
- [x] Added the aggregate-only partial result: [seed 42 raw stream, 1,000 replicates](../results/cross_cohort_paired_bootstrap_seed42_raw_1000_2026-10-14.json). Temporal-minus-static AUROC difference was +0.0575 (95% percentile interval +0.0497 to +0.0647), AUPRC difference +0.0135 (+0.0111 to +0.0167), and Brier difference -0.0641 (-0.0650 to -0.0632).
- [x] Completed all six seed/stream analyses: raw and recalibrated probabilities for seeds 42, 123, and 2026, 1,000 replicates each. Aggregate-only results are committed in [the 1,000-replicate JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_raw_and_recalibrated_exact_source_1000x3_2026-10-14.json).
- [ ] Validate the optimized bootstrap implementation against the checked-in bootstrap runner on synthetic tied-score fixtures and compare its results against the existing 20-replicate pilot where applicable.
- [ ] Exact source-byte identity for model fitting and score generation remains open; the current scores came from reconstructed local runner logic. This is not external or prospective clinical validation.
- [x] Added an operator-facing [exact-checkout reproduction runbook](EXACT_CHECKOUT_REPRODUCTION.md) with clean-checkout checks, cache-build commands, the committed runner invocation, reconciliation criteria, and data-safety boundaries. This documents the procedure; the exact-checkout data run itself remains pending.



## Source-verified cross-cohort recalibration run (14 October 2026)

- [x] Validated the local archive aggregate totals: set A 20,336 patients / 790,215 rows / 17,136 positive hourly labels; set B 20,000 patients / 761,995 rows / 10,780 positive hourly labels. Both schemas had 41 columns with no schema-mismatch or empty patient files.
- [x] Executed the byte-identical checked-in cache builder and recalibration runner source blobs for seeds 42, 123, and 2026; the set-B cohort was evaluation-only and output was aggregate-only.
- [x] Focused tests passed (7/7); GitHub Actions test run 38589529596 completed successfully.
- [x] Added [source-verified aggregate JSON](../results/cross_cohort_validation_A_recalibration_test_B_source_verified_2026-10-14.json) and [reconciliation report](CROSS_COHORT_RECALIBRATION_SOURCE_VERIFIED.md). Historical artifact remains unchanged.
- [ ] Investigate the modest recalibrated Brier/log-loss/mean-probability discrepancy versus the prior reconstructed harness; prior environment metadata is insufficient to attribute it conclusively.
- [ ] Address the EtCO2 feature-availability shift before interpreting cross-cohort performance: EtCO2 is absent in all set-A rows but present in 57,636 set-B rows; the set-A-fitted imputer drops EtCO2 and its derived features, so set-B values are unused. Assess a pre-specified feature policy without tuning on set B.
- [ ] Obtain a full clean Git checkout once DNS/network access is available to close the remaining full-checkout provenance detail. Do not mislabel the current run as a full checkout.
- [ ] Continue with pre-specified subgroup and higher-replicate uncertainty analysis; keep patient-level records, caches, group IDs, and row-level predictions outside Git. VITALIS remains research-only.

## Cross-cohort feature-availability audit (14 October 2026)

- [x] Audited finite-value availability across all 109 cached feature columns in Set A (20,336 patients / 790,215 hourly rows) and Set B (20,000 patients / 761,995 hourly rows); aggregate-only report: [feature availability audit](CROSS_COHORT_FEATURE_AVAILABILITY_AUDIT.md) and [JSON](../results/cross_cohort_feature_availability_audit_2026-10-14.json).
- [x] Found four features entirely missing in Set A but observed in Set B: EtCO2 and its lag, delta, and rolling-mean derivatives. Also found 45 features with at least a 5-percentage-point difference in finite hourly-row rate.
- [x] Pre-specified the analysis boundary: Set-A training data determines feature eligibility; freeze the feature list before validation/test; Set B remains evaluation-only and must not be used for feature selection or tuning.
- [ ] Before a new performance experiment, inspect the existing cache-builder temporal feature semantics and measurement conventions; define a Set-A-only minimum-coverage rule and document it before fitting.
- [ ] Run a sensitivity analysis with the frozen eligible-feature policy and compare it to the existing baseline; report performance and missingness separately, without selecting the policy based on Set-B metrics.
- [ ] Feature availability alone does not prove measurement comparability or explain causality. VITALIS remains research-only; no clinical validity or utility claim follows from this audit.

## Cross-cohort feature-coverage sensitivity analysis (14 October 2026)

- [x] Completed a Set-A-training-only 5% finite-coverage sensitivity rule across seeds 42, 123, and 2026; Set B remained evaluation-only. See [coverage sensitivity report](CROSS_COHORT_COVERAGE_SENSITIVITY.md) and [aggregate JSON](../results/cross_cohort_coverage_sensitivity_2026-10-14.json).
- [x] Static ranking metrics decreased slightly under the filter (mean AUROC 0.6750 to 0.6687; AUPRC 0.0455 to 0.0436); temporal ranking metrics were similar/slightly higher (AUROC 0.7319 to 0.7335; AUPRC 0.0581 to 0.0583). This is a descriptive sensitivity result, not evidence that the 5% cutoff is optimal.
- [x] The eligibility list was derived only from each Set-A training partition; recalibration used the disjoint Set-A validation partition. Set B was not used for feature eligibility, fitting, recalibration, or threshold selection.
- [ ] The 5% cutoff is an exploratory policy, not clinically justified. Before adopting any feature-coverage cutoff, obtain domain/statistical justification or specify it externally and freeze it before final evaluation.
- [ ] Further investigate large availability shifts among features retained by the policy; finite-value rates alone do not establish comparable measurement practice or missingness mechanisms.
- [ ] Full clean-checkout provenance remains open because GitHub DNS was unavailable during local execution; the sensitivity wrapper itself is local-only and is not a checked-in CLI. VITALIS remains research-only.

## Reproducible feature-availability audit CLI (14 October 2026)

- [x] Added `scripts/audit_feature_availability.py`, which reads local feature caches in bounded chunks, validates cache dimensions/schema, and writes aggregate finite-value counts/rates only.
- [x] Added unit tests for finite counts, cohort shift reporting, schema/shape errors, and threshold validation: `tests/test_feature_availability_audit.py`.
- [x] Added a runbook: [reproducing the feature-availability audit](REPRODUCING_FEATURE_AVAILABILITY_AUDIT.md).
- [ ] Confirm GitHub Actions on the current PR head before treating this step as CI-verified.
- [ ] When feasible, compare the CLI's aggregate output against the previously recorded audit JSON using local caches; keep raw caches and all row-level data outside Git.
- [ ] This audit is descriptive only. Do not use Set B to select features, tune models, or choose thresholds; no clinical validity or utility claim follows.

## Patient-level feature-availability and missingness-pattern audit (14 October 2026)

- [x] Added `scripts/audit_patient_level_availability.py` to aggregate feature availability by patient from local caches; it validates dimensions, group counts, and contiguous patient slices.
- [x] Added regression tests for patient-level aggregation and invalid cache layouts: `tests/test_patient_level_availability_audit.py`.
- [x] Recorded aggregate results and interpretation limits: [patient-level audit report](PATIENT_LEVEL_AVAILABILITY_AUDIT.md) and [aggregate JSON](../results/patient_level_feature_availability_audit_2026-10-14.json).
- [x] Observed marked patient-level coverage shifts: DBP 63.69% of Set-A patients vs 99.87% Set B; HCO3 97.37% vs 2.08%; BaseExcess 62.21% vs 2.79%; EtCO2 0% vs 16.08%. Respiratory rate availability was similar (~99.8%) across both cohorts.
- [x] Reported unadjusted differences in patient-level any-positive-label rates by feature availability as descriptive only; these do not identify missingness mechanisms or establish causality.
- [x] Reviewed the official PhysioNet/CinC 2019 documentation and added duration-stratified patient-level availability summaries. The broad record-duration strata show availability gradients, but large cohort differences persist; workflow/severity explanations remain hypotheses, not findings. See [patient-level audit report](PATIENT_LEVEL_AVAILABILITY_AUDIT.md) and [aggregate JSON](../results/patient_level_feature_availability_audit_2026-10-14.json).
- [x] GitHub Actions test workflow passed on branch head `1bad4990f63387c9427770e8bdf4baf9bf4fac20` (run https://github.com/culprit-k/VITALIS/actions/runs/38598858712). No patient-level records, identifiers, or predictions are committed; VITALIS remains research-only.


## Duration-stratified missingness and source-provenance follow-up (14 October 2026)

- [x] Reviewed the official PhysioNet/CinC Challenge 2019 documentation for cohort provenance, hourly data semantics, variable definitions, missing-value meaning, and six-hour label timing: https://physionet.org/content/challenge-2019/1.0.0/.
- [x] Extended `scripts/audit_patient_level_availability.py` to report patient-level availability overall and within record-duration bands (1–24, 25–48, 49–72, and 73+ hours), including descriptive availability by ever-positive challenge-label status.
- [x] Added regression coverage for duration-stratified output and updated the aggregate-only results and report.
- [x] Found that longer records generally have higher availability for FiO2, pH, and lactate in both cohorts, but broad duration stratification does not remove the large cross-cohort differences in DBP, HCO3/BaseExcess, or EtCO2.
- [x] Documented that positive-label status and availability are associated in several strata, while explicitly noting that the outcome is any positive label over the full record and feature availability can include post-label measurements. This is not prospective predictive evidence or causal adjustment.
- [x] GitHub Actions passed for the duration-stratified audit code/tests (run https://github.com/culprit-k/VITALIS/actions/runs/38595875000). Reran the exact checked-in script against local Set A/Set B caches; verified the local script/test Git blob SHAs against GitHub, passed the three committed tests locally, and reconciled all cohort totals and 11 feature-level aggregate metrics with the committed artifact. See the source-reproduction section of [the patient-level audit report](PATIENT_LEVEL_AVAILABILITY_AUDIT.md) and provenance in [the aggregate JSON](../results/patient_level_feature_availability_audit_2026-10-14.json).
- [x] Reviewed the original Challenge paper and clarified that public Set A and Set B correspond to different hospital systems and different EMR systems (BIDMC, 20,336 patients; Emory University Hospital, 20,000 patients). This makes hospital/EMR domain shift a well-grounded concern, but does not identify the exact cause of individual feature shifts. See [patient-level audit report](PATIENT_LEVEL_AVAILABILITY_AUDIT.md) and [aggregate JSON provenance](../results/patient_level_feature_availability_audit_2026-10-14.json).


## Patient-level audit reproduction and cohort provenance closeout (14 October 2026)

- [x] Re-executed the exact checked-in patient-level audit script against local Set A/Set B feature caches after verifying the local Git blob SHA against GitHub; the exact committed tests also passed locally (3 passed).
- [x] Reconciled cohort totals, record-length summaries, and all 11 features' patient-availability/unadjusted-label association metrics with the existing aggregate artifact; metrics matched within (10^{-12}). Duration-stratum counts and ever-positive-label rates matched, and reported availability rates matched at displayed precision.
- [x] Recorded the local aggregate output SHA-256 and exact source/test blob SHAs in the aggregate JSON. Local caches and the full source-run output remain outside Git.
- [x] Reviewed the original Challenge paper to map Set A to hospital system A (Beth Israel Deaconess Medical Center) and Set B to hospital system B (Emory University Hospital); the paper identifies different EMR systems and describes measurement-density differences across the public cohorts.
- [ ] Obtain clinical/statistical review before choosing a final minimum-coverage policy. The 5% Set-A coverage threshold remains exploratory and must not be called optimal or clinically justified.
- [x] GitHub Actions test workflow passed on PR head `1bad4990f63387c9427770e8bdf4baf9bf4fac20` after the exact-source results, reconciliation documentation, and metric regression tests were added (run https://github.com/culprit-k/VITALIS/actions/runs/38598858712).
- [ ] Do not attribute feature shifts to specific ordering workflows or missingness mechanisms without further evidence. Keep Set B evaluation-only and do not use it for feature selection, calibration, or tuning.


## Exact-source cross-cohort evaluator reproduction (14 October 2026)

- [x] Verified that the local evaluator's Git blob SHA exactly matches the checked-in GitHub source, then executed the exact script against the local Set-A and Set-B caches for seeds 42, 123, and 2026. The three seeds were run separately after the combined invocation exceeded the runtime window.
- [x] Recorded aggregate-only results, per-seed metrics, source hashes, local output hashes, and limitations in [the exact-source JSON](../results/cross_cohort_exact_source_reproduction_2026-10-14.json); updated the [cross-cohort report](FULL_COHORT_CROSS_COHORT_RESULTS.md).
- [x] Confirmed the exact-source mean AUROC/AUPRC/Brier scores are 0.6750/0.0455/0.1659 for static features and 0.7319/0.0581/0.0972 for temporal features. Across the three training subsamples, temporal features have higher ranking metrics but lower sensitivity at the fixed 0.5 threshold; this remains retrospective benchmark evidence only.
- [x] Preserved the older reconstructed-harness JSON unchanged and documented that its metrics differ from the exact-source run. Do not present the historical values as reproduced by the checked-in CLI until the discrepancy is explained.
- [x] Recorded that Set-A-all-empty EtCO2 columns are skipped by the imputer; Set-B EtCO2 values are not used by this Set-A-trained model. Set B remains evaluation-only.
- [x] Compared historical reconstructed-harness metrics with exact-source metrics and documented the differences in [the reconciliation report](CROSS_COHORT_REPRODUCIBILITY_RECONCILIATION.md) and [JSON](../results/cross_cohort_reproducibility_reconciliation_2026-10-14.json). The root cause remains unresolved because the historical artifact lacks source/split provenance; both artifacts are preserved, and the exact-source values are canonical for the checked-in evaluator.
- [ ] Review cross-cohort calibration/domain shift with clinical/statistical supervision. The fixed 0.5 threshold is not clinically selected, and this is not prospective validation or clinical utility evidence.


## Cross-cohort reproducibility discrepancy review (14 October 2026)

- [x] Compared the older reconstructed-harness aggregate with the exact-source evaluator output. The old artifact reported static/temporal mean AUROC 0.67809/0.73569; the exact-source evaluator reported 0.67502/0.73191. AUPRC and Brier score differences are also recorded in the reconciliation report.
- [x] Added `tests/test_evaluate_cross_cohort.py` to check the evaluator's AUROC/AUPRC/Brier calculations against scikit-learn, verify the fixed 0.5 threshold confusion matrix including exact-threshold behavior, and ensure the metrics payload contains no patient-level scores or identifiers. Local focused validation: 9 tests passed across the evaluator metric tests and recalibration tests.
- [x] Confirmed the exact-source recalibration runner reproduces its stored outputs on rerun for all three seeds (seeds 42 and 123 exact equality; seed 2026 max absolute metric difference 1.5e-14). Its raw Set-B metrics agree with the exact-source evaluator to floating-point precision.
- [x] Added [a dedicated discrepancy report](CROSS_COHORT_REPRODUCIBILITY_RECONCILIATION.md) and [aggregate-only reconciliation JSON](../results/cross_cohort_reproducibility_reconciliation_2026-10-14.json). Historical results were preserved unchanged.
- [ ] Root cause of the old simple-evaluator discrepancy remains unresolved: the historical artifact lacks the source hash, environment, and training-split detail needed to attribute it to a particular difference. Do not guess or consolidate the artifacts until the old harness is recoverable.
- [ ] Obtain independent clinical/statistical review of the feature-coverage policy and cross-cohort interpretation; do not treat retrospective challenge metrics as clinical validation.


## Exact-source cross-cohort raw-score uncertainty (14 October 2026)

- [x] Extended `scripts/evaluate_cross_cohort.py` with an opt-in `--local-score-archive-dir` option. It rejects output directories inside the repository and writes only the required paired arrays (`y`, synthetic patient-group indices, static probabilities, temporal probabilities) to compressed NPZ files outside Git. Default behavior remains aggregate-only JSON.
- [x] Added regression tests for metric parity with scikit-learn, the fixed 0.5 threshold boundary, private archive path enforcement, archive schema, and vector validation. Local focused tests passed (12/12); GitHub Actions also passed on code-bearing PR head `c0064adf78c40140e65a1d7bc0603d22b25b04d6` (run https://github.com/culprit-k/VITALIS/actions/runs/38600885999).
- [x] Verified the modified evaluator and tests by Git blob SHA against GitHub; generated score archives locally for all Set-B patients for seeds 42, 123, and 2026. Model metrics matched the previously verified exact-source outputs within 2.4e-14.
- [x] Ran the checked-in paired patient-cluster bootstrap for 200 replicates per seed. Aggregate-only results are in [the JSON artifact](../results/cross_cohort_paired_patient_cluster_bootstrap_exact_source_200x3_2026-10-14.json). The archives remain outside Git.
- [x] The first unoptimized 1,000-replicate attempt exceeded the execution window; the accelerated tie-aware runner now completes the 1,000-replicate analysis in deterministic chunks. Chunk offsets were validated against a full 400-replicate run.
- [x] Generated exact-source recalibrated score vectors outside Git and completed the 1,000-replicate bootstrap for all three seeds. The 20-replicate reconstructed-harness pilot remains historical and separate.


## Exact-source recalibrated-score uncertainty checkpoint (14 October 2026)

- [x] Added an opt-in `--local-score-archive-dir` to `scripts/evaluate_cross_cohort_recalibration.py`. It refuses archive directories inside the repository and writes raw and Platt-recalibrated Set-B score vectors only to the requested local directory. Patient group values are replaced with synthetic contiguous indices.
- [x] Added tests for archive path enforcement, vector validation, archive schema, and synthetic group indices. Focused tests pass locally (15 tests across recalibration and cross-cohort evaluator suites).
- [x] Executed the updated runner for seeds 42, 123, and 2026 against the local Set-A/Set-B caches. Local runner blob SHA matches GitHub (`fe355c4b7b77b322ae5c134fe7fdc0b9cbb73200`); aggregate metrics reproduce the prior source-verified outputs to a maximum absolute difference below `1e-12` per seed. Six score archives were validated (761,995 rows, 20,000 synthetic patient groups, 10,780 positive labels each) and remain outside Git.
- [x] Preserved the earlier checked-in-runner 200-replicate analysis as a historical checkpoint: [aggregate JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_raw_and_recalibrated_exact_source_200x3_2026-10-14.json) and [report](CROSS_COHORT_BOOTSTRAP_RAW_AND_RECALIBRATED.md).
- [x] Added `scripts/bootstrap_heldout_scores_fast.py`, a Numba-accelerated, tie-aware paired patient-cluster bootstrap runner. Added the optional `bootstrap-accelerated` dependency extra and CI installation. Its 25 synthetic tied-score fixtures matched scikit-learn metrics; 7 focused tests passed locally.
- [x] Compared the accelerated implementation's first 200 replicates against the checked-in bootstrap runner for all six seed/probability-stream combinations; aggregate means and percentile endpoints matched within 4e-14 absolute difference.
- [x] Completed 1,000 valid paired patient-cluster bootstrap replicates for each of seeds 42, 123, and 2026, for both raw and Set-A-validation-Platt-recalibrated probabilities. Aggregate-only results: [1,000-replicate JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_raw_and_recalibrated_exact_source_1000x3_2026-10-14.json) and [report](CROSS_COHORT_BOOTSTRAP_RAW_AND_RECALIBRATED_1000.md). Row-level score archives and chunk differences remain outside Git.
- [x] GitHub Actions test workflow passed on code-bearing head `da7d33a43c363f24c48f77eb6ca79576175fdce9` (run https://github.com/culprit-k/VITALIS/actions/runs/38606538416), including the accelerated bootstrap tests. Audit the complete PR diff before marking it ready for review.
- [ ] Exact clean Git checkout provenance, independent methodological review, and Set-A-only justification for the exploratory feature-coverage threshold remain open. Set B stays evaluation-only; no clinical validation claim is supported.


## Release-readiness checkpoint after 1,000-replicate analysis (14 October 2026)

- [x] Exact-source raw and recalibrated uncertainty analysis completed at 1,000 replicates for each of seeds 42, 123, and 2026; aggregate JSON and interpretation report are committed.
- [x] GitHub Actions test workflow passed on code-bearing commit `da7d33a43c363f24c48f77eb6ca79576175fdce9` (run https://github.com/culprit-k/VITALIS/actions/runs/38606538416). Subsequent changes are documentation-only.
- [x] Repository-diff privacy audit: 34 changed files consist of scripts, tests, docs, workflow configuration, and aggregate JSON. No raw score archives, patient-level cache files, or PSV/CSV/parquet data files are included.
- [x] README links the final cross-cohort report and uncertainty analysis and explains the optional acceleration dependency.
- [ ] Obtain a full clean Git checkout and rerun the reproduction commands from that checkout when network/DNS access permits; current source-byte identity was verified through Git blob hashes, not a successful full clone.
- [ ] Obtain independent clinical/statistical review of the cross-cohort interpretation and exploratory Set-A feature-coverage policy. Do not call the 5% cutoff optimal or clinically justified.
- [ ] Keep PR #1 draft and unmerged until the clean-checkout/release review is complete. VITALIS remains research-only; prospective external validation and clinical oversight would be required before any clinical-use claim.


## Release-readiness audit (14 October 2026)

- [x] Inspected PR #1 metadata, full base-to-head changed-path summary, latest available CI run, and existing review submissions/threads. The PR is open, draft, and unmerged; no submitted review or inline review thread was present at audit time.
- [x] Added [the research-release readiness audit](RELEASE_READINESS_AUDIT.md), separating verified gates from outstanding blockers and explicitly limiting release claims to retrospective research evidence.
- [x] Latest available GitHub Actions run at audit start (run [38606955158](https://github.com/culprit-k/VITALIS/actions/runs/38606955158)) passed the install and test steps. This does not replace a clean local full-cohort reproduction.
- [x] Performed a changed-path privacy review: no raw cohort files, row-level NPZ score archives, or cache arrays appear in the 34-file PR diff. This is not a full repository-history or secret scan.
- [ ] Complete the fresh-clone reproduction runbook with authorized local data and record the actual checkout/environment/source hashes and reconciliation results.
- [ ] Obtain independent clinical/statistical review of split and label semantics, calibration interpretation, domain shift, bootstrap estimand, and the exploratory 5% feature-coverage rule.
- [ ] Review full repository history for accidentally committed sensitive artifacts/secrets, address all reviewer findings, and rerun CI after any code changes.
- [ ] Keep PR #1 draft and unmerged until the outstanding release gates are completed and an explicit merge decision is made. VITALIS remains research-only and is not clinically validated.


## Exact-source rerun checkpoint (14 October 2026)

- [x] Retried `git clone https://github.com/culprit-k/VITALIS.git`; it failed because the runtime could not resolve `github.com`. The fresh-clone gate remains open; do not call this a clean-checkout reproduction.
- [x] Reran the exact-source recalibration runner separately for seeds 42, 123, and 2026 using the available local Set-A/Set-B feature caches and verified source blob hashes against the PR branch. All patient/row split counts matched the previous source-verified artifact; AUROC/AUPRC matched exactly at reported precision, with maximum absolute raw metric difference below 1e-12 and recalibrated difference below 5e-15.
- [x] Added [the rerun reconciliation report](FRESH_SOURCE_RERUN_RECONCILIATION.md) and [aggregate-only JSON](../results/fresh_source_rerun_reconciliation_2026-10-14.json). Row-level score archives stayed outside the repository.
- [x] Verified GitHub Actions `tests` workflow passed on current PR head `a0103df503a574f097045a34062e5f3abf229b60` (run https://github.com/culprit-k/VITALIS/actions/runs/38608383356, completed 14 October 2026 17:39 UTC). This confirms CI for the current head but does not close the clean-clone, fresh-cache, history-wide audit, or independent-review gates.
- [ ] Complete a fresh clone and fresh cache build from authorized source data when network/DNS access permits; run the full current PR test suite from that checkout and record the checkout commit and clean status.
- [ ] Obtain independent clinical/statistical review and perform a history-wide sensitive-artifact/secret audit before deciding whether to mark PR #1 ready or merge it.


## Phase 3: online adaptive twin software (started 2026-10-14)

The next implementation layer has now been added on the existing research branch:

- [x] Add `src/vitalis/adaptive_twin.py`: causal rolling and frozen-reference baselines, normalized deviation, two-sided CUSUM for gradual drift, equal-weight physiological-system aggregation, EWMA trajectory score/direction, missingness coverage, persistence, and per-channel scale floors.
- [x] Add `src/vitalis/stream.py`: timestamp-aware observations, expected-unit validation, quality-flag rejection, per-channel freshness, out-of-order sample rejection, and session reset.
- [x] Add focused tests for baseline causality, CUSUM gradual-shift detection, per-channel scale floors, baseline-update suppression, multisystem persistence, missing data, trajectory direction, session reset, unit checks, timestamps, freshness, out-of-order samples, and end-to-end stream-to-twin integration.
- [x] Add `scripts/demo_adaptive_twin.py` and `dashboard/twin_demo.py`, deterministic CLI and interactive synthetic-data demonstrations that do not read or generate real patient records.
- [x] Document the mathematical definition, output semantics, and validation boundaries in [Adaptive twin implementation](ADAPTIVE_TWIN_IMPLEMENTATION.md).
- [x] GitHub Actions passed on commit `4b3aa798af04a0819ce1523cb9bae672dcc9dddf`, including `compileall`, the synthetic timestamped-stream smoke test, and the full pytest suite: https://github.com/culprit-k/VITALIS/actions/runs/38612764680.
- [ ] Run the full suite from a clean checkout and verify the demo from a fresh environment.
- [ ] Add edge-case tests for flatline, spikes, gradual drift, sensor replacement, irregular sampling, and conflicting or correlated channels.
- [ ] Build a supervised, leakage-safe future-outcome model with a clearly defined prediction horizon. The current challenge label's six-hour lead convention is not evidence for a calibrated 1–3 hour forecast.
- [ ] Add explicit directionality and per-channel noise/freshness configuration with evidence-based settings; current score weights and cutoffs are engineering defaults, not clinical thresholds.
- [ ] Complete independent statistical/clinical review and all repository security/reproducibility gates before considering any prospective study.

**Important boundary:** the new online component detects within-person deviation patterns; it is not yet a complete physiological digital twin, calibrated sepsis probability model, or validated time-to-deterioration predictor. Do not use it for patient care.

**Hardware gate:** do not select sensor parts or claim device performance until timestamping, units, sample quality, expected sampling policies, compute requirements, and the software validation contract have been reviewed. The current stream adapter defines a software input boundary, not a hardware specification.


## Phase 4: supervised future-label forecasting (started 2026-10-14)

- [x] Add a separate target builder that predicts whether a positive Challenge SepsisLabel occurs within the next 1, 3, or 6 hourly rows, while the current label is zero.
- [x] Exclude current-positive rows and each patient's final H rows; enforce contiguous patient blocks and never shift labels across patients.
- [x] Add patient-disjoint train/validation/test modeling with training-only preprocessing, fixed reference threshold, aggregate-only outputs, patient-level warning burden, and patient-cluster bootstrap intervals.
- [x] Add tests for horizon alignment, patient-boundary isolation, eligible tail rows, alert refractory periods, warning-window coverage, and bootstrap intervals.
- [x] Document the exact target semantics and limitations in [Horizon forecasting](HORIZON_FORECASTING.md).
- [x] GitHub Actions passed on commit `2b56ad2a91ede9081ae56e51ed72b9dcfaf4aa6e`: https://github.com/culprit-k/VITALIS/actions/runs/38614183618. All 118 tests passed, including an end-to-end synthetic-PSV horizon training test.
- [ ] Run the full-cohort 1/3/6-hour experiments from a clean environment using the authorized local dataset; record aggregate-only outputs and split seed.
- [ ] Repeat on predeclared seeds and evaluate train-Set-A/test-Set-B generalization without tuning on Set B.
- [ ] Review forecast-window coverage, alert burden per at-risk patient-day, warning time relative to challenge-label entry, and patient-cluster uncertainty before interpreting any result.
- [ ] Obtain independent clinical/statistical review. These labels do not provide an independent onset timestamp, and no clinical alert policy is established.

**Interpretation boundary:** the new model forecasts entry into the Challenge SepsisLabel-positive window. Because the challenge label already incorporates a six-hour lead convention, a 1/3/6-hour forecast here is not a claim of sepsis onset prediction within 1/3/6 hours. All threshold, refractory, and alert metrics are retrospective research settings, not clinical operating points.


## Phase 5: full-cohort horizon cross-cohort evaluation (started 2026-10-14)

- [x] Add `scripts/evaluate_horizon_cross_cohort.py` to train static and temporal future-label models on a patient-disjoint Set A training subset and evaluate all eligible Set B patients.
- [x] Enforce expected official cohort counts and feature-schema agreement; fail closed when the cache does not match the source cohort.
- [x] Keep Set B evaluation-only: no fitting, feature selection, calibration, or threshold tuning on Set B.
- [x] Add synthetic-cache tests for target alignment and end-to-end Set A→Set B evaluation.
- [x] Document cache build chunks and the full-cohort run in [Horizon cross-cohort execution](HORIZON_CROSS_COHORT_EXECUTION.md).
- [x] Confirm GitHub Actions passes for the cross-cohort horizon tests: [run #513](https://github.com/culprit-k/VITALIS/actions/runs/38616619520), 120 tests passed.
- [x] Build both official feature caches locally, outside Git, from verified Set A and Set B archives; counts and schemas passed integrity checks.
- [x] Run all nine seed × horizon combinations (seeds 42, 123, 2026; horizons 1, 3, 6 hours) and retain aggregate-only JSON outside the repository; elapsed time 384.8 seconds.
- [x] Review model metrics, patient-level warning burden, and patient-cluster intervals without tuning on Set B; results are recorded in [full-cohort horizon results](FULL_COHORT_HORIZON_CROSS_COHORT_RESULTS.md).
- [ ] Obtain independent statistical/clinical review before any clinical claim.

**Current execution boundary:** the code and synthetic tests can be validated through GitHub Actions, but the official full-cohort runs require the authorized local Set A and Set B feature caches. Those caches and any row-level predictions must not be uploaded to GitHub. The horizon target remains future Challenge-label entry, not independently observed sepsis onset.


### Full-cohort horizon result summary (2026-10-14)

- The nine seed × horizon runs completed on the full verified caches. Set B remained evaluation-only.
- Static mean AUROC/AUPRC across seeds was 0.6634/0.00379 (1 h), 0.6813/0.01358 (3 h), and 0.6868/0.02859 (6 h). Temporal means were 0.6569/0.00317, 0.6800/0.01264, and 0.6864/0.02643, respectively.
- At the fixed 0.5 threshold, PPV remained very low and alert burden high; neither model should be promoted as a clinical alert policy.
- Class-weighted model probabilities were not calibrated; Brier scores were much worse than a constant-prevalence predictor. A training-only calibration protocol and independent statistical review remain required.
- See [full results and limitations](FULL_COHORT_HORIZON_CROSS_COHORT_RESULTS.md) and the committed [aggregate-only result JSON](../results/horizon_cross_cohort_2026-10-14.json). Raw caches and individual predictions were not uploaded.

### Horizon calibration results (2026-10-15)

- [x] Completed all nine horizon × seed combinations on the verified full Set A and Set B caches: 18 static/temporal model fits, 217.7 seconds summed runtime, and zero captured fit warnings.
- [x] Added [aggregate-only calibration metrics](../results/horizon_calibration_summary_2026-10-15.json) and the [calibration/operating-point report](HORIZON_CALIBRATION_RESULTS_2026-10-15.md); updated the [protocol](HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md).
- [x] Used patient-disjoint Set A 60/20/20 training/calibration/untouched-holdout partitions. Platt recalibration was fit only on Set A calibration patients. Set B remained final evaluation only and no threshold was selected from it.
- [x] Recalibration greatly reduced raw class-weighted Brier scores. However, calibrated Set-B Brier scores remained slightly worse than the constant-prevalence reference for every horizon/model pair; probabilities are not established as adequate clinical risk estimates.
- [x] Added `src/vitalis/calibration_uncertainty.py` to compute patient-cluster percentile intervals for calibrated Brier score, log loss, mean probability, fixed-bin ECE, Brier-minus-prevalence-reference, and paired calibrated-minus-raw Brier difference; wired it into the horizon calibration runner with a default of 200 replicates.
- [x] Added focused reproducibility, scikit-learn metric-parity, input-validation, patient-boundary, and aggregate-only tests in `tests/test_calibration_uncertainty.py`.
- [x] Completed the updated full-cohort uncertainty workflow in nine bounded horizon/seed invocations: 200 patient-cluster bootstrap replicates for each of 18 model/horizon/seed fits; 235.5 seconds summed runtime and zero captured fit warnings. Results: [uncertainty report](HORIZON_CALIBRATION_UNCERTAINTY_RESULTS_2026-10-15.md) and [aggregate-only JSON](../results/horizon_calibration_uncertainty_summary_2026-10-15.json).
- [x] Paired calibrated-minus-raw Brier intervals were below zero in every seed/model/horizon run. Many intervals for calibrated Brier minus the prevalence-reference score crossed zero, so added calibration is not proof of adequate risk estimation.
- [ ] Next: define a utility-based operating-point framework on development data with explicit costs for missed windows and alerts; do not select thresholds on Set B. Any selected policy needs a new independent evaluation cohort.
- [ ] Independent clinical/statistical review, external/prospective validation, and governance review remain required. VITALIS remains research-only.

## Phase 6: calibration uncertainty review (15 October 2026)

- [x] Add patient-cluster percentile bootstrap uncertainty for Set B calibrated Brier score, log loss, mean predicted probability, fixed-bin ECE, Brier-minus-prevalence-reference, and paired calibrated-minus-raw Brier difference.
- [x] Run all nine predeclared seed × horizon combinations (seeds 42, 123, 2026; horizons 1, 3, 6 h) with 200 patient-cluster bootstrap replicates per model/horizon/seed; 18 fitted model combinations, 3,600 bootstrap replicates total.
- [x] Preserve Set B as final evaluation only. Calibration remains fit on patient-disjoint Set A calibration patients; no threshold was selected from Set B.
- [x] Record aggregate-only results in [calibration uncertainty report](HORIZON_CALIBRATION_UNCERTAINTY_RESULTS_2026-10-15.md) and [JSON](../results/horizon_calibration_uncertainty_summary_2026-10-15.json).
- [x] Results support a clear reduction in Brier score after Platt recalibration versus raw class-weighted probabilities, but do not establish adequate clinical calibration or robust improvement over a constant-prevalence Brier reference. The seed-specific CI envelopes are descriptive, not pooled intervals.
- [x] Completed a predeclared paired patient-cluster comparison of Platt-calibrated static versus temporal Set-B predictions for AUROC, AUPRC, Brier score, and log loss; report and aggregate-only JSON are linked below. No threshold or model setting was selected from Set B.
- [ ] Independent statistical/clinical review, external/prospective validation, and governance review remain required. VITALIS remains research-only.

## Phase 7: paired model comparison (15 October 2026)

- [x] Add a paired patient-cluster bootstrap comparing static and temporal Platt-calibrated probabilities on identical Set-B eligible rows.
- [x] Report temporal-minus-static differences for AUROC, AUPRC, Brier score, and log loss; resample whole patients and precompute score-tie groups for efficient bootstrap calculation.
- [x] Add unit tests against scikit-learn point metrics and explicit patient-resampling intervals, plus a synthetic end-to-end evaluator test.
- [x] Run all nine seed × horizon combinations with 200 paired bootstrap replicates per run (1,800 paired replicates); 319.0 seconds summed runtime and zero captured fit warnings.
- [x] Commit [paired comparison results](HORIZON_PAIRED_MODEL_COMPARISON_RESULTS_2026-10-15.md) and [aggregate-only JSON](../results/horizon_paired_model_comparison_aggregate_2026-10-15.json).
- [x] Findings: temporal AUROC differences were positive with seed-specific intervals above zero at 1 h and 6 h, but not consistently at 3 h; AUPRC intervals overlapped zero at all horizons; temporal log loss was lower across all horizons; Brier differences were inconclusive at 1 h and 3 h and favored temporal at 6 h. These are descriptive retrospective comparisons, not grounds to select a model using Set B.
- [x] Defined and integrated a cost-sensitive utility framework on the patient-disjoint Set-A operating-point holdout. It reports sensitivity, PPV, alerts per at-risk patient-day, missed/covered forecast-positive windows, window coverage, and label-relative warning time across explicit missed-window cost scenarios. Default ratios (1, 10, 100, 500, 1,000 per alert-cost unit) are illustrative, not clinically elicited. See [utility framework](UTILITY_OPERATING_POINT_FRAMEWORK.md) and [operating-point protocol](HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md).
- [x] Completed all nine seed × horizon utility-focused runs on the available local Set-A/Set-B caches for both static and temporal models (18 fits; 249.7 seconds summed; zero captured fit warnings). Aggregate-only results: [utility report](HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md) and [JSON](../results/horizon_utility_operating_point_aggregate_2026-10-15.json). The local reconstructed working copy is not claimed as byte-identically verified exact-source execution; these reruns used 20 bootstrap replicates for ancillary uncertainty summaries.
- [x] Prepared [the independent utility-cost review checklist](UTILITY_COST_REVIEW_CHECKLIST.md) to make external review of cost assumptions, label semantics, and metric interpretation actionable.
- [ ] Obtain independent clinical/statistical justification of cost ratios and review the results before any policy choice. Do not use Set B to select a threshold; reserve a new independent cohort for final evaluation.
- [ ] Independent clinical/statistical review, external/prospective validation, and governance review remain required. VITALIS remains research-only.



## Phase 8: utility-based operating-point framework (15 October 2026)

- [x] Add a cost-sensitive operating-point function that compares missed forecast-positive windows against total alert burden under explicit, configurable cost ratios: `src/vitalis/utility.py`.
- [x] Integrate utility summaries into the horizon calibration evaluator, limited to the untouched patient-disjoint Set-A operating-point holdout. Set B remains evaluation-only and cannot rank or select thresholds.
- [x] Add focused unit tests for required metrics, cost-scenario reporting, and invalid inputs; add an integration assertion to the evaluator test.
- [x] Document the cost definition, illustrative scenarios, selection discipline, and limitations in [the utility framework](UTILITY_OPERATING_POINT_FRAMEWORK.md) and [the calibration protocol](HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md).
- [ ] Confirm the new tests and full CI suite pass on the latest branch head; repair any failures before treating this milestone as complete.
- [x] Completed the nine-run utility-focused analysis using available local caches and committed aggregate-only results at [the report](HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md) and [JSON](../results/horizon_utility_operating_point_aggregate_2026-10-15.json). Provenance remains qualified: the run used a reconstructed local working copy, not a byte-identically verified checkout; 20 bootstrap replicates were ancillary only.
- [x] Keep raw data, caches, and row-level predictions outside Git; committed output is aggregate-only.
- [ ] Obtain independent clinical/statistical review of relative cost scenarios. Current defaults (1, 10, 100, 500, 1,000 missed-window units per alert-cost unit) are illustrative engineering assumptions, not validated utility weights.
- [ ] Freeze any development policy only after cost assumptions and selection rules are reviewed and predeclared. Do not select a threshold on Set B, whose results have already been inspected; a new independent cohort is required.

**Boundary:** the utility score is a retrospective Challenge-label proxy, not clinical utility. The target is entry into the Challenge SepsisLabel-positive window, not independently observed biological onset. VITALIS remains research-only and must not guide patient care.


## Phase 9: independent-evaluation readiness (15 October 2026)

- [x] Draft the [independent-cohort evaluation protocol](INDEPENDENT_EVALUATION_PROTOCOL.md), including model freeze, independent event definition, predeclared metrics, reproducibility requirements, and staged evaluation boundaries.
- [x] Link the protocol and [utility-cost review checklist](UTILITY_COST_REVIEW_CHECKLIST.md) from the README.
- [ ] Obtain independent clinical/statistical review of the utility assumptions and endpoint semantics; record the reviewer's decision and required changes.
- [ ] Complete a clean-checkout, pinned-environment reproduction and history-wide privacy/secret audit; runtime DNS limitations have prevented a verified clean clone so far.
- [ ] Obtain data-governance/ethics approval and a genuinely new independent cohort with clinically defined/adjudicated event timing before external validation. Set B is already inspected and must not be reused for threshold selection.
- [ ] Freeze the model, calibration, threshold, refractory policy, endpoints, and analysis plan before accessing independent-cohort outcomes. Prospective silent-mode and clinical-impact studies require separate approvals and are not authorized by this protocol.

**Boundary:** these are project-readiness tasks, not evidence of clinical readiness. VITALIS remains research-only and must not guide patient care.
