# Full-cohort horizon cross-cohort results — 14 October 2026

**Status: completed retrospective research run; not clinical validation.**

The run used all eligible rows from the official Challenge 2019 Set B cohort for evaluation, with three separate patient-disjoint Set A training splits (seeds 42, 123, 2026). For each split, the static and temporal logistic-regression models were fit only on the training partition. The remaining 40% of eligible Set A patients were unused; Set B was not used for fitting, feature selection, calibration, or threshold selection.

## Cohort and run integrity

| Cohort | Patients | Hourly rows | Positive source labels |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 |
| Set B | 20,000 | 761,995 | 10,780 |

- 109 features per row; both cache schemas matched.
- All 9 seed × horizon combinations completed in 384.8 seconds of reported run time.
- Each result reports 200 patient-cluster bootstrap replicates for warning metrics.
- Aggregate-only result: [`results/horizon_cross_cohort_2026-10-14.json`](../results/horizon_cross_cohort_2026-10-14.json).
- Source archive SHA-256: `b67472a9cfc549b5d2fc911475b952e52d264287d0be864fad5ef94781a2d8e6`.

## Set B results

Values are mean ± sample standard deviation across the three Set A training seeds. The alert threshold was fixed at 0.5 and the refractory interval at six hours.

| Future-label horizon | Model | AUROC | AUPRC | Brier score* | Alerts / at-risk patient-day | Future-positive-window coverage |
|---|---|---:|---:|---:|---:|---:|
| 1 hour | Static | 0.6634 ± 0.0022 | 0.00379 ± 0.00022 | 0.19370 ± 0.00585 | 1.792 ± 0.143 | 12.0% ± 0.4% |
| 1 hour | Temporal | 0.6569 ± 0.0110 | 0.00317 ± 0.00015 | 0.13196 ± 0.00883 | 1.462 ± 0.113 | 11.7% ± 1.2% |
| 3 hours | Static | 0.6813 ± 0.0043 | 0.01358 ± 0.00017 | 0.18060 ± 0.00546 | 1.507 ± 0.039 | 32.9% ± 0.7% |
| 3 hours | Temporal | 0.6800 ± 0.0145 | 0.01264 ± 0.00048 | 0.13134 ± 0.00347 | 1.276 ± 0.081 | 29.3% ± 1.5% |
| 6 hours | Static | 0.6868 ± 0.0050 | 0.02859 ± 0.00034 | 0.17455 ± 0.00621 | 1.399 ± 0.052 | 60.2% ± 1.7% |
| 6 hours | Temporal | 0.6864 ± 0.0138 | 0.02643 ± 0.00102 | 0.14219 ± 0.00516 | 1.257 ± 0.105 | 56.8% ± 2.0% |

*Brier scores are from class-weighted, uncalibrated logistic regression; they do not establish calibration.

## Interpretation

1. **Temporal features did not improve ranking metrics consistently.** Mean AUROC and AUPRC were slightly higher for the static model at all three horizons. At six hours, AUROC was nearly identical (0.6868 static vs 0.6864 temporal).
2. **Temporal models generated fewer alerts at the fixed threshold, but also covered fewer future-positive windows.** This is a trade-off, not a demonstrated improvement in clinical utility.
3. **The temporal model's lower Brier score needs separate calibration analysis.** Class weighting changes probability interpretation; these values alone are not evidence of reliable risk calibration.
4. **Positive future-label rows are rare.** Set B target prevalence was 0.125% at one hour, 0.384% at three hours, and 0.806% at six hours. AUPRC must be interpreted against these low baselines.
5. Training-seed standard deviations describe sensitivity to the selected Set A training split. Patient-cluster bootstrap intervals are conditional on this fixed Set B cohort and do not replace independent external or prospective validation.

## Label and clinical boundaries

The target is whether the Challenge `SepsisLabel` becomes positive within the next H hourly rows, conditional on a current negative label. The source challenge label already incorporates a six-hour lead convention. These are **not predictions of independently observed sepsis onset within H hours**.

“Alerts outside future-positive windows” are not verified clinical false alarms; warning lead is relative to challenge-label entry. The threshold and refractory period are research settings, not clinically selected operating points. VITALIS remains research-only and must not be used for patient care.

## Reproduction provenance

The full Git clone was unavailable in the execution container because `github.com` DNS resolution failed. The local run used a reconstructed runner based on the checked-in evaluator source (`scripts/evaluate_horizon_cross_cohort.py`, blob SHA `891b84ad4a5da039f1dc38411211c503c971167c`) and cache builder (`scripts/build_feature_cache.py`, blob SHA `eba7dda1532675c2e3f21476b0bba2cead537e78`). The patient-cluster bootstrap was vectorized in commit `3b3dca5f32f96b34c80ab743409c72f75e878596`; its CI run passed all 120 tests. The committed JSON contains aggregate metrics and seed-level summaries only, not raw rows, patient identifiers, or individual predictions.
