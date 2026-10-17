# VITALIS external validation stage — protocol and readiness gate

**Status:** protocol preparation started; external-cohort execution is **blocked pending authorized data access and institutional review**.  
**Protocol version:** 0.1, 18 October 2026  
**Scope:** retrospective, patient-level external evaluation of the frozen VITALIS research model. This is not prospective clinical validation or evidence of clinical utility.

## 1. Purpose and claims boundary

Evaluate whether the frozen VITALIS pipeline generalizes to a separate critical-care cohort, including discrimination, calibration, warning lead time, missing-data robustness, and alert burden. The PhysioNet Challenge 2019 Set B is a benchmark test partition, not an independent external clinical cohort. Do not describe Set B performance as external clinical validation.

No live clinical use, patient-care decisions, diagnosis, triage, treatment recommendations, or device claims are in scope.

## 2. Proposed external cohorts

### Primary candidate: eICU Collaborative Research Database (eICU-CRD)

Use as a geographically distributed, multi-centre retrospective ICU cohort if the project team obtains credentialed access and approval for the intended research. Define the cohort and label mapping before inspecting model performance. eICU is a candidate, not yet an approved or accessed dataset.

Official access guide: https://eicu.mit.edu/_gettingstarted/access/

### Secondary candidate: MIMIC-IV

Use as a distinct retrospective ICU cohort only if the intended access and governance requirements are met. Since this is also a US ICU dataset, it provides an independent database/institutional source but does not by itself establish international or prospective generalization.

Official project page: https://physionet.org/content/mimiciv/

**Access controls:** PhysioNet states credentialed datasets require individual credentialing, required human-subjects/data-protection training, and acceptance of the applicable data use agreement. Access must not be shared. Each researcher must satisfy the dataset's own current requirements. Do not upload restricted data, patient-level rows, derived patient-level predictions, or caches to GitHub, ChatGPT, or unapproved services. See https://physionet.org/about/faqs/ and the applicable dataset access pages.

## 3. Mandatory pre-analysis lock

Before any external outcome is scored, create and archive a signed-off run manifest containing:

- Exact Git commit SHA, source-manifest hash, model/configuration hash, environment lock, and evaluator version.
- Frozen feature list, units, sampling/resampling rules, missingness handling, baseline warm-up, and minimum measurement coverage.
- Cohort inclusion/exclusion criteria, time-zero, prediction horizons, endpoint definition, censoring and competing-event handling.
- Label mapping and adjudication rules, documented before model predictions are inspected.
- Patient-level split strategy for any fitting/calibration; no patient can appear in multiple partitions.
- Primary and secondary endpoints, confidence-interval method, subgroup plan, missing-data analyses, and stopping/reporting rules.
- A declaration that no external-cohort labels will be used to tune features, hyperparameters, calibration, thresholds, or model choice.

The model and operating threshold remain frozen for the primary external test. Any recalibration or adaptation must be a separately specified secondary analysis, clearly labeled as such, and must not replace the primary frozen-model result.

## 4. Target population and outcome mapping

Do not assume a sepsis label is portable across databases. The PhysioNet Challenge 2019 SepsisLabel identifies a challenge-specific positive window; it is not equivalent to an independently adjudicated sepsis onset. External cohorts may use different coding, suspicion-of-infection, organ-dysfunction, and timestamp conventions.

Before execution, publish a cohort-specific mapping table covering:
- adult/pediatric inclusion (default proposal: adults only; justify and lock before extraction);
- ICU stay and transfer handling, repeated admissions, and patient identifiers;
- available vital-sign channels and units;
- label source, criteria, timestamp precision, and label uncertainty;
- medication/lab availability and temporal leakage exclusions;
- data availability windows and censoring;
- all deviations from the development cohort.

If a defensible endpoint mapping cannot be established, stop and report the cohort as not evaluable rather than forcing a proxy label.

## 5. Frozen primary evaluation

Evaluate at **1, 3, and 6 hours** before the predeclared endpoint, provided timestamp resolution supports those horizons. Use the same feature/quality checks and preprocessing contract as the frozen pipeline wherever technically defensible. Report unavailable channels and protocol deviations.

Primary metrics:
- AUROC and AUPRC with 95% confidence intervals.
- Brier score and calibration intercept/slope; reliability plots when sample support permits.
- Sensitivity, specificity, positive predictive value, and false alerts per patient-day at a threshold frozen before external evaluation.
- Event-level sensitivity, lead-time distribution, and proportion of events detected within the predeclared actionable window.
- Decision-curve/net-benefit analysis only if a clinically defensible action and utility range are specified with clinical collaborators; otherwise mark not assessed.
- Coverage, abstention/insufficient-data rate, alert burden, and performance under missing/noisy observations.
- Patient-level bootstrap confidence intervals; resample patients, not hourly rows.

Report denominators, prevalence, event counts, missingness, confidence intervals, subgroup sizes, and failures. Do not use hourly-row random splits. Do not present repeated time windows as independent patients.

## 6. Baselines and sensitivity analyses

Predeclare comparisons with:
1. the frozen VITALIS model;
2. a simple clinical-score baseline if the required variables can be mapped faithfully;
3. a non-personalized temporal/statistical baseline;
4. ablations of the adaptive baseline and trajectory components, where available.

Sensitivity analyses should include label/timestamp uncertainty, alternate defensible endpoint definitions, minimum coverage, measurement cadence, missingness, and cohort shift. Keep these separate from the primary frozen evaluation. Do not select the best result and present it as the sole primary result.

## 7. Data security and reproducibility

- Execute only in a storage/compute environment permitted by the dataset DUA and institutional policy.
- Keep raw restricted data, row-level labels/predictions, patient identifiers, and caches out of this repository and out of retained CI artifacts.
- Retain only reviewed aggregate metrics, disclosure-reviewed figures, non-identifying logs, and environment/run manifests if the data-use terms permit.
- Do not send restricted patient-level data to third-party APIs or LLM services. Follow PhysioNet's current data-use and zero-data-retention guidance.
- Record data version, access approval date, extraction code commit, and checksum locally without exposing restricted file content.
- Have an independent reviewer reproduce the aggregate outputs in the authorized environment before any public claims.

## 8. Governance gates before execution

The external cohort run remains **BLOCKED** until the project has all applicable items below:

- [ ] Named faculty/supervisor and clinical collaborator for the research question and endpoint mapping.
- [ ] Written determination from the relevant institutional ethics/IRB/research office about whether the proposed secondary-data analysis requires approval, exemption, or another review.
- [ ] Dataset credentialing, required training, and DUA completed by each person accessing the data.
- [ ] Data-management plan identifying approved storage, access control, retention, incident response, and permitted outputs.
- [ ] External-validation protocol reviewed by an independent statistician/clinical reviewer.
- [ ] Cohort definition, label mapping, frozen model, primary metrics, threshold, and analysis plan signed off before running the external test.
- [ ] A documented decision that the selected cohort actually supports the intended target population and endpoint.

This checklist is not legal or ethics approval; the responsible institution and data provider make those determinations.

## 9. Stage tracker

| Work item | Status | Evidence needed to close |
|---|---|---|
| Protocol scaffold | In progress | Review and lock v1.0 |
| Dataset selection | Candidate only | Written rationale and availability audit |
| Institutional review | Not started / unknown | Written institutional determination |
| Credentialed access | Not verified | Dataset-provider approval for the researcher |
| Cohort mapping | Blocked | Approved mapping document, completed without looking at model performance |
| Frozen external run manifest | Blocked | Commit/configuration hashes and pre-analysis lock |
| External evaluation | Not run | Authorized clean run and aggregate results |
| Independent review | Not started | Signed review and issue log |
| Clinical utility / prospective evaluation | Not started | Separate study protocol, approvals, and clinical site; not inferred from retrospective results |

## 10. Immediate next actions

1. Identify a faculty supervisor and a clinical collaborator; agree on the target population and endpoint.
2. Review current eICU and MIMIC-IV access terms and apply individually if eligible.
3. Obtain the institution's written ethics/research-governance determination before accessing or analysing restricted data for this project.
4. Complete cohort and endpoint mapping in a reviewable document.
5. Freeze the model and analysis plan, then run the external evaluation only in an authorized environment.

**No external clinical validation result is claimed by this protocol.**
