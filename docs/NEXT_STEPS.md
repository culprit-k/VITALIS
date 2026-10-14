# VITALIS next steps and current status

## Phase 1 status: completed within exploratory scope

- [x] Established research repository, dataset protocol, model card, baseline pipeline, tests, and reproducible workflow.
- [x] Implemented and tested static, temporal, and first patient-baseline deviation feature sets.
- [x] Added the Phase 1 closeout report and aggregate-only three-seed evaluation: [Phase 1 report](PHASE1_CLOSEOUT.md), [summary JSON](../results/phase1_500_patient_three_seed_summary.json).
- [x] Evaluated a deterministic 500-patient sample using three patient-disjoint split seeds and paired patient-cluster bootstrap comparisons.
- [x] Repeated the local evaluation and verified byte-for-byte reproducibility of the aggregate output; see [reproducibility manifest](../results/phase1_local_reproducibility_manifest.json).
- [x] Documented negative/mixed findings without claiming that VITALIS-PB improves the baseline.
- [x] Latest main-branch GitHub Actions checks passed.
- [ ] Execute the canonical repository runner against the local dataset and reconcile its output with the recorded artifact.
- [ ] Calibration and missingness/subgroup robustness analyses.
- [ ] Full-cohort and external validation remain future work, not completed milestones.

## Main finding

In the 500-patient exploratory sample, the static model had the best mean AUROC (0.7244) and average precision (0.1018). The temporal model had lower discrimination, while the personalized model had the lowest mean AUROC (0.5847) and average precision (0.0525). The personalized model's lower Brier score but higher log loss is mixed evidence, not proof of good calibration. These results do not justify advancing the personalized model as the default or claiming clinical benefit.

## Phase 2 status: started

- [x] Added aggregate calibration and predictor-missingness helper functions with unit tests: [Phase 2 plan](PHASE2_PLAN.md).
- [ ] Confirm GitHub Actions passes for the new helper tests.
- [ ] Execute the canonical Phase 1 runner on the local dataset and reconcile its output with the committed aggregate artifact; do not assume the local equivalent is identical.
- [ ] Run held-out calibration and split-specific missingness diagnostics; keep recalibration fit on validation data only.
- [ ] Conduct prespecified robustness checks and exploratory subgroup analysis with small-cell safeguards.
- [ ] Consider full-cohort execution only after reproducibility and memory/runtime checks; external validation remains separate.
- [ ] Obtain clinical/statistical supervision and governance review before prospective or patient-facing research.

## Next software/research actions

1. Confirm CI and test the new calibration helpers.
2. Reconcile the canonical runner with the recorded Phase 1 artifact.
3. Add the held-out calibration/missingness runner with validation-only recalibration, then execute it locally.
4. Conduct prespecified robustness checks before considering a larger/full-cohort run.
5. Obtain clinical/statistical supervision and governance review before any prospective or patient-facing research.

## Hardware gate

No custom hardware purchases are recommended from these results alone. Sensor selection and interface planning can be drafted, but hardware prototyping should follow a clearer software signal specification and research justification. VITALIS remains research-only, not a medical device or clinical decision tool.

## Innovation and IP

- [x] Defined and implemented a mathematical patient-baseline deviation hypothesis as an experimental feature generator.
- [x] Evaluated it against static and temporal feature sets on matched patient-level splits with paired patient-cluster uncertainty estimates.
- [ ] Improve or reject the hypothesis based on further analysis; no novelty or patentability claim is supported without separate prior-art and IP review.

## Safety boundary

VITALIS is not validated for diagnosis, triage, treatment, or real patient-care decisions. No patient-level records or predictions belong in this public repository.
