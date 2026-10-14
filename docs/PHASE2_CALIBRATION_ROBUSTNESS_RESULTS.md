# Phase 2 Calibration and Missingness Robustness — Local Evaluation

**Status:** exploratory evaluation completed locally; not clinical validation.

## Protocol
- Dataset: local PhysioNet/CinC Challenge 2019 training set A; 20,336 patient files available.
- Deterministic sample: 500 patients, sampling seed 20261014; 20,010 hourly rows and 439 positive `SepsisLabel` rows (2.19%).
- Patient-disjoint train/validation/test splits: 320 / 80 / 100 patients, repeated with split seeds 42, 123, and 2026.
- Models: static, temporal, and experimental personalized logistic baselines.
- Median imputation, missingness indicators, scaling, and logistic regression. Logistic recalibration was fitted on validation patients only, then applied to held-out test patients.
- `SepsisLabel` was used as supplied; it was not shifted a second time. Outputs contain aggregate metrics only, not patient-level predictions.

## Held-out test results
Values below are mean ± sample SD across the three split seeds (the SD is not a confidence interval).

| Feature set | Raw Brier | Raw log loss | Raw calibration slope | Test missing fraction |
|---|---:|---:|---:|---:|
| Static | 0.1816 ± 0.0301 | 0.5683 ± 0.0897 | 0.5748 ± 0.1507 | 70.05% |
| Temporal | 0.1518 ± 0.0353 | 0.5342 ± 0.1235 | 0.2264 ± 0.0328 | 68.12% |
| Personalized | 0.1256 ± 0.0192 | 0.6545 ± 0.2377 | 0.0722 ± 0.0167 | 69.21% |

The raw personalized model had the lowest mean Brier score but the worst mean log loss and a very shallow calibration slope. This is mixed evidence, not a reason to select it as the best model.

## Validation-fitted recalibration — caution
Mean held-out Brier/log-loss after validation-only logistic recalibration:
- Static: 0.0219 / 0.1028
- Temporal: 0.0219 / 0.1052
- Personalized: 0.0221 / 0.1103

These numbers should **not** be interpreted as proof of successful or transportable calibration. The test-set calibration intercept/slope varied substantially across splits, and the apparent Brier improvement is compatible with predictions being compressed toward the low event prevalence. The validation cohort is small (80 patients per split), so recalibration stability is a major concern. Do not deploy these probabilities or treat them as clinical risk estimates.

## Interpretation and limitations
- This is a 500-patient sample from training set A, not the full cohort, an external cohort, or prospective validation.
- Hourly challenge-label rows are correlated; row-level calibration does not measure event-level clinical utility.
- The challenge label's six-hour lead convention was retained as supplied; positive label windows are not independent observations of clinical onset.
- Missingness is substantial (about 68–70% of feature cells in held-out rows). Missingness patterns may vary across patients, sites, and time.
- Only three patient-level splits were run. The results are exploratory and should guide protocol improvements, not clinical claims.
- Raw data and patient-level predictions were not committed to GitHub.

## Reproducibility
- Local output: `VITALIS_PHASE2_CALIBRATION_ROBUSTNESS.json`
- Local output SHA-256: `b18ca134e0a30a54cd5ed8e901c613570e5821843c9edfa4fb204fb6cee7d066`
- Local runner: `run_vitalis_phase2_local.py` (equivalent local implementation using the same sample/split/model protocol; the repository runner remains the canonical shared runner).
