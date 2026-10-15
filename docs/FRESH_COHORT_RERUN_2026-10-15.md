# Fresh full-cohort rerun: Set A → Set B (15 October 2026)

**Status:** fresh data evaluation completed; strict source-reproduction and independent-review gates remain open.

## Cohort and archive checks

| Check | Set A | Set B |
|---|---:|---:|
| Patient files | 20,336 | 20,000 |
| Hourly rows | 790,215 | 761,995 |
| Positive hourly Challenge labels | 17,136 | 10,780 |
| Source columns | 41 | 41 |
| Generated features | 109 | 109 |

- Uploaded archive SHA-256: `b67472a9cfc549b5d2fc911475b952e52d264287d0be864fad5ef94781a2d8e6`.
- The archive hash matches the one recorded in the 14 October historical aggregate.
- ZIP integrity check passed; 40,336 `.psv` files parsed; no malformed rows, non-binary labels, or label reversions were detected.
- Fresh feature caches were written outside the Git repository. No raw data, caches, patient identifiers, or row-level predictions were committed.

## Evaluation protocol

- Horizons: 1, 3, and 6 hours; split seeds: 42, 123, and 2026.
- Two models per run: static baseline features and all 109 temporal/static features; 18 fits total.
- Set A uses a patient-disjoint 60% training / 40% unused holdout split. The holdout is not used for tuning.
- Set B is evaluation-only: no fitting, feature selection, calibration, or threshold selection.
- Reference threshold 0.5; six-hour refractory period; 200 patient-cluster bootstrap replicates for warning metrics.
- Target is entry into the Challenge `SepsisLabel`-positive window, **not independently observed sepsis onset**. The Challenge label already uses a six-hour lead convention.

## Results

Mean ± sample SD across the three predeclared seeds. The across-seed SD is descriptive, not a confidence interval.

| Horizon | Model | AUROC | AUPRC | Brier | Sensitivity @ 0.5 | PPV @ 0.5 | Alerts / at-risk patient-day | Window coverage |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 h | Static | 0.6634 ± 0.0022 | 0.00379 ± 0.00022 | 0.1937 ± 0.0058 | 0.5285 | 0.00248 | 1.7922 ± 0.1428 | 0.1201 ± 0.0038 |
| 1 h | Temporal | 0.6569 ± 0.0110 | 0.00317 ± 0.00015 | 0.1319 ± 0.0089 | 0.4012 | 0.00319 | 1.4620 ± 0.1126 | 0.1179 ± 0.0113 |
| 3 h | Static | 0.6813 ± 0.0043 | 0.01358 ± 0.00017 | 0.1806 ± 0.0055 | 0.5213 | 0.00842 | 1.5067 ± 0.0389 | 0.3286 ± 0.0071 |
| 3 h | Temporal | 0.6800 ± 0.0145 | 0.01264 ± 0.00048 | 0.1313 ± 0.0035 | 0.4151 | 0.01077 | 1.2763 ± 0.0807 | 0.2938 ± 0.0151 |
| 6 h | Static | 0.6868 ± 0.0050 | 0.02859 ± 0.00034 | 0.1745 ± 0.0062 | 0.5147 | 0.01903 | 1.3994 ± 0.0518 | 0.6017 ± 0.0174 |
| 6 h | Temporal | 0.6864 ± 0.0138 | 0.02643 ± 0.00102 | 0.1422 ± 0.0052 | 0.4457 | 0.02237 | 1.2566 ± 0.1054 | 0.5680 ± 0.0203 |

## Reconciliation and provenance limits

The fresh cohort counts, target-eligible row counts, feature count, and archive hash match the historical 14 October run. Most seed-level metrics agree with that aggregate to its displayed rounding. A small number of temporal-model operating-point results differ, most notably the 1-hour seed-42 run (AUROC difference about 0.000053; alert-rate difference about 0.00111 per at-risk patient-day; window-coverage difference about 0.00218). The 3-hour seed-2026 temporal coverage also differs by about 0.00109.

This runtime uses Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, and SciPy 1.17.0. The evaluation logic was reconstructed locally from the checked-in source content fetched through GitHub; this was **not** executed from a clean, byte-verified Git checkout. A numeric tolerance was not predeclared, so this is a descriptive reconciliation, not a formal pass. The aggregate JSON records the archive hash, source blob SHAs, environment, metrics, and the unresolved discrepancies.

## Required next steps

- Re-run from a clean checkout at a frozen commit with the checked-in cache builder and evaluator, using the documented Python 3.11 CI baseline and exact resolved dependency inventory.
- Investigate the noted temporal-model discrepancies before accepting aggregate reconciliation; preserve both reports rather than overwriting historical results.
- Obtain independent source-provenance and statistical review; issue #4 tracks the review checklist.

**Research-only:** Set B is another Challenge training cohort, not prospective clinical validation. These results do not establish safe clinical thresholds, clinical utility, or prediction of independently observed onset. Do not use VITALIS to guide patient care.
