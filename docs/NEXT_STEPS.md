# VITALIS next steps and current status

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
- [x] Reported seed-specific intervals separately without pooling test rows across split seeds. Only 20 replicates per seed completed, so intervals are preliminary and too coarse for final inferential claims. [ ] Repeat with 200–1,000 replicates after runtime optimization.


## Preliminary full-cohort uncertainty results

- [x] Committed aggregate-only paired patient-cluster bootstrap results for seeds 42, 123, and 2026. Temporal AUROC differences were positive across all three seeds; Brier differences were negative; AUPRC interval crossed zero for seed 123. See [report](FULL_COHORT_PAIRED_BOOTSTRAP.md).
- [ ] Increase bootstrap replicates to at least 200–1,000 and verify the checked-in source bytes are the ones actually executed before treating the intervals as final research results.


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
- [ ] A 1,000-replicate full-cohort attempt exceeded the local five-minute execution window before producing a complete artifact. Do not treat it as a result. Further optimize runtime or run the bootstrap over retained held-out score vectors before increasing repetitions.
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
- [ ] Run the checked-in script from an exact repository checkout against the local caches and reconcile results; the first local analysis used a reconstructed working copy, so source-byte identity remains open.
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
- [ ] Execute the checked-in runner from an exact repository checkout against local set-A/set-B caches and reconcile its aggregate output against the prior reconstructed-harness artifact. Do not claim exact source reproduction until that run is performed.


## Current handover checkpoint — cross-cohort recalibration (14 October 2026)

- [x] Confirmed the latest main-branch workflow run for `Track checked-in cross-cohort recalibration runner` completed successfully: https://github.com/culprit-k/VITALIS/actions/runs/38583831584.
- [x] Confirmed the preceding documentation update workflow also passed: https://github.com/culprit-k/VITALIS/actions/runs/38583816179.
- [x] The checked-in runner uses patient-disjoint 60/20/20 partitions in set A, fits Platt recalibration on set-A validation predictions only, scores set B in chunks, and writes aggregate-only results. Set B is not used for fitting or threshold selection.
- [ ] Run `scripts/evaluate_cross_cohort_recalibration.py` from a byte-identical checkout against the local set-A and set-B caches; compare the resulting aggregate JSON against `results/cross_cohort_validation_A_recalibration_test_B_3seed_2026-10-14.json`. Current local network DNS has prevented establishing source-byte identity, so do not claim exact reproduction yet.
- [ ] Add paired patient-cluster uncertainty intervals for cross-cohort results using held-out set-B predictions, while keeping score vectors and patient group IDs outside Git. Preserve split-specific results and avoid treating three seed SDs as confidence intervals.
- [ ] Audit subgroup performance and calibration without using set B to tune model or recalibrator. Suppress small cells and frame results as exploratory.
- [ ] Document the final pre-specified evaluation protocol and obtain statistical/clinical governance review before any prospective or patient-facing study. VITALIS remains research-only.


## Cross-cohort paired uncertainty pilot (14 October 2026)

- [x] Generated local-only held-out Set B score archives for seeds 42, 123, and 2026; archives include labels, patient groups, and raw/recalibrated model scores and remain outside Git.
- [x] Ran an exploratory paired patient-cluster bootstrap comparing temporal vs static models for raw and Set-A-validation-recalibrated probabilities (20 replicates per seed/stream).
- [x] Committed aggregate-only pilot intervals: [JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_20x3_2026-10-14.json) and [report](CROSS_COHORT_RECALIBRATION_PILOT.md).
- [ ] Upgrade the bootstrap to at least 1,000 replicates per seed/stream using an optimized implementation; current 20-replicate intervals are rough pilot estimates only.
- [ ] Run score generation from an exact repository checkout and reconcile the aggregate results; current score-generation source identity remains unverified.
- [ ] Continue with a pre-specified subgroup robustness audit, suppress small cells, and keep Set B out of all model/recalibrator/threshold tuning.
