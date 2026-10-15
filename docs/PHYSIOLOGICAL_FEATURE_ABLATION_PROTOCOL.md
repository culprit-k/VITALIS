# Predeclared physiological-feature ablation protocol

**Status:** frozen before the ablation's Set B results are generated. Research-only; not clinical validation.

## Question
Does adding causal, patient-relative deviation features to the reproduced baseline change retrospective prediction of entry into the Challenge 2019 SepsisLabel-positive window?

## Models
1. Static baseline: existing raw baseline feature schema.
2. Temporal baseline: existing raw, lag, delta and trailing-mean feature schema.
3. Candidate physiology ablation: exactly the temporal baseline features plus prior-only robust personal-deviation z features for HR, O2Sat, Temp, SBP, MAP, DBP and Resp.

The candidate uses the existing `add_patient_baseline_features` implementation with `min_history=5` and `min_scale=1e-3`. At row t, only observations strictly before t contribute to the personal reference; patient boundaries are isolated. The current observation is compared to that prior reference. This tests the causal personal-baseline feature idea, not the full streaming adaptive twin with CUSUM/persistence logic.

## Fixed evaluation
- Official Set A/Set B caches and exact expected cohort counts.
- Horizons: 1, 3 and 6 hours; seeds: 42, 123 and 2026.
- Same patient-group split protocol as the reproduced experiment: 60% Set A training patients; remaining 40% held out and unused.
- Same logistic-regression family, median imputation with missingness indicators, standard scaling, balanced class weights, fixed threshold 0.5 and six-hour alert refractory period.
- 200 patient-cluster bootstrap replicates for aggregate alert metrics.
- Set B is used only to calculate frozen models' descriptive metrics. It is not used for fitting, feature selection, calibration, threshold selection or model selection.
- Metrics include AUROC, AUPRC, Brier score, threshold-specific metrics, forecast-window coverage, alerts per at-risk patient-day and patient-cluster uncertainty.

## Interpretation and stop rules
This is an exploratory ablation on a second Challenge training cohort, not independent external or prospective validation. The target is Challenge label-window entry, not independently adjudicated biological onset. The 0.5 threshold is a fixed reference, not clinically selected. Do not select the candidate based on Set B results or tune parameters against Set B. Any further model selection must use development data only, freeze the full model/policy and be assessed on a genuinely new independent cohort.

No raw rows, patient identifiers, individual predictions or patient-level derived artifacts may be retained in GitHub Actions artifacts.
