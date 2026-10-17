# VITALIS Research Model Card

## Intended use
Research and education on longitudinal physiological modeling using retrospective, de-identified challenge data.

## Out-of-scope use
Not for patient care, diagnosis, triage, treatment decisions, or real-time deployment. Not a medical device.

## Data
The initial planned dataset is PhysioNet/CinC Challenge 2019. Dataset-specific terms apply. The challenge label uses a six-hour lead convention.

## Methods
The current baseline workflow uses logistic regression with median imputation, missingness indicators, and standard scaling. A temporal variant adds per-patient lagged values, one-step differences, and trailing means. Splits are at the patient level.

## Evaluation
The script reports row-level AUROC, AUPRC, Brier score, threshold-specific sensitivity, specificity, PPV, NPV, and confusion matrix. It records patient and row counts by split.

## Known limitations
- No external validation or prospective evaluation is included.
- Hourly observations are correlated, so row-level metrics can overstate effective sample size.
- A fixed threshold of 0.5 is a reference point, not a clinically justified operating point.
- Missingness and measurement frequency may encode care processes and introduce bias.
- Retrospective calibration and alert-burden analyses exist, but results do not establish clinically usable probabilities or a safe operating point. The project reports Brier/log loss against a constant-prevalence reference, reliability bins/ECE, and patient-cluster uncertainty for selected metrics; calibration intercept/slope and patient-cluster sandwich intervals are implemented as diagnostics, but their updated full-cohort artifact is pending.
- No claim of clinical utility, novelty, or patentability is made.

## Governance
Never commit raw data, patient-level derived tables, individual predictions, credentials, or tokens to this repository. Do not interpret model output as medical advice.


## Supervised horizon-forecasting research branch

A separate research workflow forecasts whether a future row enters the Challenge \`SepsisLabel\`-positive window within 1, 3, or 6 hours. Current-positive rows and each patient's final H rows are excluded. This target is **not independently observed biological sepsis onset**: the Challenge label itself uses a six-hour lead convention.

The horizon workflow compares static and temporal logistic-regression features. Within Set A, patient groups are separated into approximately 60% model training, 20% Platt calibration, and 20% untouched operating-point development holdout. Set B has been used as a final retrospective cohort for descriptive comparisons only; it must not be reused to select thresholds or cost assumptions.

### Findings that constrain intended use

- Full-cohort cross-cohort metrics are documented in [the horizon results report](FULL_COHORT_HORIZON_CROSS_COHORT_RESULTS.md). Differences between static and temporal ranking performance are small or horizon-dependent in this evaluation; no model is selected as clinically superior.
- Platt recalibration reduces Brier score relative to raw class-weighted scores, but calibrated Set-B Brier scores remained slightly worse than the constant-prevalence reference across model/horizon pairs. This does not establish adequate probability calibration. General calibration evaluation now records intercept/slope point estimates and explicit undefined states; a further diagnostic reports patient-cluster sandwich standard errors and asymptotic 95% intervals on frozen scores. These are conditional retrospective diagnostics and do not recalibrate predictions or establish clinical utility. The latest-main full-cohort workflow [#39019018791](https://github.com/culprit-k/VITALIS/actions/runs/39019018791) is in progress; do not cite its results until the aggregate artifact and strict reconciliation have been inspected.
- The paired comparison reports conditional patient-cluster intervals for AUROC, AUPRC, Brier score, and log loss in [the paired results report](HORIZON_PAIRED_MODEL_COMPARISON_RESULTS_2026-10-15.md). It is descriptive retrospective evidence, not independent validation or a license to tune on Set B.
- The cost-sensitive operating-point framework and its uncertainty analysis are described in [the utility framework](UTILITY_OPERATING_POINT_FRAMEWORK.md) and [the utility bootstrap report](HORIZON_UTILITY_BOOTSTRAP_RESULTS_2026-10-15.md). At a 6-hour horizon and threshold 0.005, reported mean forecast-window coverage was about 99.3%, but burden was about 4.20 alerts per at-risk patient-day and row-level PPV about 1.45%. The preferred threshold changes under different assumed missed-window costs. These costs are illustrative, not clinician-elicited; no threshold is endorsed.
- Legacy full-cohort reports generated from reconstructed local working copies remain provenance-qualified and are not claimed as byte-identical clean-checkout reproductions. Separate successful clean-checkout full-cohort artifacts are linked in the [project status](PROJECT_STATUS.md); the newest reproduction, including patient-cluster calibration coefficient intervals, is pending.

## Evidence gaps

No new independent cohort with independently defined/adjudicated onset timing, prospective silent-mode study, clinical impact evaluation, or clinical utility study has been completed. Fairness, subgroup safety, real-device signal quality, workflow effects, and sensor integration are not established. The synthetic adaptive-twin demonstrations validate software behavior on constructed inputs only.

**Current status:** VITALIS is a research prototype for retrospective algorithm development and education. Do not use its outputs to guide diagnosis, triage, treatment, or other patient-care decisions. Before any external/prospective study, require a frozen model/policy, a clean-checkout/fresh-cache reproduction, independent clinical/statistical review, data-governance and ethics determinations, and a genuinely new independent cohort.
