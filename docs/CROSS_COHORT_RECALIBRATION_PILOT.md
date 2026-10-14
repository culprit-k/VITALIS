# Cross-cohort recalibration: validation on set A, evaluation on set B

Date: 14 October 2026

## Question

Can recalibration fitted only on patient-disjoint validation data from training set A improve probability quality when applied to set B?

## Protocol

- Three patient-level split seeds: 42, 123, 2026.
- For each seed, set A was divided into 60% model-training patients, 20% calibration-validation patients, and 20% unused patients. These partitions are patient-disjoint.
- Static and temporal logistic-regression models used median imputation, missingness indicators, standard scaling, and balanced class weights.
- A one-dimensional logistic (Platt) recalibrator was fitted on the set A validation predictions only.
- The fitted recalibrator was frozen and applied once to all set B patients. Set B was not used for model fitting, recalibrator fitting, or threshold selection.
- Set B contains 20,000 patients, 761,995 hourly rows, and 10,780 positive hourly challenge-label rows (1.415%).

## Results

Mean ± sample standard deviation across three split seeds. These are not confidence intervals.

| Model / probability stream | AUROC | Average precision | Brier score | Log loss | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| Static, raw | 0.6750 ± 0.0058 | 0.0455 ± 0.0018 | 0.1659 ± 0.0057 | 0.5223 ± 0.0121 | 36.76% |
| Static, recalibrated | 0.6750 ± 0.0058 | 0.0455 ± 0.0018 | 0.01406 ± 0.00012 | 0.07171 ± 0.00037 | 1.90% |
| Temporal, raw | 0.7319 ± 0.0064 | 0.0581 ± 0.0015 | 0.0972 ± 0.0022 | 0.3526 ± 0.0052 | 26.33% |
| Temporal, recalibrated | 0.7319 ± 0.0064 | 0.0581 ± 0.0015 | 0.01382 ± 0.00003 | 0.06895 ± 0.00036 | 1.34% |

Set A validation positive hourly-label prevalence was about 2.17%; set B prevalence was 1.415%.

## Interpretation

1. Temporal features had better ranking discrimination than static features on set B across all three splits.
2. Validation-only Platt recalibration substantially lowered Brier score and log loss on set B across all three splits while leaving ranking metrics effectively unchanged.
3. This is encouraging for the *recalibration method under this benchmark protocol*, but it is not proof that probabilities are clinically calibrated or will transport to another hospital or future population. The average recalibrated probability remains above set B prevalence, particularly for the static model.
4. Calibration was fit on set A validation labels; the evaluation was on set B, which is held out from recalibration. This separation avoids directly tuning on set B, but does not remove distribution-shift risk.
5. Next: implement this procedure in a checked-in, parameterized runner, test patient isolation and set-B non-use, and execute it from an exact repository checkout. Then assess subgroup and uncertainty robustness without tuning on set B.

## Provenance and limitations

The local runs used a reconstructed experimental harness and a local feature cache; exact byte identity with checked-in source has not been established. The aggregate-only results are in [the three-seed JSON](../results/cross_cohort_validation_A_recalibration_test_B_3seed_2026-10-14.json). No raw patient records, identifiers, or row-level predictions were committed.

Both cohorts are from the PhysioNet/CinC Challenge 2019 benchmark, not prospective clinical validation. Hourly challenge-label metrics are not patient-level event sensitivity, lead time, or real-world clinical false-alarm rates. The threshold 0.5 is not clinically selected.

VITALIS remains research-only and is not validated for diagnosis, triage, treatment, or real patient-care decisions.
