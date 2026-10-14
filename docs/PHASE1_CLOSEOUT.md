# VITALIS Phase 1 closeout: software and exploratory evidence

**Phase 1 software/research foundation is complete within the defined exploratory scope. Clinical-validation and hardware-readiness gates remain open.**

## What was completed

- Research-first repository, dataset protocol, data dictionary, model card, baseline pipeline, temporal feature pipeline, and reproducible workflow.
- First experimental VITALIS-PB patient-baseline deviation feature generator and matched three-model comparison.
- Unit tests and GitHub Actions CI for the feature generator and comparison helpers; the latest repository checks passed.
- Local exploratory evaluation on a deterministic patient sample using three patient-disjoint split seeds and paired patient-cluster bootstrap comparisons.
- A second execution of the local evaluation script reproduced the same aggregate JSON byte-for-byte; see the [reproducibility manifest](../results/phase1_local_reproducibility_manifest.json).
- Aggregate-only reporting. Raw PhysioNet files, patient identifiers, and patient-level predictions were not committed.

## Dataset and protocol

- Dataset: PhysioNet/CinC Challenge 2019 training set A, local copy.
- Available patient files: 20,336. Deterministic sample: 500 patients, sampled without replacement from sorted file paths with seed 20261014.
- Sample contains 20,010 hourly rows and 439 positive challenge-label rows (2.19%).
- Three patient-disjoint train/validation/test splits: seeds 42, 123, and 2026; each split uses 320 train, 80 validation, and 100 test patients.
- Models: logistic regression with class weighting, training-fold median imputation with missingness indicators, standard scaling, and max_iter=1000.
- Compared feature sets: static; temporal (lag, change, trailing mean); temporal plus causal personal-baseline deviation features.
- Metrics: AUROC, average precision, Brier score, and log loss. Paired patient-cluster bootstrap: 200 replicates per comparison per split.
- Challenge `SepsisLabel` is used as supplied and is not shifted again. It is a challenge-defined label convention, not an independently observed clinical onset.

## Results across three split seeds

| Model | AUROC (mean ± SD) | Average precision (mean ± SD) | Brier score ↓ (mean ± SD) | Log loss ↓ (mean ± SD) |
|---|---:|---:|---:|---:|
| Static | 0.7244 ± 0.0551 | 0.1018 ± 0.0107 | 0.1816 ± 0.0301 | 0.5683 ± 0.0897 |
| Temporal | 0.6745 ± 0.0238 | 0.0776 ± 0.0121 | 0.1518 ± 0.0353 | 0.5352 ± 0.1229 |
| Temporal + personal baseline (VITALIS-PB) | 0.5847 ± 0.0215 | 0.0525 ± 0.0135 | 0.1256 ± 0.0192 | 0.7054 ± 0.3011 |

SD is variability across three split seeds, **not a confidence interval**. Paired patient-cluster bootstrap intervals are recorded in the aggregate JSON artifact.

## Interpretation and decision

1. In this exploratory sample, the static model had better mean AUROC and average precision than the temporal and personalized variants.
2. The personalized model had a lower mean Brier score but substantially worse mean log loss. This mixed result does not establish better calibration or clinical usefulness.
3. The patient-baseline feature hypothesis has **not** demonstrated overall improvement and should not be the default model. Keep it experimental pending investigation of feature scaling, missingness, calibration, and personal-variability definitions.
4. This is a 500-patient sampled internal evaluation, not full-cohort or external validation, a prospective study, or a clinical-utility evaluation.
5. No threshold was selected, and no patient-event sensitivity, detection lead time, or clinically meaningful false-alarm rate is claimed.

## Phase 1 exit status

- [x] Research repository, protocol, and baseline workflows established.
- [x] Static, temporal, and patient-baseline feature approaches implemented and unit-tested.
- [x] Latest main-branch GitHub Actions checks passed.
- [x] Three patient-level split seeds evaluated locally with matched cohorts and paired patient-cluster uncertainty estimates.
- [x] A repeated local run reproduced the aggregate JSON byte-for-byte; SHA-256 and protocol are recorded in the reproducibility manifest.
- [x] Negative and mixed findings documented without claiming model superiority.
- [x] Raw dataset files, patient identifiers, and patient-level predictions excluded from public artifacts.
- [ ] Canonical repository runner still needs to be executed against the local dataset and reconciled with the recorded local artifact.
- [ ] Calibration and missingness/subgroup robustness analyses remain next research tasks.
- [ ] Full-cohort and external validation remain future work.

## Hardware gate

**Phase 1 is complete as a software/research foundation and exploratory-evaluation milestone, but hardware readiness is not approved.** Do not buy custom hardware or describe VITALIS as clinically ready on the basis of these results. The next step is to reconcile the canonical runner, analyze calibration and missingness, and establish a defensible signal specification. Any later prototype remains research-only and requires sensor validation, risk management, appropriate ethics/data governance, and clinical supervision before patient-facing use.

## Reproducibility artifacts

- [Three-model runner](../scripts/run_phase1_repeated_comparison.py)
- [Aggregate Phase 1 summary](../results/phase1_500_patient_three_seed_summary.json)
- [Local rerun reproducibility manifest](../results/phase1_local_reproducibility_manifest.json)
- Reproduce with: `python scripts/run_phase1_repeated_comparison.py /path/to/training_setA --sample-size 500 --sampling-seed 20261014 --split-seeds 42 123 2026 --bootstrap-replicates 200 --output results/phase1_reproduction.json`
- [VITALIS-PB algorithm specification](VITALIS_PB_ALGORITHM.md)
- [Model evaluation plan](MODEL_EVALUATION.md)
- [Dataset protocol](COHORT_PROTOCOL.md)
