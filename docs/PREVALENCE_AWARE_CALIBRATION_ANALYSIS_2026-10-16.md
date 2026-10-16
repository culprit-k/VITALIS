# Prevalence-aware model and calibration analysis — 16 October 2026

## Provenance

- Source: aggregate-only artifact from clean-checkout full-cohort workflow [38889950689](https://github.com/culprit-k/VITALIS/actions/runs/38889950689), on source commit `426ac5dd2a8076fb192bcebd0b1c8f838bf72906`.
- Input artifact: `vitalis_set_a_platt_calibration.json` retained inside [artifact 12042469450](https://github.com/culprit-k/VITALIS/actions/runs/38889950689/artifacts/12042469450).
- Protocol: three seeds (42, 123, 2026), 1/3/6-hour horizons, patient-disjoint Set A 60% model-fit / 20% calibration / 20% untouched development holdout, and Set B final evaluation only.
- Four configurations: temporal baseline and temporal + patient-relative physiology, each with class-balanced and unweighted logistic regression. Platt calibration was fit on Set A calibration patients only.
- No raw data, feature caches, patient identifiers, or row-level predictions are published here.

## Evaluation prevalence and constant-probability reference

The constant-prevalence Brier reference is (p(1-p)), where (p) is the observed positive-window prevalence among eligible Set B rows. It is a descriptive reference, not a fitted model or a clinical operating policy.

| Horizon | Eligible Set B rows | Positive future-window rows | Prevalence | Constant-prevalence Brier |
|---:|---:|---:|---:|---:|
| 1 h | 732,357 | 919 | 0.001255 | 0.001253 |
| 3 h | 694,628 | 2,665 | 0.003837 | 0.003822 |
| 6 h | 638,026 | 5,144 | 0.008062 | 0.007997 |

## Set B results by model and horizon

Metrics below are mean ± sample standard deviation across the three seeds. AUROC and AUPRC do not change under the monotonic Platt transform, so they are reported once per model/horizon. Sensitivity and PPV are reported at the fixed diagnostic threshold 0.5; that threshold was not selected on Set B and is not clinically justified.

| Horizon | Configuration | AUROC | AUPRC | Raw Brier | Platt Brier | Raw sensitivity @ 0.5 | Platt sensitivity @ 0.5 | Platt PPV @ 0.5 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 h | Temporal, balanced | 0.659459 ± 0.006159 | 0.003469 ± 0.000032 | 0.112765 ± 0.007551 | 0.001270 ± 0.000002 | 0.363076 | 0.000000 | 0.000000 |
| 1 h | Temporal, unweighted | 0.661736 ± 0.004215 | 0.003394 ± 0.000133 | 0.001266 ± 0.000002 | 0.001264 ± 0.000002 | 0.000000 | 0.000000 | 0.000000 |
| 1 h | Temporal + personal physiology, balanced | 0.668269 ± 0.007420 | 0.003714 ± 0.000101 | 0.119062 ± 0.010014 | 0.001268 ± 0.000005 | 0.396808 | 0.000000 | 0.000000 |
| 1 h | Temporal + personal physiology, unweighted | 0.666985 ± 0.006025 | 0.003374 ± 0.000151 | 0.001268 ± 0.000002 | 0.001266 ± 0.000004 | 0.000000 | 0.000000 | 0.000000 |
| 3 h | Temporal, balanced | 0.681265 ± 0.003083 | 0.012775 ± 0.000246 | 0.115349 ± 0.003271 | 0.003852 ± 0.000026 | 0.371857 | 0.000125 | 0.015152 |
| 3 h | Temporal, unweighted | 0.667388 ± 0.006297 | 0.011662 ± 0.000372 | 0.003836 ± 0.000002 | 0.003829 ± 0.000005 | 0.000000 | 0.000000 | 0.000000 |
| 3 h | Temporal + personal physiology, balanced | 0.691350 ± 0.003587 | 0.013528 ± 0.000224 | 0.119650 ± 0.003450 | 0.003868 ± 0.000045 | 0.399250 | 0.000000 | 0.000000 |
| 3 h | Temporal + personal physiology, unweighted | 0.676214 ± 0.004870 | 0.012035 ± 0.000226 | 0.003841 ± 0.000002 | 0.003832 ± 0.000007 | 0.000000 | 0.000000 | 0.000000 |
| 6 h | Temporal, balanced | 0.683405 ± 0.001590 | 0.026411 ± 0.000351 | 0.133599 ± 0.008519 | 0.008124 ± 0.000115 | 0.418740 | 0.000713 | 0.031657 |
| 6 h | Temporal, unweighted | 0.664619 ± 0.002991 | 0.024091 ± 0.000326 | 0.008043 ± 0.000014 | 0.008020 ± 0.000027 | 0.000259 | 0.000065 | 0.016667 |
| 6 h | Temporal + personal physiology, balanced | 0.693398 ± 0.002942 | 0.027704 ± 0.000315 | 0.136159 ± 0.008550 | 0.008176 ± 0.000161 | 0.437468 | 0.001490 | 0.033398 |
| 6 h | Temporal + personal physiology, unweighted | 0.678726 ± 0.003905 | 0.025013 ± 0.000340 | 0.008048 ± 0.000011 | 0.008021 ± 0.000031 | 0.000259 | 0.000065 | 0.018519 |

## Interpretation

1. **Class weighting changes score scale and threshold behavior.** Balanced models have materially higher sensitivity at 0.5 before calibration but severely overpredict probabilities under the observed low prevalence, with much worse Brier scores than the constant-prevalence reference. Platt scaling compresses their scores and reduces Brier, but their 0.5 sensitivity then becomes essentially zero.
2. **Unweighted logistic regression gives a more plausible raw probability scale but does not solve alerting.** Its Brier score is near the constant-prevalence reference, but it is still slightly worse than that reference at all three horizons. Sensitivity at 0.5 is zero or nearly zero, so these probabilities do not provide a usable alert policy at that threshold.
3. **The personal-physiology features are not an across-metric winner.** They improve AUROC over the temporal baseline in both weighting configurations at each horizon, but unweighted AUPRC is lower than the temporal unweighted baseline, and Brier does not improve over the prevalence reference. Under balanced weighting, physiology features slightly improve AUPRC but further worsen raw Brier.
4. **Calibration is not established by Brier reduction alone.** In this rare-outcome setting, a probability predictor near zero can have a low Brier score while missing nearly every positive window at a fixed threshold. Calibration quality, discrimination, and alert utility must be considered separately.
5. **Set B must not be used to repair these outcomes.** Do not select a threshold, model, feature set, or calibrator from these Set B results. Set B has already been used for exploratory evaluation. Any new operating-point work must use Set A development data and then be evaluated on a genuinely new independent cohort.

## Decision and next experiment

- Do not promote the balanced, unweighted, calibrated, or personal-physiology candidate as clinically superior.
- Keep the historical baseline and all previous artifacts immutable.
- On Set A only, predeclare and compare probability objectives and candidate operating points using patient-disjoint fit/calibration/holdout partitions. Report Brier, log loss, calibration intercept/slope and reliability curves, AUROC/AUPRC, sensitivity, PPV, alerts per at-risk patient-day, positive-window coverage, and patient-cluster uncertainty. Freeze the full model and policy before evaluation on a genuinely new cohort.
- The current Set B benchmark is retrospective and shares the same Challenge labeling framework; it is not independent prospective clinical validation.

## Scope and safety

The endpoint is future entry into the Challenge `SepsisLabel`-positive window, whose source definition already incorporates a six-hour lead convention. It is not independently adjudicated biological sepsis onset. These results do not establish clinical utility, patient benefit, safe alert thresholds, regulatory clearance, or patentability. VITALIS remains a research prototype and must not be used to guide patient care.
