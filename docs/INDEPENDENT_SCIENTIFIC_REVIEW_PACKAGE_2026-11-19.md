# VITALIS — independent scientific review package

**Version:** 1.0 | **Prepared:** 19 November 2026  
**Repository:** https://github.com/culprit-k/VITALIS  
**Main snapshot at preparation:** `80edfe4b8df969fc7b84129023e44b316a3455f5`  
**Status:** Invitation package prepared; no independent reviewer has signed off.

## 1. Requested review

VITALIS seeks an independent, critical review by a statistician, clinical informatician, critical-care researcher, sepsis-prediction methodologist or reproducible-ML researcher who did not author the analysis.

Please inspect the actual code, protocol, workflows and aggregate evidence; identify blocking, major and minor concerns; list evidence not available; and recommend one disposition:

- **REVISION REQUIRED**
- **NOT READY**
- **RESEARCH-CODE RELEASE CANDIDATE WITH LIMITATIONS**
- **UNABLE TO ASSESS**

This is not a request for endorsement, co-authorship, clinical approval or patient-care advice. A negative or conditional conclusion is acceptable and useful.

## 2. Project summary and component boundaries

VITALIS explores an **Adaptive Physiological Digital Twin for Early Prediction of Clinical Deterioration**: a software representation that learns a person's reference physiology from earlier accepted observations and describes later deviations, persistence and cross-system patterns.

The repository contains distinct components that must not be conflated:

1. **Adaptive-twin heuristic:** personal-reference, deviation, persistence and trajectory logic. Its score is unitless and heuristic, not a calibrated probability, diagnosis, alarm or treatment recommendation.
2. **Retrospective supervised experiments:** logistic-regression baselines and a temporal feature variant evaluated against PhysioNet/CinC Challenge 2019 Set A and Set B.
3. **Streaming interface and synthetic demo:** timestamped data contracts and generated signals for software testing. This is not a physical monitor or evidence of clinical performance.
4. **Hardware concept:** proposed sensor-to-gateway integration. No completed, validated wearable or patient-connected hardware device exists.

The digital-twin concept and supervised benchmark are related research directions, not one integrated and clinically validated prediction system.

## 3. Review scope

**In scope:** endpoint/horizon semantics; cohort provenance; patient-level partitioning; temporal leakage; missingness and preprocessing; Set B isolation; statistical estimands and uncertainty; discrimination and probability quality; calibration; alert burden; CPU/BLAS-sensitive reproducibility; privacy/artifact hygiene; and the claims justified by the evidence.

**Out of scope:** clinical validation or utility; diagnosis, triage, monitoring, treatment or alarm approval; human hardware connection; regulatory clearance; ethics approval or dataset permission; novelty, patentability or freedom-to-operate opinions.

## 4. Data, target and model

### Cohorts

The documented cohort audit reports:

| Cohort | Patient files | Hourly rows | Positive source labels |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 |
| Set B | 20,000 | 761,995 | 10,780 |

These are two cohorts from the same Challenge benchmark. Set B is held-out evaluation data, **not independent external clinical validation**.

### Target

The supervised experiment forecasts entry into the Challenge `SepsisLabel`-positive window over 1-, 3- and 6-hour horizons. The Challenge label incorporates a six-hour lead convention. It is not independently adjudicated biological sepsis-onset time. Inspect the implementation of current-positive exclusions, incomplete patient tails and patient boundaries.

### Model and preprocessing

The documented baseline uses logistic regression with median imputation, missingness indicators and standard scaling. The temporal variant adds per-patient lagged values, one-step differences and trailing means. Splits are patient-level. Verify the implementation and fit scope in the exact source rather than treating this summary as proof.

Set B must remain evaluation-only: no fitting, feature selection, calibration fitting, threshold selection, model selection or policy tuning may use Set B outcomes.

## 5. Reproducibility evidence

### Frozen rule

The preserved aggregate is `results/horizon_cross_cohort_2026-10-14.json`. The predeclared rule compares mean and sample SD across seeds 42, 123 and 2026 for seven metrics, two models and three horizons: 42 mean/SD pairs and 84 scalar values. Every scalar must match after rounding to six decimal places. Neither the historical baseline nor acceptance tolerance was changed to obtain a pass.

### CPU-dispatch investigation

Controlled Python 3.11 runs using OpenBLAS `SkylakeX` passed the unchanged comparison:

- [Run #38857500125](https://github.com/culprit-k/VITALIS/actions/runs/38857500125): 42/42 pairs, 84/84 scalars.
- [Repeat #38857522352](https://github.com/culprit-k/VITALIS/actions/runs/38857522352): 42/42 pairs, 84/84 scalars.

Runs forced to OpenBLAS `Haswell` repeated the five temporal-model mismatches: [#38855115107](https://github.com/culprit-k/VITALIS/actions/runs/38855115107) and [#38855119347](https://github.com/culprit-k/VITALIS/actions/runs/38855119347).

The workflow now requests `OPENBLAS_CORETYPE=SkylakeX` and checks AVX-512F capability plus the loaded OpenBLAS architecture before cohort download. This strongly supports CPU-kernel-dependent floating-point variation as the explanation for the observed discrepancy. It is not a separate causal decomposition of each metric and does not guarantee identical results on all hardware.

A later extended full-cohort run [#39057821508](https://github.com/culprit-k/VITALIS/actions/runs/39057821508), on source commit `14440230ff19bd1ade378374c47158cda321f628`, completed with zero reconciliation mismatches. Its aggregate-only artifact was [#12111943281](https://github.com/culprit-k/VITALIS/actions/runs/39057821508/artifacts/12111943281), SHA-256 `565f0ccecb900c6d41566de8e0dfbc61e79793874079c9bd124b8c4a8f05980e`. GitHub artifact retention is finite; if unavailable, mark it unavailable rather than claiming to have inspected it.

**Current-head qualification:** that full-cohort run did not execute on current main `80edfe4b8df969fc7b84129023e44b316a3455f5`. Current main has subsequent documentation/community changes and standard CI evidence, but a fresh full-cohort run on the exact current main snapshot remains an open release gate. Do not describe the older full-cohort run as if it executed on current main.

Standard CI is not full-cohort reproduction. It tests installation, compilation, source manifest, repository/history hygiene, synthetic demos/bench and unit tests; it does not rerun the full Challenge cohorts.

## 6. Selected retrospective results

The documented full-cohort report gives these Set B results (mean ± sample SD across seeds):

| Horizon | Model | AUROC | AUPRC | Brier | Alerts / at-risk patient-day | Positive-window coverage |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Static | 0.663385 ± 0.002217 | 0.003793 ± 0.000219 | 0.193701 ± 0.005846 | 1.792175 ± 0.142768 | 0.120058 ± 0.003821 |
| 1 h | Temporal | 0.656890 ± 0.010999 | 0.003170 ± 0.000148 | 0.131964 ± 0.008834 | 1.461593 ± 0.113243 | 0.117156 ± 0.012230 |
| 3 h | Static | 0.681317 ± 0.004288 | 0.013583 ± 0.000165 | 0.180597 ± 0.005457 | 1.506671 ± 0.038862 | 0.328618 ± 0.007135 |
| 3 h | Temporal | 0.680004 ± 0.014513 | 0.012639 ± 0.000478 | 0.131344 ± 0.003472 | 1.276286 ± 0.080706 | 0.293435 ± 0.014854 |
| 6 h | Static | 0.686763 ± 0.004962 | 0.028594 ± 0.000336 | 0.174550 ± 0.006209 | 1.399416 ± 0.051793 | 0.601741 ± 0.017410 |
| 6 h | Temporal | 0.686375 ± 0.013809 | 0.026433 ± 0.001021 | 0.142186 ± 0.005156 | 1.256563 ± 0.105401 | 0.568009 ± 0.020328 |

These are retrospective benchmark results, not clinical operating characteristics. PPV is very low in the fixed-threshold experiment (approximately 0.25%–2.24% across the rows in the source report). Alerts outside a Challenge-positive future window are not adjudicated clinical false alarms.

The patient-relative physiology candidate improved AUROC over the temporal baseline at evaluated horizons but worsened Brier score at every horizon. The reported Platt experiment sharply reduced Brier score but yielded essentially zero sensitivity at the fixed 0.5 reference threshold. These findings caution against selecting a model using one metric.

No clinically justified alert threshold has been established. Illustrative utility-cost ratios are assumptions, not clinician-elicited or validated costs. Set B must not be reused to select a threshold or policy.

## 7. Priority reviewer questions

1. Is the Challenge-label endpoint accurately described, without biological-onset overclaim?
2. Are horizon construction, current-positive exclusions, patient boundaries and time ordering correct?
3. Are splits patient-disjoint and are imputation/scaling/missingness features fitted only on permitted training partitions?
4. Is Set B fully isolated from development choices?
5. Are estimands and uncertainty appropriate for repeated hourly rows and patient clustering?
6. Are AUROC/AUPRC interpreted separately from Brier, log loss, calibration slope/intercept and prevalence references?
7. Are calibration diagnostics and uncertainty intervals defensible and clearly qualified?
8. Are threshold, refractory-alert and future-window coverage definitions correctly implemented?
9. Does CPU/BLAS evidence support the reproducibility conclusion? What portability/provenance work remains?
10. Are adaptive-twin heuristic outputs and supervised forecasts clearly separated in the product narrative?
11. Are dataset terms, privacy, artifact handling and repository history adequate?
12. Which claims are justified for a research-software release or manuscript now?

## 8. Review procedure

1. Record the exact commit SHA and date inspected.
2. Inspect source, protocol, evaluator, feature/cache construction, workflow, model card and aggregate reports.
3. Record workflow run and artifact IDs actually inspected.
4. Mark each item **PASS**, **CONCERN** or **NOT ASSESSED**, citing file/line or artifact evidence.
5. Classify findings as blocking, major or minor and propose concrete corrections.
6. Disclose expertise, prior Challenge involvement and conflicts of interest.
7. Do not request or publish patient-level predictions, identifiers, raw records or private caches.
8. Do not tune or modify anything using Set B.
9. Distinguish computational reproducibility from statistical validity and clinical validity.

If a workflow artifact has expired, mark it unavailable/NOT ASSESSED. Do not infer that it was inspected.

## 9. Reviewer decision form

**Reviewer details**
- Name (optional for public record):
- Role and relevant expertise:
- Institution/affiliation (optional):
- Review date:
- Exact repository commit SHA:
- Workflow run(s) and artifact(s) inspected:
- Prior involvement with PhysioNet/CinC Challenge 2019:
- Conflicts of interest, funding or relationships:

**Assessment — PASS / CONCERN / NOT ASSESSED with evidence**
1. Endpoint and temporal alignment:
2. Patient-level split integrity and leakage:
3. Set B isolation:
4. Feature construction, missingness and preprocessing:
5. Calibration and probability quality:
6. Uncertainty and patient clustering:
7. Threshold, alert burden and event-window metrics:
8. CPU/BLAS reproducibility and provenance:
9. Privacy, governance and dataset terms:
10. Claims, limitations and intended use:

**Findings**
- Blocking issues:
- Major issues:
- Minor issues:
- Evidence unavailable:
- Required analyses/corrections:
- Recommended manuscript/release changes:

**Overall disposition**
- [ ] REVISION REQUIRED
- [ ] NOT READY
- [ ] RESEARCH-CODE RELEASE CANDIDATE WITH LIMITATIONS
- [ ] UNABLE TO ASSESS

This review is not ethics approval, regulatory clearance, medical-device approval, clinical validation or permission to use VITALIS for patient care.

## 10. Copy-ready invitation

**Subject:** Request for independent statistical and clinical-methods review — VITALIS research prototype

Dear [Title and surname],

I am seeking an independent, critical methods review of VITALIS, a research-only project exploring adaptive physiological modelling and retrospective forecasting against the PhysioNet/CinC Challenge 2019 sepsis labels.

I am not seeking endorsement. I would particularly value scrutiny of the endpoint definition, patient-level splits and leakage controls, Set B isolation, calibration and probability quality, alert burden, and reproducibility evidence. The project has documented repeated strict baseline-reconciliation passes under the reference OpenBLAS kernel, alongside earlier CPU-dispatch-sensitive failures. A fresh full-cohort run on the exact current repository snapshot remains outstanding.

I have prepared a bounded reviewer package with the methods summary, evidence links, limitations and a structured decision form:
https://github.com/culprit-k/VITALIS/blob/main/docs/INDEPENDENT_SCIENTIFIC_REVIEW_PACKAGE_2026-11-19.md

Would you be willing to review the package, or recommend a suitably qualified statistician, clinical informatician, intensivist or sepsis-prediction researcher? A conclusion of revision required or not ready is entirely acceptable. Please let me know your availability, relevant expertise and any conflicts of interest.

I will not publish your name, affiliation, comments or review letter without your explicit permission. I will not share patient-level data or confidential material.

Thank you for considering this request.

Kind regards,  
[Your name]  
VITALIS project

## 11. Related materials

- [Project status](PROJECT_STATUS.md)
- [Research and engineering brief](RESEARCH_AND_ENGINEERING_BRIEF.md)
- [Model card](MODEL_CARD.md)
- [Independent methods review checklist](INDEPENDENT_METHODS_REVIEW_CHECKLIST_2026-10-16.md)
- [Independent evaluation protocol](INDEPENDENT_EVALUATION_PROTOCOL.md)
- [Frozen reconciliation acceptance rule](HORIZON_RECONCILIATION_ACCEPTANCE_RULE.md)
- [CPU-dispatch investigation](REPRODUCTION_FAILURE_TRIAGE_2026-10-15.md)
- [Historical reproducibility review package](VITALIS_REPRODUCIBILITY_INDEPENDENT_REVIEW_PACKAGE_2026-10-15.md)
- [Tracking issue #4](https://github.com/culprit-k/VITALIS/issues/4)

## 12. Safety and evidence boundaries

- VITALIS is a research prototype, not a clinically validated medical device or clinical decision-support system.
- No output may guide diagnosis, triage, monitoring, treatment or patient-care decisions.
- Hardware work is bench-only with synthetic signals, simulators or appropriate non-human test equipment. Do not connect people to DIY or unverified hardware.
- Do not publish raw patient data, patient-level records, identifiers, predictions, caches, credentials or confidential institutional material.
- Confirm dataset terms, institutional governance and ethics determinations before new data collection or access.
- Public repository visibility does not grant blanket reuse rights; no top-level repository licence is present as of this package date.
- Independent review is a prerequisite for the next research decision, not a substitute for external validation, prospective evaluation or governance approval.
