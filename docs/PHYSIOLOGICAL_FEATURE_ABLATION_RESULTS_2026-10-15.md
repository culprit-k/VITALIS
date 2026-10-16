# VITALIS patient-relative physiology feature ablation — 15 October 2026

## Reproducibility status

- Full-cohort workflow: [run 38748749241](https://github.com/culprit-k/VITALIS/actions/runs/38748749241), Python 3.11.17, clean checkout at source commit `d0c149a0941ba26139ec6793436896f504be8bd6`.
- The preserved baseline reconciliation passed the predeclared six-decimal rule: **42/42 mean/sample-SD pairs and 84/84 scalar values matched**. The baseline was not edited.
- The same run completed all nine horizon × seed ablation runs and the required aggregate-only probability-quality checks.
- Standard tests and reporting-dashboard tests on this source revision passed. PR #2 remains draft and unmerged.

## Aggregate Set B results

The table reports means across seeds 42, 123, and 2026. Set B is evaluation-only. The candidate adds prior-only patient-relative deviation features for HR, O2Sat, Temp, SBP, MAP, DBP, and Resp; it is not the complete streaming adaptive digital twin.

| Horizon | Model | AUROC | AUPRC | Brier score |
|---:|---|---:|---:|---:|
| 1 h | Temporal baseline | 0.656890 | 0.003170 | 0.131964 |
| 1 h | Temporal + personal physiology | 0.666296 | 0.003478 | 0.138101 |
| 3 h | Temporal baseline | 0.680004 | 0.012639 | 0.131344 |
| 3 h | Temporal + personal physiology | 0.689820 | 0.013419 | 0.135656 |
| 6 h | Temporal baseline | 0.686375 | 0.026433 | 0.142186 |
| 6 h | Temporal + personal physiology | 0.695591 | 0.027696 | 0.145115 |

## Paired probability-quality comparison

Paired patient-cluster bootstrap intervals (200 replicates per seed) estimate candidate-minus-temporal-baseline Brier score. **Positive values mean the candidate has worse Brier score.** Each row below gives the point-estimate range across the three seeds and the full envelope of their 95% percentile intervals; these ranges are descriptive, not a pooled confidence interval.

| Horizon | Per-seed Brier differences | Envelope of per-seed 95% intervals |
|---:|---|---|
| 1 h | +0.005086, +0.007817, +0.005508 | +0.004681 to +0.008209 |
| 3 h | +0.003195, +0.006993, +0.002747 | +0.002421 to +0.007330 |
| 6 h | +0.003153, +0.004114, +0.001520 | +0.001247 to +0.004449 |

## Calibration diagnostics

The calibration slope averaged across seeds for the temporal baseline versus candidate was:

| Horizon | Temporal baseline slope | Candidate slope |
|---:|---:|---:|
| 1 h | 0.301736 | 0.317730 |
| 3 h | 0.490778 | 0.457662 |
| 6 h | 0.496824 | 0.468079 |

Slopes well below 1 indicate predictions are too extreme relative to observed outcomes in this evaluation cohort. The candidate does not consistently improve calibration: it is slightly less over-steep at 1 h, but worse by slope at 3 h and 6 h. Calibration intercepts are also strongly negative because the balanced-class training procedure yields probabilities that are not aligned to the much lower Set B event prevalence. These are descriptive Set B diagnostics only; no calibration transformation was fitted or applied on Set B.

## Decision

**Do not promote the physiology-feature candidate as the current best model.** It improves ranking metrics (AUROC and AUPRC) at all three horizons, but worsens Brier score at all three horizons; paired patient-cluster intervals are positive for every seed/horizon comparison. Probability quality therefore did not improve.

Next experiment, if pursued: predeclare a probability-calibration method and fit it using only patient-disjoint Set A training/validation data, freeze it before evaluation, and evaluate once on Set B. Compare calibration and Brier alongside AUROC/AUPRC and patient-alert burden. Do not select a calibrator or alter thresholds based on Set B. Keep the current baseline and candidate results as separate, immutable artifacts.

## Scope

This is a retrospective cross-cohort analysis of the Challenge 2019 label convention, not independently adjudicated sepsis onset and not prospective clinical validation. Set B is another Challenge training cohort, not an independent external clinical cohort. Outside-window alerts are not verified clinical false alarms. VITALIS remains research-only and must not be used to guide patient care.
