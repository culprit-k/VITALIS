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

## Follow-up: subgroup and missingness sensitivity audit

A separate local, aggregate-only audit was run with the same deterministic 500-patient sample and three patient-disjoint split seeds. The static model was fitted only on each training split. Age strata were defined as under 65 vs 65 and older; source-dataset Gender codes were evaluated as encoded, without interpreting them beyond the source coding. Metrics were suppressed when a subgroup had fewer than 20 patients or fewer than 20 positive label rows.

- Held-out age/gender subgroup AUROC varied across split seeds. For example, age 65+ AUROC ranged from approximately 0.69 to 0.76. Some strata had too few positive label rows for metrics to be reported.
- Splitting test rows by row-level missingness at the median did not reveal a simple monotonic relationship between missingness and performance. AUROC varied by split and missingness stratum; the small sample and repeated hourly rows prevent strong conclusions.
- These are exploratory subgroup diagnostics, not evidence of fairness, subgroup safety, or transportability. The dataset sample and positive-row counts are too limited to make such claims.

Aggregate output SHA-256: `60975095429af8d9083faf8dd3469dce573d90a8c2a9f1a06706d509e77b388e`. The JSON is local-only; it contains aggregate counts and metrics, not patient-level predictions. The canonical repository runner has not yet been executed byte-for-byte in the local environment, so that exact reconciliation remains open.

## Repeatability check (2026-10-14)

Both local evaluation scripts were rerun against the local training-set-A files. Their aggregate outputs reproduced the same byte-level hashes:
- Calibration/missingness output: `b18ca134e0a30a54cd5ed8e901c613570e5821843c9edfa4fb204fb6cee7d066`
- Subgroup/missingness output: `60975095429af8d9083faf8dd3469dce573d90a8c2a9f1a06706d509e77b388e`

The two latest documentation commits' GitHub Actions runs completed successfully:
- [Subgroup results report](https://github.com/culprit-k/VITALIS/actions/runs/38550242081)
- [Roadmap update](https://github.com/culprit-k/VITALIS/actions/runs/38550254446)

**Remaining reproducibility limitation:** this environment cannot resolve `raw.githubusercontent.com` or `github.com` from the local container, so I could not execute the exact checked-in repository runner in-place. The local scripts reproduce the stated sample/split/model protocol and output hashes, but that is not a byte-for-byte reconciliation against the canonical repository runner. Keep that gate open until the canonical code and local dataset are available in the same runtime.

## Additional robustness grid: imputation and calibration methods

A further local experiment compared median imputation **with vs without missingness indicators**, and raw vs validation-only Platt/logistic vs validation-only isotonic recalibration. The static model and patient-disjoint split seeds were held fixed (500 patients; seeds 42, 123, 2026). The held-out test set was never used to fit calibration.

Mean test metrics across the six split/method combinations for each imputation setting (three split seeds per setting):

| Imputation | Calibration | Brier | Log loss | AUROC | Average precision |
|---|---|---:|---:|---:|---:|
| Median + missingness indicators | Raw | 0.1816 | 0.5683 | 0.7244 | 0.1018 |
| Median + missingness indicators | Platt, validation-only | 0.0219 | 0.1028 | 0.7244 | 0.1018 |
| Median + missingness indicators | Isotonic, validation-only | 0.0225 | 0.1056 | 0.7045 | 0.0778 |
| Median only, no indicators | Raw | 0.1855 | 0.5797 | 0.7055 | 0.1216 |
| Median only, no indicators | Platt, validation-only | 0.0245 | 0.1108 | 0.7055 | 0.1216 |
| Median only, no indicators | Isotonic, validation-only | 0.0280 | 0.1212 | 0.7175 | 0.1041 |

**Critical interpretation:** the striking reduction in Brier score and log loss after Platt recalibration should not be read as a performance breakthrough. Test label prevalence is low, and validation-fitted logistic calibration compresses probabilities toward that low prevalence; AUROC is unchanged by Platt scaling and discrimination did not improve. The Brier/log-loss values approach what a low-risk constant predictor can achieve in a low-prevalence row-level task. Calibration quality still needs careful reliability analysis on larger independent data and clinically meaningful event-level endpoints. Isotonic recalibration was inconsistent across splits and can overfit small validation sets.

Missingness indicators showed a modestly better mean AUROC in this sample, but average precision did not improve consistently. This is not sufficient to select a final imputation strategy. The results support retaining missingness indicators as the provisional baseline while testing them prospectively on a larger, independent sample.

- Local aggregate grid output: `VITALIS_PHASE2_ROBUSTNESS_GRID.json`
- Output SHA-256: `a24e02badb34dc0fde751f377e2f4b447d3b6a6a24fb2757c4739673587cfbd0`
- Local runner: `run_vitalis_phase2_robustness_grid.py`

The canonical repository calibration runner has still not been executed in the same local runtime as the dataset; the network restriction prevents downloading GitHub source from the local container. This is a reproducibility-environment limitation, not evidence that the analysis failed. Keep exact canonical-runner reconciliation as an explicit open item.
