# Local VITALIS experiments on PhysioNet Challenge 2019

This file records locally run experiments using the PhysioNet Computing in Cardiology Challenge 2019 sepsis dataset. It contains aggregate metrics only; raw `.psv` files, patient identifiers, hourly records, and patient-level predictions must remain outside this repository.

Dataset source: https://physionet.org/content/challenge-2019/1.0.0/

## Experiment register

| Experiment | Data used | Configuration | Main result | Status |
|---|---|---|---|---|
| Preliminary baseline comparison | 5,000-patient deterministic subset of training_setA; subset seed 2026 | 3,500 train / 750 validation / 750 test patients; split seed 42; validation-selected thresholds | AUROC 0.7679 baseline vs 0.7827 temporal; average precision 0.0957 vs 0.1003 | Exploratory; internal test split |
| Repeated patient-level validation | Same 5,000-patient subset; split seeds 42, 123, 2026 | Each split 3,500 / 750 / 750 patients | Mean AUROC 0.7621 baseline vs 0.7730 temporal across three splits | Exploratory; SD across three splits is not a confidence interval |
| Patient-cluster bootstrap | Same 5,000-patient subset; fixed seed-42 split | 200 paired bootstrap replicates resampling test patients with all their hourly rows | Temporal-minus-baseline AUROC +0.0149 (95% percentile interval +0.0027 to +0.0288); average precision +0.0047 (-0.0029 to +0.0115); Brier score -0.0034 (-0.0050 to -0.0017) | Conditional on one split; not external validation |
| Full training_setA evaluation | 20,336 patients; 790,215 hourly rows; 17,136 positive hourly labels | Patient split seed 42; 14,235 train / 3,050 validation / 3,051 test patients | AUROC 0.6839 baseline vs 0.6778 temporal | **Provisional**: SGDClassifier fitted for only five iterations with convergence warnings; do not treat as final metrics |
| Full-cohort rerun (14 Oct 2026) | All 20,336 training_setA patients; 790,215 hourly rows | Seed 42; patient split 13,014 / 3,254 / 4,068; fixed threshold 0.5; LogisticRegression max_iter=500 | AUROC 0.7623 baseline vs 0.7873 temporal; AUPRC 0.0777 vs 0.0842 | Aggregate local optimized harness aligned to repository algorithm; direct CLI reproduction and patient-cluster intervals still pending |
| Alert-burden analysis | Aggregate predictions/labels from local experiments | Threshold and refractory-period based analysis | Intended to characterize alert counts; challenge-label windows are not independent clinical events | Exploratory; do not call these a validated clinical false-alarm rate |

## Key methodology notes

- The challenge-provided `SepsisLabel` is already shifted according to the challenge's early-warning definition. Do not shift it again or describe the start of positive labels as independently observed clinical onset.
- Splits are patient-level so a patient's hourly rows do not cross train/validation/test partitions.
- Classification thresholds are selected on validation data, not the test partition.
- Hourly-row metrics are not patient-level event-detection metrics and may overweight longer ICU stays.
- The temporal features used in the early experiments are simple lag/difference and rolling summaries. They are not yet evidence that VITALIS's proposed patient-specific baseline approach is novel or clinically useful.
- All results are retrospective internal experiments on the same challenge dataset. No independent external cohort, prospective validation, clinical impact study, novelty assessment, or patentability assessment is established by these results.

## Reproduction and provenance

The local reports/results that informed this register were created on 2026-10-14 UTC, but that is the report artifact timestamp and is **not asserted to be the exact time each experiment ran**. The experiment seeds and cohort/split counts are recorded above where available. Keep the local raw dataset outside GitHub and rerun using the repository's documented scripts before treating historical metrics as reproduced by the current repository code.

## Dataset integrity caution

A prior generated file called `cohort_full_verified.csv` was found to contain only 375,602 rows and 9,668 unique patients, not the 790,215 rows and 20,336 patients claimed by its build log. It must not be used as the full cohort. The full-cohort report says its evaluation read the raw training_setA files directly, but the model fit used only five SGD iterations and produced convergence warnings, so its scores remain provisional.
