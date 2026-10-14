# VITALIS Phase 1 closeout: software and exploratory evidence

**Status: Phase 1 software/research foundation completed; clinical-validation and hardware-readiness gates remain open.**

## What was completed

- Research-first repository, dataset protocol, data dictionary, model card, reproducible workflow, baseline and temporal feature pipelines.
- First experimental VITALIS-PB patient-baseline deviation feature generator and matched three-model comparison.
- Unit tests and GitHub Actions CI for the new feature generator and model-comparison wiring.
- Local exploratory evaluation on a deterministic sample, using patient-disjoint splits and paired patient-cluster bootstrap intervals.
- Aggregate-only reporting. Raw PhysioNet files, patient identifiers, and patient-level predictions were not committed.

## Dataset and protocol for this closeout run

- Dataset: PhysioNet/CinC Challenge 2019 training set A, local copy.
- Available patient files: 20,336. Deterministic sample: 500 patients, sampled without replacement from sorted file paths with seed 20261014.
- Sample contains 20,010 hourly rows and 439 positive challenge-label rows (2.19%).
- Three patient-disjoint train/validation/test splits: split seeds 42, 123, 2026; each split uses 320 train, 80 validation, and 100 test patients.
- Models: logistic regression with class weighting, training-fold median imputation with missingness indicators, standard scaling, and max_iter=1000.
- Compared feature sets: static; temporal (lag, change, trailing mean); temporal plus causal personal-baseline deviation features.
- Metrics: AUROC, average precision, Brier score, and log loss. Paired patient-cluster bootstrap: 200 replicates per model comparison per split.
- Challenge `SepsisLabel` is used as supplied and is not shifted again. It is a challenge-defined label convention, not an independently observed clinical onset.

## Results across the three split seeds

| Model | AUROC (mean ± SD) | Average precision (mean ± SD) | Brier score ↓ (mean ± SD) | Log loss ↓ (mean ± SD) |
|---|---:|---:|---:|---:|
| Static | 0.7244 ± 0.0551 | 0.1018 ± 0.0107 | 0.1816 ± 0.0301 | 0.5683 ± 0.0897 |
| Temporal | 0.6745 ± 0.0238 | 0.0776 ± 0.0121 | 0.1518 ± 0.0353 | 0.5352 ± 0.1229 |
| Temporal + personal baseline (VITALIS-PB) | 0.5847 ± 0.0215 | 0.0525 ± 0.0135 | 0.1256 ± 0.0192 | 0.7054 ± 0.3011 |

SD is variability across three split seeds, **not a confidence interval**. Paired patient-cluster bootstrap intervals are recorded in the associated aggregate JSON artifact for each split and metric.

## Interpretation and decision

1. In this exploratory sample, the static model had better mean AUROC and average precision than the temporal and personalized variants.
2. The personalized model had a lower mean Brier score but substantially worse mean log loss. This disagreement is a warning not to infer that its probabilities are better calibrated from one metric alone; calibration analysis is still required.
3. The patient-baseline feature hypothesis has **not** demonstrated an overall improvement and should not be the default model. Keep it experimental and investigate feature scaling, missingness, calibration, and the definition of personal variability before reconsidering it.
4. This is a 500-patient sampled internal evaluation, not a full-cohort rerun, external validation, prospective study, or clinical utility evaluation.
5. No threshold was selected, and no patient-event sensitivity, detection lead time, or clinically meaningful false-alarm rate is claimed.

## Phase 1 exit status

- [x] Repository and research documentation established.
- [x] Static, temporal, and personal-baseline feature approaches implemented.
- [x] Automated tests and GitHub Actions CI for the algorithm/comparison wiring passed on the current main commit.
- [x] Three patient-level split seeds evaluated locally with matched cohorts and paired patient-cluster uncertainty estimates.
- [x] Negative and mixed findings documented rather than claiming model superiority.
- [x] Patient-level predictions and raw dataset files excluded from public artifacts.
- [ ] Full-cohort canonical rerun and independent external validation remain future work; they are not represented as completed.
- [ ] Calibration/subgroup analyses and a clinically justified alert threshold require further research and expert review.

## Hardware gate

**Do not buy custom hardware or describe VITALIS as clinically ready on the basis of these results.** The next sensible work is software analysis and design specification: investigate why temporal/personalized features underperform on this sample, evaluate calibration and missingness, and define sensor signal-quality and data-interface requirements. Any later prototype remains research-only and would require sensor validation, risk management, appropriate ethics/data governance, and clinical supervision before patient-facing use.

## Reproducibility artifacts

- Aggregate experiment JSON: [phase1_500_patient_three_seed_summary.json](../results/phase1_500_patient_three_seed_summary.json)
- Algorithm specification: [VITALIS-PB algorithm](VITALIS_PB_ALGORITHM.md)
- Evaluation plan: [model evaluation plan](MODEL_EVALUATION.md)
- Dataset protocol: [cohort protocol](COHORT_PROTOCOL.md)
