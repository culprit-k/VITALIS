# Data Dictionary and Semantics

## Challenge target
- SepsisLabel: binary label supplied by the PhysioNet/CinC Challenge 2019. It uses a six-hour lead convention in the challenge construction. Do not shift the label again or call its first positive row independently observed clinical onset.

## Common source fields
The challenge data may include fields such as HR, O2Sat, Temp, SBP, MAP, DBP, Resp, EtCO2, BaseExcess, HCO3, FiO2, pH, PaCO2, SaO2, AST, BUN, Alkalinephos, Calcium, Chloride, Creatinine, Bilirubin_direct, Glucose, Lactate, Magnesium, Phosphate, Potassium, Bilirubin_total, TroponinI, Hct, Hgb, PTT, WBC, Fibrinogen, Platelets, Age, Gender, Unit1, Unit2, HospAdmTime, and ICULOS. Actual columns vary by data release and file; inspect files rather than assuming all fields are present.

## Interpretation rules
- Missing is not equivalent to normal.
- Units and valid ranges must be verified against dataset documentation before clinical interpretation.
- A feature is eligible only if it would be available at prediction time.
- Demographic or care-location fields must be reviewed for leakage and transportability.
- Patient-specific baseline features must be computed from prior observations only, never future rows.

## Dataset provenance
Use the official PhysioNet/CinC Challenge 2019 landing page and its data-use requirements: https://physionet.org/content/challenge-2019/1.0.0/
