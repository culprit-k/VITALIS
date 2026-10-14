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
- [ ] Full-cohort and external validation remain future work, not completed milestones.

## Main finding

In the 500-patient exploratory sample, the static model had the best mean AUROC (0.7244) and average precision (0.1018). The temporal model had lower discrimination, while the personalized model had the lowest mean AUROC (0.5847) and average precision (0.0525). The personalized model's lower Brier score but higher log loss is mixed evidence, not proof of good calibration. These results do not justify advancing the personalized model as the default or claiming clinical benefit.

## Phase 2 status: exploratory analysis and aggregate reconciliation complete; strict source-byte identity open

Formal closeout: [Phase 2 closeout report](PHASE2_CLOSEOUT.md). Aggregate-metric reconciliation is complete; strict byte-for-byte source identity remains a documented reproducibility exception.

- [x] Added aggregate calibration and predictor-missingness helper functions with unit tests: [Phase 2 plan](PHASE2_PLAN.md).
- [x] GitHub Actions passed for the Phase 2 helper tests and runner (latest verified run: https://github.com/culprit-k/VITALIS/actions/runs/38549292731).
- [x] Execute runner logic mirrored from checked-in source on the local dataset and reconcile aggregate outputs; split counts and feature counts match, with small metric differences documented in the closeout report. The repository helper assigns reliability bins using original probabilities; the corrected local aggregate artifact records that convention. Strict byte-for-byte source verification remains blocked by local DNS.
- [x] Run held-out calibration and split-specific missingness diagnostics; recalibration was fit on validation data only. Results are exploratory and show unstable recalibration.
- [x] Run an exploratory age/gender and missingness-stratified audit with small-cell suppression; see the Phase 2 results report. Results are unstable and not fairness/safety evidence.
- [ ] Consider full-cohort execution only after exact runner reconciliation and memory/runtime checks; external validation remains separate.
- [ ] Obtain clinical/statistical supervision and governance review before prospective or patient-facing research.

## Leakage/evaluation audit (2026-10-14)

- [x] Reviewed patient-level split isolation, training-only preprocessing/feature selection, fixed threshold handling, label timing, temporal feature assumptions, and alert-burden interpretation. See [leakage and evaluation audit](LEAKAGE_EVALUATION_AUDIT.md).
- [x] Added regression tests for overlapping patient splits and threshold/alert-burden calculations; CI verification pending for the latest commits.
- [ ] Revisit the chronological-row assumption if any new data loader or dataset format is introduced.

## Full-cohort data-integrity gate (2026-10-14)

- [x] Added an aggregate-only dataset integrity checker and unit tests: `scripts/check_dataset_integrity.py` and `tests/test_dataset_integrity.py`.
- [x] Ran the checker over all 20,336 `training_setA` patient files: 790,215 rows; 17,136 positive challenge-label rows; zero invalid target rows, empty files, or column-set mismatches. See [integrity audit JSON](../results/phase3_training_setA_integrity_audit.json).
- [ ] Direct execution of the checked-in full-cohort model CLI and strict source-byte verification remain open. A full-cohort calibration run exceeded the five-minute execution window without an artifact; a second full-cohort seed-123 static/temporal attempt also timed out before completing and is not counted as a result. The existing seed-42 full-cohort result remains a separate optimized local harness run, not a checked-in CLI execution.

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
- [ ] Build and test a repository-native, cache-backed multi-seed runner with explicit seed/output arguments, bounded memory, and aggregate-only output; then verify it against these local results.
- [ ] Add paired patient-cluster uncertainty intervals across matched test predictions from each seed; current multi-seed summary cannot estimate paired differences because only aggregate outputs were retained for seeds 123 and 2026.
- [ ] Perform external validation and obtain clinical/statistical supervision before any prospective or patient-facing study.


## Cache-backed reproducible multi-seed runner

- [x] Added `scripts/build_feature_cache.py` to build a local memory-mapped feature cache in patient-index chunks; raw dataset and cache must remain outside Git.
- [x] Added `scripts/evaluate_cached_multiseed.py` to evaluate patient-disjoint splits and write aggregate-only results for multiple seeds.
- [x] Added metric tests for the cached evaluator: `tests/test_cached_multiseed.py`.
- [ ] Run the repository-native scripts against the full local dataset and compare their outputs with [the prior exploratory summary](FULL_COHORT_MULTISEED_RESULTS.md). Prior results came from local optimized harnesses; source-level equivalence has not yet been verified.
- [ ] Ensure the cache is complete before evaluation: every chunk marker must exist, and metadata must match the dataset file list. Do not commit cache files, row-level predictions, or patient identifiers.
