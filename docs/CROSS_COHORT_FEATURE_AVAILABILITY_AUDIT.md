# VITALIS cross-cohort feature-availability audit

Date: 14 October 2026

## Scope and method

Compared finite-value counts per feature in the existing local memory-mapped caches for Set A and Set B. No model was fitted, no threshold was selected, and no row-level data or predictions were exported. Rates use hourly rows as denominators; rows are correlated within patients, so these are descriptive availability rates, not independent-sample inference.

| Cohort | Patients | Hourly rows | Feature columns |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 109 |
| Set B | 20,000 | 761,995 | 109 |

## Key counts

- Features all-missing in Set A but observed at least once in Set B: **4**.
- Features all-missing in Set B but observed at least once in Set A: **0**.
- Features whose finite-value rate differs by at least 5 percentage points: **45**.

### All-missing in A, observed in B

| Feature | A finite rows | B finite rows | B finite rate |
|---|---:|---:|---:|
| `EtCO2` | 0 | 57,636 | 7.564% |
| `EtCO2_lag1` | 0 | 56,837 | 7.459% |
| `EtCO2_delta1` | 0 | 51,766 | 6.793% |
| `EtCO2_rollmean6` | 0 | 73,733 | 9.676% |

### Largest availability-rate shifts (absolute difference ≥ 5 percentage points)

| Feature | A finite rate | B finite rate | B − A (pp) |
|---|---:|---:|---:|
| `DBP_rollmean6` | 56.510% | 96.553% | +40.04 |
| `HCO3_rollmean6` | 38.074% | 0.499% | -37.58 |
| `DBP` | 51.874% | 86.055% | +34.18 |
| `DBP_lag1` | 50.941% | 83.908% | +32.97 |
| `BaseExcess_rollmean6` | 33.394% | 0.640% | -32.75 |
| `FiO2_rollmean6` | 41.198% | 9.714% | -31.48 |
| `DBP_delta1` | 48.874% | 77.133% | +28.26 |
| `pH_rollmean6` | 37.063% | 9.315% | -27.75 |
| `PaCO2_rollmean6` | 32.464% | 9.337% | -23.13 |
| `Unit1` | 51.132% | 70.368% | +19.24 |
| `Unit2` | 51.132% | 70.368% | +19.24 |
| `Glucose_rollmean6` | 49.588% | 68.417% | +18.83 |
| `Hct_rollmean6` | 49.701% | 31.462% | -18.24 |
| `Resp_delta1` | 83.506% | 67.912% | -15.59 |
| `FiO2` | 14.193% | 2.259% | -11.93 |
| `FiO2_lag1` | 14.010% | 2.234% | -11.78 |
| `Resp` | 90.223% | 78.861% | -11.36 |
| `Resp_lag1` | 88.108% | 76.873% | -11.24 |
| `BaseExcess` | 10.425% | 0.231% | -10.19 |
| `BaseExcess_lag1` | 10.309% | 0.228% | -10.08 |
| `Glucose` | 12.232% | 22.160% | +9.93 |
| `EtCO2_rollmean6` | 0.000% | 9.676% | +9.68 |
| `Glucose_lag1` | 12.059% | 21.697% | +9.64 |
| `Potassium_rollmean6` | 47.152% | 37.641% | -9.51 |
| `pH` | 11.467% | 2.225% | -9.24 |
| `pH_lag1` | 11.326% | 2.203% | -9.12 |
| `SaO2_rollmean6` | 16.749% | 7.900% | -8.85 |
| `HCO3` | 8.051% | 0.185% | -7.87 |
| `HCO3_lag1` | 7.927% | 0.182% | -7.75 |
| `Chloride` | 8.324% | 0.615% | -7.71 |
| `BUN_rollmean6` | 38.641% | 30.940% | -7.70 |
| `Hgb_rollmean6` | 39.521% | 31.863% | -7.66 |
| `EtCO2` | 0.000% | 7.564% | +7.56 |
| `EtCO2_lag1` | 0.000% | 7.459% | +7.46 |
| `EtCO2_delta1` | 0.000% | 6.793% | +6.79 |
| `PaCO2` | 8.768% | 2.233% | -6.54 |
| `PaCO2_lag1` | 8.669% | 2.210% | -6.46 |
| `HR_delta1` | 86.028% | 79.862% | -6.17 |
| `Hct` | 11.776% | 5.824% | -5.95 |
| `WBC_rollmean6` | 35.342% | 29.474% | -5.87 |
| `Hct_lag1` | 11.602% | 5.740% | -5.86 |
| `Creatinine_rollmean6` | 36.753% | 30.962% | -5.79 |
| `MAP_delta1` | 82.246% | 76.637% | -5.61 |
| `Platelets_rollmean6` | 35.333% | 29.774% | -5.56 |
| `Lactate_rollmean6` | 12.799% | 7.585% | -5.21 |

## Interpretation and pre-specified policy recommendation

1. **Fit-time availability governs learnability.** If a feature is entirely missing in Set A, a model trained only on Set A cannot learn a coefficient for it. Set-B-only observations must not be used to estimate that coefficient.
2. **Use a Set-A-only eligibility rule for any new model.** Before looking at Set-B results, define eligible features as features with nonzero finite observations in the model-training partition (or, more conservatively, a pre-specified minimum coverage threshold) and apply that frozen feature list to both validation and test cohorts.
3. **Do not infer that a feature is safe or comparable just because it is available.** For eligible features, report missingness/coverage by cohort and inspect units, measurement practices, and missingness mechanisms before interpretation.
4. **Treat Set B as evaluation-only.** Its availability rates are reported to characterize transport shift, not to select features, tune thresholds, or choose a model. If a future protocol uses a common-feature intersection, define the intersection using training data alone or external protocol knowledge, then freeze it before evaluation.
5. **No model-performance claim is made by this audit.** This is a descriptive data-quality result, not a new validation experiment or clinical evidence.

## Data handling

The report and JSON contain only feature-level aggregate counts/rates. Raw patient records, patient IDs, group vectors, caches, and row-level predictions remain outside Git.
