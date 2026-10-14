# Cross-cohort recalibration pilot: validation on set A, evaluation on set B

Date: 14 October 2026

## Question

Can a simple recalibration step, fitted only on patient-disjoint validation data from training set A, improve probability quality when applied to training set B?

## Protocol

- One exploratory split seed: 42.
- Set A was divided by patient into 12,201 model-training patients, 4,067 calibration-validation patients, and 4,068 unused patients.
- Static and temporal logistic-regression models used median imputation, missingness indicators, standard scaling, and balanced class weights.
- A one-dimensional logistic (Platt) recalibrator was fitted on set A validation predictions only.
- The fitted recalibrator was frozen and applied once to all 20,000 set B patients (761,995 hourly rows; 10,780 positive hourly labels).
- No set B labels were used to fit the models, recalibrators, or thresholds. No patient-level predictions were exported.

## Results for seed 42

| Model / probability stream | AUROC | Average precision | Brier score | Log loss | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| Static, raw | 0.6742 | 0.0452 | 0.1598 | 0.5100 | 35.84% |
| Static, recalibrated | 0.6742 | 0.0452 | 0.01394 | 0.07159 | 1.85% |
| Temporal, raw | 0.7316 | 0.0585 | 0.0957 | 0.3492 | 25.86% |
| Temporal, recalibrated | 0.7316 | 0.0585 | 0.01383 | 0.06917 | 1.39% |

Observed positive hourly-label prevalence was 2.17% in the set A validation partition and 1.415% in set B.

## Interpretation

1. Temporal features had higher ranking discrimination than static features in this split.
2. Validation-only Platt recalibration substantially improved Brier score and log loss on set B in this pilot, while leaving ranking metrics effectively unchanged.
3. This is not evidence that the probabilities are clinically calibrated. It is one seed, and the prevalence shift from 2.17% in validation to 1.415% in set B means transportability remains a major concern.
4. The next required test is to repeat the same pre-specified procedure for seeds 123 and 2026, report all seed-specific results, and calculate uncertainty without using set B to tune the recalibrator.
5. Both cohorts are from the same PhysioNet/CinC Challenge 2019 benchmark. This is not prospective validation, and hourly-label metrics are not patient-level event sensitivity, lead time, or real-world clinical false-alarm rates.

## Provenance and limitations

This result was generated locally with a reconstructed experimental harness and a local feature cache; exact byte identity with checked-in source has not been established. The output committed to the repository is aggregate-only. No raw patient records, identifiers, or row-level predictions are included.

VITALIS remains research-only and is not validated for diagnosis, triage, treatment, or real patient-care decisions.

Aggregate artifact: [seed 42 results](../results/cross_cohort_validation_A_recalibration_test_B_seed42_2026-10-14.json).
