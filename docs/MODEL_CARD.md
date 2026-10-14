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
- Calibration, event-level detection, alert burden, subgroup performance, and uncertainty require additional analysis.
- No claim of clinical utility, novelty, or patentability is made.

## Governance
Never commit raw data, patient-level derived tables, individual predictions, credentials, or tokens to this repository. Do not interpret model output as medical advice.
