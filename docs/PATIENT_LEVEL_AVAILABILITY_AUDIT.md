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


## Follow-up: duration-stratified missingness and source provenance (14 October 2026)

### What the official documentation establishes

The [official PhysioNet/CinC Challenge 2019 documentation](https://physionet.org/content/challenge-2019/1.0.0/) describes hourly records from two publicly available hospital systems plus a third system withheld for scoring. It defines the source variables and states that `NaN` means no measurement was recorded for that hour. The challenge label is shifted six hours before the defined sepsis time. The documentation does **not** attribute a particular Set A/Set B availability difference to a named clinical workflow or establish why a measurement was absent.

This distinction matters: the source documents variable meanings and broad cohort provenance, while our local analysis measures the availability patterns present in the supplied files. A site/workflow explanation remains a hypothesis until supported by additional provenance or clinical data.

### Record-duration strata

Availability here means at least one finite measurement for a patient across the entire record. Record duration is the number of hourly rows. The following are descriptive patient-level strata; no inferential model or causal adjustment was performed.

| Record duration | Set A patients | Set A ever-positive label rate | Set B patients | Set B ever-positive label rate |
|---|---:|---:|---:|---:|
| 1–24 h | 4,944 | 13.51% | 5,597 | 8.04% |
| 25–48 h | 10,950 | 3.38% | 10,275 | 2.17% |
| 49–72 h | 3,911 | 5.80% | 3,629 | 3.97% |
| 73+ h | 531 | 98.87% | 499 | 65.13% |

The very high ever-positive label fraction in the 73+ hour stratum—especially in Set A—is a warning against treating record duration as an ordinary nuisance variable. The challenge's sepsis-label construction and inclusion rules are related to clinical timing, and the official description specifies a 72-consecutive-hour antibiotic criterion in its suspicion definition. This does not prove that the rule alone explains the observed duration pattern; selection, label construction, and clinical course can all contribute. The duration bins are exploratory and must not be used as a deployment eligibility rule.

### Availability rises with duration for several measurements

Patient-level availability (%) by duration stratum:

| Feature | Cohort | 1–24 h | 25–48 h | 49–72 h | 73+ h |
|---|---|---:|---:|---:|---:|
| DBP | A | 55.8 | 63.8 | 70.1 | 87.8 |
| DBP | B | 99.9 | 99.8 | 99.8 | 100.0 |
| HCO3 | A | 91.6 | 99.0 | 99.7 | 100.0 |
| HCO3 | B | 0.6 | 2.1 | 3.3 | 9.2 |
| FiO2 | A | 47.4 | 59.4 | 67.6 | 92.8 |
| FiO2 | B | 18.4 | 29.3 | 39.1 | 73.7 |
| pH | A | 51.2 | 65.9 | 74.9 | 95.9 |
| pH | B | 19.1 | 28.9 | 37.3 | 71.7 |
| Lactate | A | 23.9 | 38.4 | 48.8 | 81.4 |
| Lactate | B | 16.3 | 23.6 | 30.6 | 62.1 |
| EtCO2 | A | 0.0 | 0.0 | 0.0 | 0.0 |
| EtCO2 | B | 8.2 | 16.4 | 22.6 | 51.5 |

The duration gradient is substantial for several features in both cohorts. However, duration alone does not explain the cross-cohort pattern: DBP remains almost universally available in Set B but is less available in shorter Set-A records; HCO3 remains uncommon in Set B even among longer records; and EtCO2 is absent throughout Set A while its availability increases with duration in Set B.

### Availability also differs by ever-positive label within duration strata

For selected features, the percentage of patients with any observed value was higher among ever-positive-label patients than among patients with no positive label in most shorter and middle-duration strata. Examples:

| Cohort and duration | FiO2 available: ever-positive | FiO2 available: no positive label | Lactate available: ever-positive | Lactate available: no positive label |
|---|---:|---:|---:|---:|
| A, 1–24 h | 68.4% | 44.1% | 51.9% | 19.6% |
| A, 25–48 h | 82.2% | 58.6% | 66.5% | 37.5% |
| A, 49–72 h | 83.7% | 66.6% | 70.5% | 47.4% |
| B, 1–24 h | 47.8% | 15.8% | 40.0% | 14.3% |
| B, 25–48 h | 72.2% | 28.3% | 59.6% | 22.8% |
| B, 49–72 h | 77.8% | 37.5% | 63.2% | 29.2% |

These are crude comparisons, not adjusted associations. “Ever-positive label” uses any positive hourly `SepsisLabel` anywhere in the record; it is not a separately adjudicated clinical outcome. Because availability is assessed over the whole record, it can include measurements taken after the first positive label. Therefore these numbers **cannot** establish prospective predictive value or support a claim that measurement availability independently predicts sepsis.

### Evidence versus hypotheses

**Observed in the supplied data**
- Large Set A/Set B availability differences persist after stratifying patients into broad record-duration bands.
- For FiO2, pH, and lactate, availability is often higher among patients with at least one positive challenge label within the same duration band.
- The two cohorts have similar median record lengths (39 vs 38 hours), but their availability profiles differ markedly.

**Plausible, not demonstrated by this audit**
- Different measurement ordering or documentation practices between hospital systems.
- Clinical suspicion or illness severity influencing which laboratory/respiratory tests are ordered.
- Differences in patient mix, care pathways, or cohort/label selection influencing both record length and observed measurements.

**Not established**
- The exact cause of any feature shift.
- Whether missingness is MCAR, MAR, or MNAR.
- Whether feature availability has an independent association after adequate adjustment.
- Whether the differences can be safely corrected by imputation or recalibration.

### Consequences for VITALIS

1. Keep Set B evaluation-only; do not use it to choose features, thresholds, transformations, or model settings.
2. Keep training-set feature eligibility frozen from Set A or external protocol knowledge; do not add EtCO2-derived features to a Set-A-trained model based on Set-B availability.
3. Report cohort-specific availability and duration-stratified descriptive results alongside model metrics.
4. If a future inferential analysis is justified, pre-specify the estimand and covariates, account for patient-level dependence and label/timing limitations, and keep all model-selection decisions isolated from Set B.
5. Do not describe this analysis as clinical validation, a missingness-mechanism test, or evidence of clinical utility.

The aggregate JSON contains only cohort-level counts and rates. Raw records, patient IDs, caches, and row-level predictions remain outside Git.


## Exact-source reproduction check (14 October 2026)

The duration-stratified audit was rerun against the local Set A and Set B feature caches using the exact checked-in script bytes. The local script's Git blob SHA was verified as `d745b47febb2bb0f28edb36fb289a51ae4523b1d`, matching the source blob on `work/exact-checkout-reproduction`. The committed regression test file's blob SHA was also verified as `f8ff12908c845460c38bc4c45710ddc6de076aea`; the exact checked-in tests passed locally (3 passed).

The source-run output remained outside the repository at `/mnt/data/vitalis-local/patient_level_audit_committed_script_rerun.json` (SHA-256 `dadc3d1ce8c4950f7221861e038ac8151c7d121ce7a6febc8b8ec007497e4629`). It reproduced the cohort totals:
- Set A: 20,336 patients, 790,215 hourly rows, 1,790 patients with any positive hourly challenge label; median/p90 record lengths 39/55 hours.
- Set B: 20,000 patients, 761,995 hourly rows, 1,142 patients with any positive hourly challenge label; median/p90 record lengths 38/54 hours.

Reconciliation against the existing aggregate artifact found exact agreement for cohort counts and record-length summaries, and agreement within (10^{-12}) for all 11 features' overall patient availability and unadjusted ever-positive-label rates by feature availability. The duration-stratum patient counts and positive-label rates also matched; displayed duration-specific availability rates matched at the report's stated precision. The aggregate JSON records this reproduction check and its provenance.

This closes the **local exact-source reproduction** item for the patient-level audit. It does not establish a full Git checkout of the repository, explain the cause of cohort shifts, or provide inferential or clinical validation. Set B remained evaluation-cohort characterization only. The source-run output, caches, patient identifiers, and row-level data remain outside Git.
