# Model Evaluation Plan

## Minimum comparison
1. Establish a simple, reproducible baseline before adding adaptive features.
2. Compare baseline features with predeclared temporal and patient-relative features.
3. Use the same patient-level splits and evaluation definitions for each comparison.
4. Tune thresholds only on validation data; freeze them before test evaluation.

## Report
- Patient and hourly-row counts per split, plus positive-label counts.
- AUROC and AUPRC with patient-level uncertainty intervals where feasible.
- Sensitivity, specificity, PPV, NPV, and calibration at the chosen threshold.
- Event-level sensitivity, detection lead time, and alerts per patient-day for alerting analyses.
- Convergence warnings, missingness, software versions, random seeds, and failed runs.

## Prohibited shortcuts
Do not split hourly rows randomly across train and test. Do not fit preprocessing on the full dataset. Do not tune on the test set. Do not report accuracy alone. Do not present challenge labels as independently observed onset. Do not claim clinical readiness from retrospective challenge data alone.
