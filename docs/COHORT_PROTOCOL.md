# Cohort and Evaluation Protocol

## Purpose
Define the cohort before training any model. All choices must be version-controlled and recorded in experiment metadata.

## Expected input
The PhysioNet/CinC Challenge 2019 hourly patient time series use one PSV file per patient. Files may include vital signs, laboratory measurements, demographic fields, and the challenge target SepsisLabel.

## Required integrity checks
1. Each file represents one patient; assign a stable local patient identifier without exposing identity.
2. Validate column names, data types, row count, and target values.
3. Preserve the original row order and explicitly document any time indexing.
4. Record missingness and never interpret missing measurements as normal values.
5. Keep source files read-only; write derived artifacts outside the repository.
6. Never commit patient-level rows, data files, predictions, or fitted models containing patient-specific information.

## Target timing
The challenge SepsisLabel already incorporates the challenge's six-hour lead convention. Do not shift it a second time. Describe it as the challenge label, not independently observed biological onset.

## Splitting
Split at the patient level before fitting transformations or selecting features. No patient may appear in more than one of train, validation, and test. If repeated or grouped external data are later introduced, define grouping before splitting.

## Missing data and preprocessing
Fit imputers, scalers, feature selection, and calibration only on training data within each split. Avoid forward/backward filling across patient boundaries. Any rolling feature must use only current and past observations.

## Baselines
Begin with a transparent baseline such as logistic regression before testing temporal or patient-specific features. Report exact features, hyperparameters, random seeds, split definition, software versions, and convergence status.

## Metrics
Report AUROC and AUPRC alongside threshold-specific sensitivity, specificity, PPV, NPV, calibration, and patient-level uncertainty. For alerting experiments, define alert thresholds, refractory period, alerts per patient-day, and event-level sensitivity before evaluating. Do not rely on row-level accuracy alone.

## Reproducibility gate
A result is provisional until cohort counts, patient splits, label distribution, missingness, warnings, and metrics have been regenerated from a clean run and independently checked.
