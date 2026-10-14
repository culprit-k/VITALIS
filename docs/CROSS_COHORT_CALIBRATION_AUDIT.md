# Cross-cohort calibration audit: train on set A, test on set B

Date: 14 October 2026

## Why this check matters

The earlier cross-cohort experiment found better ranking metrics for temporal features on training_setB, but Brier scores and fixed-threshold behavior raised concerns about the meaning of raw probabilities. This audit evaluates probability quality descriptively on held-out set B. **It does not fit a recalibrator or select a threshold on set B.**

## Data and method

- Training set A: 20,336 patients, 790,215 hourly rows, 17,136 positive hourly challenge-label rows.
- Held-out set B: 20,000 patients, 761,995 hourly rows, 10,780 positive hourly challenge-label rows (1.415% positive hourly-label prevalence).
- Three patient-level training-subset seeds: 42, 123, and 2026. Models trained on 60% of set A patients; the remaining set A patients were unused; all set B patients were evaluated.
- Static and temporal logistic-regression models used median imputation, missingness indicators, standard scaling, and balanced class weights.
- Reported calibration intercept/slope and reliability bins are descriptive estimates on the held-out set. They must not be mistaken for a recalibration procedure.

## Results

Mean ± sample SD across three seeds. SD is not a confidence interval.

| Metric | Static | Temporal |
|---|---:|---:|
| AUROC | 0.6750 ± 0.0058 | 0.7319 ± 0.0064 |
| Average precision (AUPRC) | 0.0455 ± 0.0018 | 0.0581 ± 0.0015 |
| Brier score (lower is better) | 0.1659 ± 0.0057 | 0.0972 ± 0.0021 |
| Log loss (lower is better) | 0.5223 ± 0.0120 | 0.3526 ± 0.0054 |
| Mean predicted probability | 36.8% | 26.3% |
| Observed positive hourly-label prevalence | 1.415% | 1.415% |
| Descriptive calibration slope | 0.575 | 0.681 |

A constant probability equal to the held-out set B prevalence has Brier score 0.01395 and log loss 0.07429. This is a **descriptive reference only**, because test prevalence is not known in advance in real deployment. Both trained models' raw probabilities score substantially worse on these proper scoring rules.

## Interpretation

1. **Temporal features rank hourly positive labels better** than static features on set B in these runs.
2. **Neither model produces trustworthy raw risk probabilities.** With balanced class weights, mean predicted probabilities are far above the observed 1.415% hourly-label prevalence. The temporal model is less overpredicted than the static model, but its probability outputs are still not deployment-ready.
3. The Brier/log-loss comparison is consistent with severe probability miscalibration and/or distribution shift. This experiment does not determine how much is due to class weighting versus cohort shift.
4. The calibration intercept and slope were estimated on held-out set B only as diagnostics. They were not used to modify predictions, and no threshold was tuned on B.
5. A next defensible experiment is to fit any recalibration method on a patient-disjoint validation partition from set A, freeze it, and evaluate once on set B. That should be pre-specified and repeated with uncertainty intervals before making any clinical claim.

## Provenance and limitations

- Local runs used a reconstructed working copy of the evaluation logic; byte-for-byte identity with the checked-in source has not been verified.
- Set A and set B are both from the PhysioNet/CinC Challenge 2019 benchmark. This is not prospective clinical validation.
- The target is the dataset's hourly SepsisLabel; hourly-row performance is not patient-level event sensitivity, lead time, or a real-world clinical false-alarm rate.
- The threshold 0.5 is not clinically selected.
- No raw patient records, identifiers, or row-level predictions were written to the report or committed.

Aggregate-only artifact: [cross-cohort calibration JSON](../results/cross_cohort_calibration_diagnostics_2026-10-14.json). Reusable runner: [scripts/evaluate_cross_cohort_calibration.py](../scripts/evaluate_cross_cohort_calibration.py).
