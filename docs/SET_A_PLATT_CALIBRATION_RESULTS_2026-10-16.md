# Set A Platt calibration results — 16 October 2026

## Execution and reproducibility

- Clean-checkout full-cohort workflow: [run 38783490400](https://github.com/culprit-k/VITALIS/actions/runs/38783490400), source commit `2377f5fe244e6ae317f68d27f27a0f263cf82813`.
- Workflow conclusion: success. Standard tests and reporting-dashboard tests also passed on this revision.
- The aggregate calibration artifact contains nine horizon × seed runs and completed in 1,312.9 seconds. No row-level predictions, patient identifiers, raw cohort files, or feature caches were included.
- Calibration was fitted only on a patient-disjoint Set A calibration partition; Set B was evaluation-only. The preserved baseline was not modified.

## Results

Values below are the mean across seeds 42, 123 and 2026. Brier is a proper probability scoring rule (lower is better); AUROC is a ranking metric. The 0.5 threshold is a fixed research reference and is not clinically selected.

| Horizon | Model | Raw Brier | Platt Brier | Raw AUROC | Platt AUROC | Mean sensitivity after Platt at 0.5 |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Temporal baseline | 0.112765 | 0.001270 | 0.659459 | 0.659459 | 0.000000 |
| 1 h | Temporal + personal physiology | 0.119062 | 0.001268 | 0.668269 | 0.668269 | 0.000000 |
| 3 h | Temporal baseline | 0.115349 | 0.003852 | 0.681265 | 0.681265 | 0.000125 |
| 3 h | Temporal + personal physiology | 0.119650 | 0.003868 | 0.691350 | 0.691350 | 0.000000 |
| 6 h | Temporal baseline | 0.133599 | 0.008124 | 0.683405 | 0.683405 | 0.000713 |
| 6 h | Temporal + personal physiology | 0.136159 | 0.008176 | 0.693398 | 0.693398 | 0.001490 |

The paired patient-cluster bootstrap 95% intervals for calibrated-minus-raw Brier were below zero in all nine runs. However, **this is not a usable calibration success**: at the fixed 0.5 threshold, mean sensitivity is effectively zero. Platt scaling has compressed predicted probabilities so strongly that nearly no positive rows cross 0.5. The Brier score is dominated by the very low event prevalence, so a near-zero probability predictor can score well while failing to identify positive windows.

AUROC remains effectively unchanged, as expected for a monotonic calibration map. The results show probability rescaling, not improved ranking or a validated alerting operating point. The Set A calibration prevalence and Set B prevalence differ, so transport is also a concern.

## Decision

Do not promote this calibration or candidate model as clinically useful. Do not adjust the threshold on Set B to recover sensitivity. The fixed 0.5 operating point is demonstrably unsuitable after this calibration, but selecting a new threshold using Set B would leak evaluation information.

## Next predeclared experiment

Use Set A only to compare:
1. a prevalence-aware logistic objective without class balancing, and
2. Platt calibration trained on patient-disjoint Set A predictions generated out-of-fold or on a reserved calibration partition.

Use a Set A validation partition to select and freeze any operating point and calibration method. Then evaluate once on Set B, reporting Brier, log loss, calibration curve/intercept/slope, AUROC/AUPRC, sensitivity, PPV and alert burden. Do not use Set B to choose a threshold or calibrator. Keep all prior baselines and artifacts immutable.

## Scope

The endpoint is entry into the PhysioNet/CinC Challenge 2019 SepsisLabel-positive window, not independently adjudicated biological sepsis onset. Set B is another Challenge training cohort, not an independent prospective clinical cohort. This is retrospective research, not clinical validation; VITALIS must not be used to guide patient care.
