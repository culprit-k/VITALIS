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

## Next software/research actions

1. Confirm the latest CI runs for the calibration, split-isolation, and alert-burden regression tests.
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
