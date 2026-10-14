# Cross-cohort evaluation: train on training_setA, test on training_setB

Date: 14 October 2026

## What was done

The local PhysioNet/CinC Challenge 2019 data were verified and used from both official training cohorts:

- **training_setA:** 20,336 patients, 790,215 hourly rows, 17,136 positive hourly challenge-label rows.
- **training_setB:** 20,000 patients, 761,995 hourly rows, 10,780 positive hourly challenge-label rows.

To avoid testing on patients seen during training, models were trained on a patient-level 60% subset of set A; the other 40% of set A was held out and not used for tuning. The complete set B cohort was the test set. Three training-subset seeds (42, 123, 2026) were evaluated. We compared static baseline features with temporal lag, delta, and trailing-six-row features using median imputation, missingness indicators, standard scaling, and balanced logistic regression. Test predictions were processed in memory and were not exported.

## Exact-source mean held-out set B results

Mean ± sample SD across the three training-subset seeds. These SDs describe variation across training subsets, not confidence intervals.

| Metric | Static | Temporal |
|---|---:|---:|
| AUROC | 0.6750 ± 0.0058 | 0.7319 ± 0.0064 |
| Average precision (AUPRC) | 0.0455 ± 0.0018 | 0.0581 ± 0.0015 |
| Brier score | 0.1659 ± 0.0057 | 0.0972 ± 0.0022 |
| Sensitivity at fixed 0.5 threshold | 0.4765 ± 0.0195 | 0.3829 ± 0.0047 |
| Specificity at fixed 0.5 threshold | 0.7971 ± 0.0134 | 0.9230 ± 0.0022 |
| PPV at fixed 0.5 threshold | 0.0326 ± 0.0012 | 0.0666 ± 0.0017 |
| NPV at fixed 0.5 threshold | 0.9907 ± 0.00023 | 0.9905 ± 0.00007 |

Set B positive hourly-label prevalence is 10,780 / 761,995 = 1.41%, so average precision should be interpreted against this low baseline prevalence.

## Source-execution reconciliation

The aggregate values in the table above come from the exact checked-in evaluator, not the earlier reconstructed-harness run. The local script Git blob SHA matched the GitHub blob exactly: `f700bf0848cd718301d9693c3dae13444a9bfe8b`. Seeds 42, 123, and 2026 were executed separately against the local memory-mapped caches after a combined three-seed invocation exceeded the runtime window. Aggregate-only output and per-seed metrics are recorded in [the exact-source reproduction JSON](../results/cross_cohort_exact_source_reproduction_2026-10-14.json).

**Important correction:** the historical [cross-cohort summary JSON](../results/cross_cohort_train_A_test_B_2026-10-14.json) records different values from the exact-source run (for example, historical mean AUROC 0.6781 static / 0.7357 temporal versus exact-source 0.6750 / 0.7319). That older artifact has been preserved, not overwritten. Until the source of the discrepancy is separately explained, use the exact-source artifact when describing results from the checked-in CLI and do not treat the old reconstructed-harness metrics as reproduced by that script.

The exact-source run emitted expected scikit-learn warnings for Set-A-all-empty EtCO2 columns (and temporal derivatives), which the median imputer skips. Thus those Set-B EtCO2 values do not enter this Set-A-trained model. Set B remains evaluation-only; no feature, calibration, model, or threshold tuning used it.

## Interpretation

In this first cross-cohort experiment, temporal features ranked positive hourly challenge-label rows better than static features on set B (higher AUROC and AUPRC). At the fixed 0.5 threshold, however, the temporal model had **lower sensitivity** and higher specificity; neither threshold was selected for clinical use. The Brier scores also differ substantially and require calibration and distribution-shift analysis before they can be interpreted as reliable probabilities. These results are a reason to investigate further, not proof of clinical utility.

## Limitations

- Both sets are from the same PhysioNet/CinC Challenge 2019 benchmark. Set B is a held-out cohort for this experiment, not prospective or independent real-world clinical validation.
- Labels are hourly challenge labels with the dataset's existing lead-time convention; they are not independent clinical onset events. No extra label shift was applied.
- The 0.5 threshold is a fixed research comparison, not a clinically selected operating point.
- No calibration, decision-curve analysis, patient-level event sensitivity, lead-time, or clinically meaningful false-alarm rate was evaluated here.
- The exact checked-in `scripts/evaluate_cross_cohort.py` bytes were fetched from branch `work/exact-checkout-reproduction`, and the local Git blob SHA matched GitHub (`f700bf0848cd718301d9693c3dae13444a9bfe8b`). The exact script was executed against the local caches one seed at a time. A full Git checkout was not possible in this runtime, so the claim is exact-source-byte execution, not a verified checkout.
- Raw records, identifiers, and patient-level predictions remain outside GitHub.

## Reproduction

Build separate local caches outside the repository with `scripts/build_feature_cache.py`, then run:

```bash
python scripts/evaluate_cross_cohort.py \
  --set-a-cache /path/to/cache-A \
  --set-b-cache /path/to/cache-B \
  --seeds 42 123 2026 \
  --output /path/to/cross-cohort-results.json
```
