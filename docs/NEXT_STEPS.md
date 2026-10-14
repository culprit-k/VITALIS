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
