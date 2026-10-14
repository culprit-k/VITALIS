# Cross-cohort evaluation: train on training_setA, test on training_setB

Date: 14 October 2026

## What was done

The local PhysioNet/CinC Challenge 2019 data were verified and used from both official training cohorts:

- **training_setA:** 20,336 patients, 790,215 hourly rows, 17,136 positive hourly challenge-label rows.
- **training_setB:** 20,000 patients, 761,995 hourly rows, 10,780 positive hourly challenge-label rows.

To avoid testing on patients seen during training, models were trained on a patient-level 60% subset of set A; the other 40% of set A was held out and not used for tuning. The complete set B cohort was the test set. Three training-subset seeds (42, 123, 2026) were evaluated. We compared static baseline features with temporal lag, delta, and trailing-six-row features using median imputation, missingness indicators, standard scaling, and balanced logistic regression. Test predictions were processed in memory and were not exported.

## Mean held-out set B results

Mean ± sample SD across the three training-subset seeds. These SDs describe variation across training subsets, not confidence intervals.

| Metric | Static | Temporal |
|---|---:|---:|
| AUROC | 0.6781 ± 0.0015 | 0.7357 ± 0.0028 |
| Average precision (AUPRC) | 0.0464 ± 0.0002 | 0.0597 ± 0.0010 |
| Brier score | 0.1649 ± 0.0018 | 0.0969 ± 0.0024 |
| Sensitivity at fixed 0.5 threshold | 0.4778 ± 0.0055 | 0.3848 ± 0.0080 |
| Specificity at fixed 0.5 threshold | 0.7996 ± 0.0055 | 0.9250 ± 0.0028 |
| PPV at fixed 0.5 threshold | 0.0331 ± 0.0005 | 0.0686 ± 0.0018 |
| NPV at fixed 0.5 threshold | 0.9907 ± 0.00004 | 0.9905 ± 0.0001 |

Set B positive hourly-label prevalence is 10,780 / 761,995 = 1.41%, so average precision should be interpreted against this low baseline prevalence.

## Interpretation

In this first cross-cohort experiment, temporal features ranked positive hourly challenge-label rows better than static features on set B (higher AUROC and AUPRC). At the fixed 0.5 threshold, however, the temporal model had **lower sensitivity** and higher specificity; neither threshold was selected for clinical use. The Brier scores also differ substantially and require calibration and distribution-shift analysis before they can be interpreted as reliable probabilities. These results are a reason to investigate further, not proof of clinical utility.

## Limitations

- Both sets are from the same PhysioNet/CinC Challenge 2019 benchmark. Set B is a held-out cohort for this experiment, not prospective or independent real-world clinical validation.
- Labels are hourly challenge labels with the dataset's existing lead-time convention; they are not independent clinical onset events. No extra label shift was applied.
- The 0.5 threshold is a fixed research comparison, not a clinically selected operating point.
- No calibration, decision-curve analysis, patient-level event sensitivity, lead-time, or clinically meaningful false-alarm rate was evaluated here.
- The local run used a reconstructed working copy of the script logic. The checked-in script and tests are being added, but byte-for-byte identity between local execution and the GitHub source has not been established.
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
