# Independent-cohort evaluation protocol for VITALIS

**Status:** protocol scaffold only. No independent cohort has been obtained, no policy is frozen, and no prospective or clinical validation has occurred.

## 1. Purpose and gate

This protocol defines the next evidence gate after exploratory Set-A operating-point analysis. It is not authorization to collect data or run a prospective study. Obtain institutional data-governance approval, ethics/IRB determination, qualified clinical/statistical oversight, and a written protocol before accessing any new patient data.

Set B has already been inspected and must remain evaluation-only; it cannot be reused to select a threshold or report a newly unbiased final estimate. The final retrospective external evaluation must use a genuinely new, independent cohort. If the intended claim is about clinical sepsis onset, the cohort needs a clinically defined and independently adjudicated onset/event time—not only the Challenge SepsisLabel convention.

## 2. Freeze the model before opening evaluation outcomes

Record and sign off on a versioned lockfile containing:

- Git commit SHA, source hashes, dependency versions, runtime/container specification, and feature schema.
- Intended population, care setting, inclusion/exclusion criteria, prediction index time, and the exact target/event definition.
- Model family and parameters, preprocessing, imputation, missingness handling, calibration method, and all fitted artifact hashes.
- Prediction horizon(s), threshold(s), alert refractory/suppression policy, and any data-quality/freshness rules.
- Primary endpoint, secondary metrics, confidence-interval method, subgroup plan, missing-data plan, and stopping criteria.
- Cost assumptions and their independent clinical/statistical rationale. If they remain abstract scenario weights, state that they are not clinical utility.

No threshold, feature, model, calibration, or subgroup definition may be changed after evaluation outcomes are inspected. Any change creates a new model version requiring a new independent evaluation cohort.

## 3. Cohort and label quality

Before modeling, document data provenance, participating sites, calendar period, care setting, measurement frequency, inclusion flow, missingness, and potential overlap with development datasets. Check for patient duplication across cohorts and for leakage through site, time, post-index data, treatment actions, or label construction.

Prefer an event time defined independently of the predictor and adjudicated using a prespecified clinical standard. Record uncertainty in event times and censoring/discharge/death. If only proxy labels are available, restrict claims to prediction of that proxy and do not describe the endpoint as biological onset.

## 4. Predeclared evaluation metrics

Report estimates with uncertainty intervals and denominators, overall and by predeclared clinically relevant site/population groups where sample size permits:

- Discrimination: AUROC and AUPRC, with event prevalence.
- Calibration: calibration-in-the-large, calibration slope, reliability plot, Brier score and log loss; compare with a simple prevalence/reference model.
- Fixed-policy performance: sensitivity, specificity, PPV, NPV, and confusion matrix at the frozen threshold.
- Workflow burden: alerts per patient-day, patients alerted, repeat-alert distribution, and alerts requiring review.
- Event-level performance: proportion of adjudicated events receiving an alert in the predeclared actionable window, lead-time distribution, and missed events.
- Data robustness: missingness/freshness, sensor or measurement failure, subgroup/site variation, and performance under documented domain shift.
- Safety/utility: only if a defensible, independently reviewed clinical utility definition and prospective workflow are available. Label-proxy costs are not a substitute for clinical outcomes.

Use patient-level resampling or an appropriate clustered design for uncertainty. Predeclare how repeated admissions, sites, and temporal clusters are handled. Calculate sample size from the desired precision for key event-level and safety estimates with a statistician; do not choose sample size based on a convenient number of rows.

## 5. Staged deployment boundary

1. **Retrospective external evaluation:** frozen pipeline, no tuning, independent cohort, full audit trail.
2. **Prospective silent-mode study:** only after approvals and a protocol; predictions do not influence care. Monitor data quality, drift, alert burden, and prespecified safety indicators.
3. **Clinical impact evaluation:** a separately approved study with appropriate comparison design, clinician workflow, training, adverse-event reporting, and stopping rules.

Do not move between stages solely because discrimination improves. A decision to stop, revise, or proceed should be made by independent clinical, statistical, engineering, and governance reviewers against prespecified criteria.

## 6. Reproducibility and privacy

Run from a clean, immutable checkout in a pinned environment. Record commit SHA, data manifest hashes, configuration, seeds, environment, logs, and output hashes. Store data and row-level predictions only in approved access-controlled environments; publish aggregate outputs only after disclosure review. Audit repository history and current artifacts for accidentally committed sensitive data or secrets.

## 7. Required sign-offs

- Clinical endpoint owner: ____________________
- Independent statistician: ____________________
- Data-governance / ethics authority: ____________________
- ML/software reviewer: ____________________
- Protocol version and date: ____________________
- Frozen model/configuration hash: ____________________

**Current conclusion:** the VITALIS results available today are retrospective research evidence on Challenge-label windows. This protocol is a planning artifact, not evidence that the system is externally validated, safe, clinically useful, or ready for patient care.


## Machine-checkable freeze gate

The repository now includes a deliberately incomplete scaffold at `configs/independent_evaluation_lockfile.template.json` and a validator at `scripts/validate_evaluation_lockfile.py`. Copy the template into the approved, access-controlled study workspace (do not fill it with sensitive cohort metadata in the public repository), complete the fields, and obtain the required sign-offs before outcome access.

Run:

    python scripts/validate_evaluation_lockfile.py /approved/private/path/evaluation_lockfile.json

The validator fails closed unless the lockfile is marked `frozen`, identifies a new independent cohort with a SHA-256 manifest hash, freezes the model and thresholds, specifies endpoints/analysis plans, and records clinical, statistical, governance, ethics-determination, and software-review approvals. It rejects Set B as the final evaluation cohort and rejects using the Challenge-label proxy for a clinical-onset claim.

This is a completeness and consistency guard, not evidence that signatures are authentic, ethics approval has been granted, a cohort is truly independent, or the model is clinically valid. Never commit the completed private lockfile or patient-level data to the public repository.
