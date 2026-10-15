# VITALIS fresh full-cohort source-verified reproduction

**Run date:** 2026-10-15  
**Scope:** Fresh retrospective Set A → Set B evaluation of 1-, 3-, and 6-hour future Challenge-label targets.  
**Status:** The core pipeline source blobs and fresh data caches were verified, all nine predeclared runs completed, and the aggregate summary reconciles with the preserved 14 October report at six decimal places. The *full release gate remains open* because the environment was not a clean full-repository checkout, dependencies were not locked, and independent review is outstanding.

## Source and data provenance

- Repository branch: `work/strict-reproducibility-gate`
- Branch head used for source-file retrieval: `bfa78a9cfc6a045feb2edff57c0dc6d2b82e4641`
- Uploaded archive SHA-256: `b67472a9cfc549b5d2fc911475b952e52d264287d0be864fad5ef94781a2d8e6` (matches the archive hash recorded in the preserved 14 October aggregate).
- Exact Git-blob matches were verified for the four pipeline-critical files:

| File | Git blob SHA-1 |
|---|---|
| `scripts/build_feature_cache.py` | `eba7dda1532675c2e3f21476b0bba2cead537e78` |
| `scripts/evaluate_horizon_cross_cohort.py` | `891b84ad4a5da039f1dc38411211c503c971167c` |
| `src/vitalis/horizon.py` | `7d275dfb23ec86be25bdca26b9c30fc639887630` |
| `src/vitalis/validation.py` | `8a2cabc1ef08194b4873934529c1ba72833f4f41` |

The four local files' Git blob hashes exactly matched those recorded by GitHub. This is targeted source-blob verification, **not** a full clean Git checkout or a full-tree source-manifest verification.

## Cohort and cache checks

| Cohort | Patients | Hourly rows | Positive hourly labels | Features | Fresh cache chunks |
|---|---:|---:|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 | 109 | 4 |
| Set B | 20,000 | 761,995 | 10,780 | 109 | 4 |

Fresh caches were rebuilt from scratch using the exact blob-verified cache builder in eight non-overlapping chunks. All chunk markers are present. Patient group sizes match the metadata for every patient; array shapes, binary labels, cohort totals, positive-label totals, and the shared 109-feature schema passed checks.

## Evaluation protocol

- Horizons: 1, 3, and 6 hours; seeds: 42, 123, and 2026.
- Static model (40 baseline features) and temporal model (109 features): 18 model fits total.
- Patient-disjoint Set A split: 60% training / 40% unused holdout; holdout not used for tuning.
- Set B is final evaluation only. No fitting, feature selection, calibration, threshold selection, or model changes use Set B.
- Fixed threshold 0.5, six-hour refractory period, and 200 patient-cluster bootstrap replicates.
- Runtime: Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0; BLAS/OpenMP threads limited to one.
- Evaluation runtime: 355.799 seconds; no model-fit warnings were captured.
- Twelve focused horizon tests passed locally. The prior successful repository CI run passed 183 tests in 4.42 seconds: [GitHub Actions run](https://github.com/culprit-k/VITALIS/actions/runs/38676169821).

## Aggregate results

Mean ± sample standard deviation across the three predeclared seeds. PPV is measured at the fixed research threshold of 0.5.

| Horizon | Model | AUROC | AUPRC | Brier score | Sensitivity | PPV | Alerts / at-risk patient-day | Future-positive-window coverage |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 h | Static | 0.6634 ± 0.0022 | 0.00379 ± 0.00022 | 0.1937 ± 0.0058 | 0.528 | 0.00248 | 1.792 | 12.0% |
| 1 h | Temporal | 0.6569 ± 0.0110 | 0.00317 ± 0.00015 | 0.1320 ± 0.0088 | 0.401 | 0.00319 | 1.462 | 11.7% |
| 3 h | Static | 0.6813 ± 0.0043 | 0.01358 ± 0.00017 | 0.1806 ± 0.0055 | 0.521 | 0.00842 | 1.507 | 32.9% |
| 3 h | Temporal | 0.6800 ± 0.0145 | 0.01264 ± 0.00048 | 0.1313 ± 0.0035 | 0.415 | 0.01077 | 1.276 | 29.3% |
| 6 h | Static | 0.6868 ± 0.0050 | 0.02859 ± 0.00034 | 0.1746 ± 0.0062 | 0.515 | 0.01903 | 1.399 | 60.2% |
| 6 h | Temporal | 0.6864 ± 0.0138 | 0.02643 ± 0.00102 | 0.1422 ± 0.0052 | 0.446 | 0.02237 | 1.257 | 56.8% |

## Reconciliation

Compared seven metrics for each of two models at each of three horizons (42 mean/SD pairs) with the preserved [14 October aggregate report](../results/horizon_cross_cohort_2026-10-14.json).

**All 42 mean/SD pairs match at six decimal places.** The earlier aggregate report was preserved, not overwritten. The full fresh aggregate output was retained locally; its SHA-256 is `13daeb6bb2b83c8df79bbf2cf056756fe21509c221c5fe7399ecca811335fda4`. The compact machine-readable summary is [here](../results/horizon_cross_cohort_source_verified_summary_2026-10-15.json).

## Interpretation and remaining gates

- Static AUROC/AUPRC are slightly higher on average than temporal-model values across these horizons. Temporal Brier scores are lower, but these are uncalibrated class-weighted logistic regressions; the scores do not establish clinical calibration.
- PPV is very low (about 0.25%–2.24%), and the fixed threshold creates substantial alert burden. These results do not support clinical deployment.
- The Challenge `SepsisLabel` already incorporates a six-hour lead convention. The target is entry into the benchmark's positive-label window, not independently observed biological sepsis onset.
- Set B is a second cohort within the same benchmark, not prospective or genuinely independent clinical validation.
- The Python 3.13.5 runtime differs from the documented Python 3.11 baseline, and no fully locked environment was used. A clean full-repository checkout/tree manifest was not completed in this network-restricted runtime.
- The GitHub-hosted full-cohort workflow run [#38677355122](https://github.com/culprit-k/VITALIS/actions/runs/38677355122) was cancelled and is **not** counted as a successful reproduction. A later clean-checkout/Python 3.11 run, [#38677774161](https://github.com/culprit-k/VITALIS/actions/runs/38677774161), is currently in progress; it is not counted as passed until it completes successfully and its outputs are reviewed.
- An independent statistician/clinical reviewer, governance/ethics sign-off, and a genuinely new cohort with independently defined event timing remain required.

**Research only:** VITALIS is not a medical device or a clinically validated decision-support system. Do not use these outputs to guide patient care.
