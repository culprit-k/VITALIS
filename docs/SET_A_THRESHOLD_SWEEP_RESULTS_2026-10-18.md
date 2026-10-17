# Set A-only operating-threshold sweep — 18 October 2026

## Provenance and scope

- Source commit: `14440230ff19bd1ade378374c47158cda321f628`.
- Workflow: [full-cohort reproduction run 39057821508](https://github.com/culprit-k/VITALIS/actions/runs/39057821508).
- Aggregate artifact: `vitalis-clean-checkout-reproduction-14440230ff19bd1ade378374c47158cda321f628`, artifact ID `12111943281`.
- Artifact SHA-256: `565f0ccecb900c6d41566de8e0dfbc61e79793874079c9bd124b8c4a8f05980e`.
- Experiment: nine horizon × seed runs; horizons 1/3/6 hours; seeds 42, 123, 2026.
- Set A partitioning is patient-disjoint: 60% base-model fit, 20% probability calibration, 20% threshold selection. Threshold-selection patients are not used to fit the model or calibrator.
- The sweep evaluates 102 predeclared thresholds per configuration. It did not load or evaluate Set B; no Set B outcomes were used for model, calibration, or threshold selection.
- Tables below report the arithmetic mean of the three seed-level metrics, not a pooled-patient estimate. Alert-burden and future-positive-window coverage estimates are specific to the Set A threshold-selection partition.

## Threshold-independent results

| Horizon | Configuration | AUROC | AUPRC | Brier |
|---:|---|---:|---:|---:|
| 1 h | Temporal baseline, balanced | 0.743864 | 0.008555 | 0.002259 |
| 1 h | Temporal baseline, unweighted | 0.748431 | 0.008851 | 0.002258 |
| 1 h | Temporal + personal physiology, balanced | 0.750704 | 0.008764 | 0.002261 |
| 1 h | Temporal + personal physiology, unweighted | 0.751744 | 0.008918 | 0.002259 |
| 3 h | Temporal baseline, balanced | 0.763421 | 0.026968 | 0.006878 |
| 3 h | Temporal baseline, unweighted | 0.759220 | 0.025921 | 0.006844 |
| 3 h | Temporal + personal physiology, balanced | 0.769415 | 0.027450 | 0.006902 |
| 3 h | Temporal + personal physiology, unweighted | 0.760510 | 0.025643 | 0.006849 |
| 6 h | Temporal baseline, balanced | 0.765933 | 0.056129 | 0.014129 |
| 6 h | Temporal baseline, unweighted | 0.759161 | 0.053365 | 0.014041 |
| 6 h | Temporal + personal physiology, balanced | 0.769902 | 0.056484 | 0.014164 |
| 6 h | Temporal + personal physiology, unweighted | 0.760448 | 0.052665 | 0.014045 |

These results are descriptive development-partition estimates. Small differences between configurations should not be treated as established improvements without uncertainty-aware paired comparison and independent review. Brier score is prevalence-sensitive and must not be interpreted alone as evidence of useful risk prediction.

## Operating-point trade-offs on Set A

The following are seed-averaged sensitivity, positive predictive value (PPV), alert episodes per at-risk patient-day, and coverage of future Challenge-positive windows at two predeclared reference thresholds. They are not clinically selected thresholds.

| Horizon | Configuration | Threshold | Sensitivity | PPV | Alerts / at-risk patient-day | Future-window coverage |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Temporal baseline, balanced | 0.01 | 0.1221 | 0.01572 | 0.1399 | 0.0340 |
| 1 h | Temporal baseline, balanced | 0.05 | 0.0048 | 0.01085 | 0.0074 | 0.0020 |
| 1 h | Temporal baseline, unweighted | 0.01 | 0.1291 | 0.01470 | 0.1614 | 0.0278 |
| 1 h | Temporal baseline, unweighted | 0.05 | 0.0057 | 0.01267 | 0.0086 | 0.0011 |
| 1 h | Temporal + personal physiology, balanced | 0.01 | 0.1201 | 0.01550 | 0.1280 | 0.0372 |
| 1 h | Temporal + personal physiology, balanced | 0.05 | 0.0067 | 0.01199 | 0.0083 | 0.0028 |
| 1 h | Temporal + personal physiology, unweighted | 0.01 | 0.1426 | 0.01512 | 0.1758 | 0.0330 |
| 1 h | Temporal + personal physiology, unweighted | 0.05 | 0.0057 | 0.01154 | 0.0100 | 0.0011 |
| 3 h | Temporal baseline, balanced | 0.01 | 0.4573 | 0.02489 | 0.8029 | 0.2821 |
| 3 h | Temporal baseline, balanced | 0.05 | 0.0726 | 0.05133 | 0.0573 | 0.0562 |
| 3 h | Temporal baseline, unweighted | 0.01 | 0.4808 | 0.02270 | 0.9355 | 0.3213 |
| 3 h | Temporal baseline, unweighted | 0.05 | 0.0645 | 0.05231 | 0.0544 | 0.0478 |
| 3 h | Temporal + personal physiology, balanced | 0.01 | 0.4435 | 0.02665 | 0.7455 | 0.2628 |
| 3 h | Temporal + personal physiology, balanced | 0.05 | 0.0733 | 0.05017 | 0.0580 | 0.0507 |
| 3 h | Temporal + personal physiology, unweighted | 0.01 | 0.4798 | 0.02263 | 0.9940 | 0.3295 |
| 3 h | Temporal + personal physiology, unweighted | 0.05 | 0.0632 | 0.04876 | 0.0632 | 0.0516 |
| 6 h | Temporal baseline, balanced | 0.01 | 0.8128 | 0.02651 | 2.4760 | 0.8952 |
| 6 h | Temporal baseline, balanced | 0.05 | 0.1960 | 0.09382 | 0.1605 | 0.2192 |
| 6 h | Temporal baseline, unweighted | 0.01 | 0.7904 | 0.02679 | 2.3610 | 0.8792 |
| 6 h | Temporal baseline, unweighted | 0.05 | 0.1948 | 0.08972 | 0.1810 | 0.2309 |
| 6 h | Temporal + personal physiology, balanced | 0.01 | 0.8217 | 0.02649 | 2.5020 | 0.9046 |
| 6 h | Temporal + personal physiology, balanced | 0.05 | 0.1896 | 0.09248 | 0.1589 | 0.2181 |
| 6 h | Temporal + personal physiology, unweighted | 0.01 | 0.7923 | 0.02698 | 2.4249 | 0.8860 |
| 6 h | Temporal + personal physiology, unweighted | 0.05 | 0.1979 | 0.08626 | 0.2059 | 0.2447 |

## Interpretation and decision

1. The threshold trade-off is substantial: a lower threshold can increase sensitivity and future-window coverage while increasing alert burden; a higher threshold reduces alert burden but can miss most future-positive windows.
2. The 6-hour horizon has higher future-window coverage in this development partition, but it also has a materially different prediction horizon and alert burden. It is not automatically the preferred configuration.
3. The personal-physiology feature configuration shows mixed, modest changes across horizons and class-weighting choices. This sweep alone does not establish that the feature improves generalization or clinical utility.
4. PPV remains low in absolute terms, in part because the target is rare. Outside-window alerts are not verified clinical false alarms.
5. **No operating threshold is selected here.** No clinically defensible alert budget or utility objective has been signed off by an independent clinical/research supervisor. The protocol requires that objective before nominating a threshold.

## Next gate

- Obtain independent methods review of the partitioning, metrics, bootstrap uncertainty, target semantics, and the interpretation above.
- Agree and document a development-only utility objective and acceptable alert burden with a qualified supervisor before selecting any operating point.
- Freeze the selected configuration and threshold using Set A only; only then run the separately frozen Set B evaluation once.
- Treat Set B as a second Challenge training cohort, not an external clinical validation cohort. A genuinely external cohort and appropriate institutional, ethics, privacy, safety, and regulatory governance remain required.

This is retrospective research evidence only. The target is entry into the Challenge `SepsisLabel`-positive window, not independently adjudicated sepsis onset. VITALIS is not a validated medical device and must not be used for patient care.
