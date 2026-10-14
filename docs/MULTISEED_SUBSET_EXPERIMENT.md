# VITALIS multi-seed static-versus-temporal subset experiment

**Status:** exploratory internal experiment; not clinical validation.

## Protocol

- Dataset: PhysioNet/CinC Challenge 2019 `training_setA`; local inventory contains 20,336 patient files.
- Deterministic cohort: 1,500 patient files sampled without replacement from sorted filenames using sampling seed `2026`; same patients reused for all split seeds.
- Split seeds: `42`, `123`, `2026`; patient-level train/validation/test partitions (960/240/300 patients per split).
- Model: class-weighted logistic regression (`max_iter=500`, `lbfgs`), fixed threshold 0.5. Temporal features are within-patient previous-row lag, one-row delta, and trailing six-row mean.
- All-missing training columns were excluded; no convergence/model warnings were observed. EtCO2 and engineered EtCO2 columns were excluded as all-missing in training.
- `SepsisLabel` used as supplied, with no additional shift. Metrics are hourly-row metrics.

## Test results by split seed

| Seed | Static AUROC | Temporal AUROC | Δ AUROC | Static AP | Temporal AP | Δ AP | Static Brier | Temporal Brier | Δ Brier |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 42 | 0.754 | 0.766 | +0.012 | 0.092 | 0.083 | -0.009 | 0.181 | 0.163 | -0.019 |
| 123 | 0.728 | 0.707 | -0.021 | 0.074 | 0.067 | -0.008 | 0.172 | 0.160 | -0.012 |
| 2026 | 0.722 | 0.688 | -0.034 | 0.099 | 0.090 | -0.009 | 0.178 | 0.172 | -0.006 |

Negative Δ Brier means the temporal model has lower Brier score.

## Mean across split seeds

| Metric | Static mean (SD across seeds) | Temporal mean (SD across seeds) |
|---|---:|---:|
| AUROC | 0.735 (0.017) | 0.720 (0.041) |
| Average precision (AP) | 0.088 (0.013) | 0.080 (0.012) |
| Brier score | 0.177 (0.005) | 0.165 (0.006) |

Across-seed SD is not a confidence interval. Paired patient-cluster bootstrap intervals were not completed in this pass.

## Interpretation

Temporal features improved AUROC on seed 42 only; AUROC and AP were lower on seeds 123 and 2026. Mean AUROC and AP were lower for the temporal model. The temporal model had a lower mean Brier score, but this alone does not establish better discrimination or clinical utility.

**Current conclusion:** these results do not support claiming that the present temporal feature set consistently improves prediction. Keep the static baseline as the benchmark; inspect calibration and threshold-specific alert burden before adding personalized-baseline complexity.

## Limitations and next checks

- Only 1,500 patients from one dataset partition; no full-cohort or external validation.
- Hourly rows are correlated within patients and are not independent clinical events.
- AP is low and precision at threshold 0.5 is low; threshold 0.5 is not clinically optimized.
- Validation partitions were created but not used for model selection or threshold tuning.
- No paired bootstrap intervals in this run; small differences should not be treated as established effects.
- This is not evidence of clinical utility, novelty, or patentability.
