# Patient-level availability and missingness-pattern audit

Run this descriptive audit against the local feature caches:

```bash
python scripts/audit_patient_level_availability.py \
  --set-a-cache /path/to/set-a-cache \
  --set-b-cache /path/to/set-b-cache \
  --output /path/outside/repo/patient_level_availability.json
```

For each selected feature, “available” means at least one finite value anywhere in a patient's record. The outcome summary is whether that patient has any positive hourly `SepsisLabel` in the record. The tool reports patient-level availability and the unadjusted positive-label-patient rate among patients with and without any observed value.

## Findings from the 14 October 2026 local-cache analysis

- Set A: 20,336 patients; 1,790 (8.80%) had at least one positive hourly label. Median record length was 39 hours; 90th percentile 55 hours.
- Set B: 20,000 patients; 1,142 (5.71%) had at least one positive hourly label. Median record length was 38 hours; 90th percentile 54 hours.
- DBP was observed in at least one row for 63.69% of Set-A patients versus 99.87% of Set-B patients.
- HCO3 was observed for 97.37% of Set-A patients versus 2.08% of Set-B patients; BaseExcess was 62.21% versus 2.79%.
- EtCO2 was observed for 0% of Set-A patients versus 16.08% of Set-B patients.
- FiO2, pH, and PaCO2 were each observed for about 59–65% of Set-A patients, versus about 29% of Set-B patients.
- Respiratory rate was observed for 99.86% of Set-A patients and 99.79% of Set-B patients, despite other respiratory/acid-base measurements shifting substantially.

## Interpretation limits

The association between feature availability and whether a patient ever has a positive hourly label is **unadjusted and descriptive**. For example, lab availability may be related to clinical suspicion, severity, treatment, duration of observation, site workflows, or other factors. This analysis cannot distinguish those mechanisms or establish causality. The similar median record lengths do not rule out confounding by duration or care processes.

Set B is used only to characterize evaluation-cohort shift. It is not used for feature selection, threshold selection, fitting, or tuning. No model is fitted. The output contains aggregate counts and rates only; no patient identifiers, raw records, or predictions are exported. VITALIS remains research-only and is not clinically validated.
