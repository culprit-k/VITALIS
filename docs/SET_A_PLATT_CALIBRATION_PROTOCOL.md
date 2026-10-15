# Patient-disjoint Set A Platt-calibration experiment

**Status:** predeclared before generating this experiment's Set B results. Research-only.

## Purpose
The physiology ablation improved AUROC/AUPRC but worsened Brier score. This follow-up tests whether a simple probability-calibration map trained only on Set A development patients improves probability quality when transported to Set B. It does not alter the original baseline, the original ablation, or their acceptance criteria.

## Fixed partitions and method
- Horizons: 1, 3 and 6 hours; seeds: 42, 123 and 2026.
- Per horizon/seed, split eligible Set A patients into 60% model-fit, 20% calibration, and 20% untouched holdout, with patient groups disjoint.
- Fit the existing logistic regression model on the model-fit partition only.
- Fit Platt scaling (logistic regression on the logit of the base model's predicted probabilities) on the separate Set A calibration partition only. Both target classes must be present and both model/calibrator fits must converge.
- Report raw and Platt-calibrated results for the temporal baseline and temporal-plus-personal-physiology model. The candidate is an exploratory comparison, not a selection target.
- Keep the threshold at 0.5 for comparability; it is a diagnostic reference, not clinically selected.
- Report AUROC, AUPRC, Brier, calibration intercept/slope, and paired patient-cluster bootstrap uncertainty for calibrated-minus-raw Brier score.
- Set B is frozen final evaluation only. No fitting, method selection, recalibration, threshold tuning, or model selection may use Set B.
- Outputs are aggregate metrics and cryptographic digests only; never persist row-level predictions, patient identifiers, caches, or raw data.

## Interpretation and stop rules
Platt scaling can fail to transport when prevalence, measurement processes, or cohort composition differ. A lower Brier score on Set B is not proof of clinical benefit and must not be used to tune the next iteration. If probability quality does not improve, report the negative result and investigate training objective/label prevalence using development data only. This is retrospective evaluation against Challenge label-window entry, not independently adjudicated biological onset or clinical validation.
