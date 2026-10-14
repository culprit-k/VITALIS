# VITALIS clinical translation, validation, and regulatory roadmap

**Document status:** initial planning baseline; not evidence of compliance, clinical validation, or regulatory authorization.  
**As of:** 15 October 2026  
**Repository:** \`culprit-k/VITALIS\`  
**Current maturity:** retrospective research prototype; no clinical-use authorization.

## Executive decision

VITALIS must not be used to diagnose, triage, monitor, or treat real patients at this stage. Its current evidence is retrospective analysis of the PhysioNet/CinC Challenge 2019 benchmark, where the hourly \`SepsisLabel\` includes a six-hour lead convention. The target is entry into a benchmark-positive label window, not independently adjudicated biological sepsis onset. Set B is already inspected and therefore must not be repurposed as an untouched test set for any threshold or model choices.

Clinical translation is a programme of work across intended use, quality management, risk management, software engineering, analytical/clinical evaluation, cybersecurity, human factors, regulatory authorization, and post-market monitoring. Repository changes alone cannot establish clinical validity or authorize a medical device.

## 1. Intended use and claims gate — BLOCKING

Before finalizing model requirements or regulatory classification, the product owner and qualified clinical/regulatory advisors must approve a version-controlled intended-use statement covering:

- Intended purpose and precise clinical claim (for example, whether it provides an early-warning risk score for clinician review).
- Intended patient population, age range, care setting, care pathway, exclusions, and contraindications.
- Intended users and required training.
- Inputs, source systems, units, sampling frequency, acceptable missingness, freshness, and data-quality requirements.
- Output, forecast horizon, alert semantics, expected response, and whether the output is advisory or drives an intervention.
- Foreseeable misuse, out-of-scope use, and the action required when inputs are unavailable or unreliable.
- Deployment geography and manufacturer/legal entity.

Do not infer a regulatory class from the algorithm alone. Intended purpose, claims, risk, and jurisdiction determine the pathway. Until this statement is approved, all classification and study plans are provisional.

## 2. Target-market regulatory assessment — BLOCKING

Choose the first target market before making jurisdiction-specific compliance claims. Obtain written advice from a qualified regulatory professional and, where available, early feedback from the relevant authority.

### India (if selected)

The Central Drugs Standard Control Organization (CDSCO) states that medical devices, including qualifying software, are regulated under the Drugs and Cosmetics Act, 1940 and Medical Devices Rules, 2017. CDSCO published a Medical Device Software guidance document in July 2026. Review the current guidance and applicable software risk-classification list, then confirm classification, licensing, clinical-investigation requirements, quality-system obligations, and post-market duties with a qualified Indian regulatory professional.

Official starting points:
- CDSCO Medical Devices Rules: https://cdsco.gov.in/opencms/opencms/en/Acts-and-rules/Medical-Devices-Rules
- CDSCO Medical Device & Diagnostics portal and current software guidance: https://cdsco.gov.in/opencms/opencms/en/Medical-Device-Diagnostics/Medical-Device-Diagnostics/

### United States (if selected)

Assess the current FDA device-software policies and the January 2026 final Clinical Decision Support Software guidance. Do not assume a sepsis prediction model is excluded as non-device CDS. A patient-specific forecast that informs time-sensitive clinical action may fall within device oversight; the determination must be made against the actual intended use and software function.

Official starting points:
- FDA Clinical Decision Support Software guidance (January 2026): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
- FDA Software Functions and Mobile Medical Applications policy: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/policy-device-software-functions-and-mobile-medical-applications

### European Union (if selected)

Assess qualification and classification under the EU Medical Device Regulation and the current MDCG 2019-11 revision (June 2025). Confirm the applicable conformity-assessment route, clinical-evaluation expectations, quality system, and notified-body involvement where required.

Official starting point:
- European Commission / MDCG software qualification and classification guidance: https://health.ec.europa.eu/system/files/2025-06/mdcg_2019_11_en.pdf

### International clinical-evaluation framework

Use the IMDRF SaMD clinical-evaluation framework as a planning reference for valid clinical association, analytical validation, and clinical validation. It is not a substitute for the chosen jurisdiction's binding requirements.

- IMDRF SaMD Clinical Evaluation (N41): https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation

## 3. Quality management and design controls

Establish a documented quality-management system appropriate to the selected jurisdiction and device lifecycle. Have a quality/regulatory lead determine which standards and editions apply; the following are planning references, not a declaration of conformity:

- ISO 13485 — medical-device quality management.
- ISO 14971 — medical-device risk management.
- IEC 62304 — medical-device software lifecycle processes.
- IEC 62366-1 — usability engineering for medical devices.
- Applicable cybersecurity, privacy, interoperability, clinical-investigation, and AI-specific requirements in the target market.

Minimum controlled records to create and maintain:

1. Quality plan, roles, approvals, training, supplier controls, document control, CAPA, and change control.
2. User needs, intended use, system/software requirements, architecture, detailed design, and design reviews.
3. Requirements-to-test traceability matrix linking each safety and performance requirement to verification evidence.
4. Software configuration/version history, dependency inventory/SBOM, reproducible build instructions, release records, and rollback plan.
5. Verification/validation plans, protocols, test reports, defect logs, and release acceptance criteria.
6. Risk-management plan, hazard analysis, risk controls, residual-risk assessment, and benefit-risk review.
7. Cybersecurity threat model, secure-development controls, vulnerability response, access control, encryption, audit logging, backup/recovery, and incident handling.
8. Data-management plan covering lawful basis/permissions, data provenance, de-identification, access, retention, transfer, and deletion.
9. Clinical evaluation plan/report, clinical-investigation documentation, site agreements, ethics approvals, informed consent where required, and monitoring plans.
10. Labeling, instructions for use, training materials, limitations, warnings, and post-market surveillance/vigilance procedures.

A document template or passing software test is not proof that the corresponding quality or regulatory requirement has been met.

## 4. Model and data evidence gate

### Required before a pivotal clinical study

- Reproduce all key results from a clean checkout and newly built caches; record commit, source hashes, dependency lockfile, environment, seeds, data version, and clean Git status.
- Resolve the documented differences between historical reconstructed harness results and exact-source outputs. Preserve both historical records and explain the root cause only when supported by evidence.
- Conduct a history-wide privacy/secret/artifact audit. Confirm all dataset licenses, access terms, permissions, and data-processing agreements.
- Freeze the intended-use population, reference standard, prediction time, horizons, eligible observations, exclusions, and primary/secondary endpoints.
- Define missingness, out-of-range values, unit conversion, timestamp ordering, stale values, device failure, and out-of-distribution handling.
- Predefine feature selection, training/calibration/test separation, model architecture, hyperparameters, threshold/alert policy, refractory period, and statistical analysis before the final evaluation.
- Report discrimination, precision-recall performance, calibration, sensitivity, PPV, specificity, false alerts per patient-day, missed events, lead-time distribution, subgroup performance, and uncertainty at the patient level.
- Compare against clinically relevant baseline practice and existing validated scores where appropriate; document why the comparator and endpoints matter clinically.
- Assess dataset shift and performance across hospitals, wards, age/sex groups where lawful and scientifically appropriate, comorbidity, measurement frequency, missingness, and relevant device/vendor differences.
- Quantify the consequences of false negatives, false positives, alert fatigue, and delayed or unnecessary responses. Obtain cost/utility assumptions from qualified clinical stakeholders, not arbitrary developer-selected weights.
- Validate the full end-to-end system, not just the classifier: data ingestion, timestamps, units, score generation, alert routing, downtime, human factors, audit trail, and safe failure behavior.

### Existing benchmark limitation

Set A and Set B belong to the same public challenge ecosystem. Set B has already been used for retrospective model comparisons and must not be reused for threshold selection or described as an untouched final test set. A genuinely new independent cohort with independently defined/adjudicated event timing is required for a stronger external clinical evaluation. The challenge label alone cannot establish clinical-onset prediction.

## 5. Clinical evidence programme

The clinical lead, statistician, ethics committee/IRB, study sponsor, and regulator should approve the actual study designs and sample-size rationale. The stages below are a planning sequence, not authorization to enroll patients.

### Stage A — retrospective external validation

- Use a genuinely independent hospital/cohort and a prespecified protocol.
- Define an independent clinical reference standard and adjudication process for event onset and competing events.
- Freeze the model, feature schema, calibration, thresholds, alert suppression, endpoints, and analysis plan before access to the evaluation outcomes.
- Use patient-level separation and account for site-level clustering and missing data.
- Report confidence intervals, subgroup results, calibration, alert burden, lead time, and failures; document deviations transparently.
- Do not tune on the external test cohort. If changes are required, treat the next dataset as a new evaluation cohort.

### Stage B — prospective silent-mode evaluation

After required governance approvals, run the frozen system in the intended workflow without showing alerts to treating staff or affecting care. Evaluate input availability, technical reliability, calibration drift, false-alert burden, lead-time validity, subgroup performance, and workflow feasibility against prospectively collected and adjudicated outcomes.

### Stage C — interventional clinical evaluation

Only after evidence and approvals justify it, design an appropriately powered study comparing the intended use with standard care. Predefine clinical outcomes, safety endpoints, escalation rules, monitoring, stopping criteria, adverse-event handling, and analysis. An ethics committee/IRB and applicable regulator must determine what authorization is required before enrollment.

### Stage D — post-market clinical follow-up

Plan ongoing real-world monitoring, complaint/adverse-event reporting, performance drift detection, periodic clinical review, cybersecurity updates, controlled model changes, and corrective actions. A model update must not silently alter the validated intended purpose or performance claims.

## 6. Risk management and safety controls

Start a hazard analysis with at least these scenarios:

- False negative or late warning.
- Excessive false alerts, alarm fatigue, or workflow overload.
- Missing, stale, delayed, misaligned, or corrupted measurements.
- Incorrect units, sensor replacement, device/vendor changes, or implausible values.
- Performance deterioration in underrepresented subgroups or new hospitals.
- Model drift, calibration drift, distribution shift, or dependency/software update.
- Interface/API outage, duplicate alerts, lost alerts, wrong-patient association, or timestamp errors.
- Unauthorized access, ransomware, data leakage, malicious modification, and supply-chain vulnerability.
- Automation bias, misunderstood uncertainty, inappropriate reliance, or use outside the intended population.
- Unsafe fallback when VITALIS is unavailable or a score cannot be calculated.

For each hazard, record cause, foreseeable sequence, severity, probability rationale, risk control, verification evidence, residual risk, owner, and approval. Controls should include fail-safe behavior, input-quality checks, explicit uncertainty/unavailable states, clear labeling, monitoring, human-factors testing, and a clinically reviewed response protocol. Do not invent numeric acceptance limits without clinical and risk-management justification.

## 7. AI/model lifecycle and change control

- Version and hash the training data manifest, feature schema, preprocessing, model artifact, calibration parameters, threshold policy, source code, dependencies, and inference environment.
- Keep patient-level data and predictions in access-controlled approved storage; publish only authorized aggregate results.
- Record model cards, dataset statements, known limitations, intended population, subgroup evidence, calibration, and failure modes.
- Define monitoring triggers and who can pause or roll back the system.
- Treat retraining, recalibration, feature changes, threshold changes, new sensors, and changes in intended use as controlled changes with documented impact assessment and required re-verification/re-validation.
- Determine whether a predetermined change-control plan or other AI-specific regulatory mechanism is applicable in the target jurisdiction; do not assume it is available or approved.
- Maintain an audit trail for every release and a reproducible, tested rollback path.

## 8. Governance and ownership gates

Named, qualified owners must be assigned before proceeding:

- Clinical lead with relevant acute-care/sepsis expertise.
- Independent biostatistician/clinical epidemiologist.
- Regulatory affairs professional in the target jurisdiction.
- Quality-management/design-control lead.
- Software safety and cybersecurity lead.
- Data-protection/privacy and data-governance lead.
- Study sponsor/site investigators and ethics/IRB contacts.
- Human-factors/usability specialist.
- Independent reviewer for final protocol, results, and release evidence.

An individual developer or AI assistant cannot substitute for these accountable professionals or sign their approvals.

## 9. Current gate register

| Gate | Current status | Evidence needed to close |
|---|---|---|
| Intended use and target market | BLOCKED | Approved intended-use statement and first jurisdiction |
| Regulatory classification/pathway | OPEN | Written qualified assessment for the chosen market |
| QMS and design controls | NOT ESTABLISHED | Approved QMS plan, controlled records, audits |
| Risk management and usability | INCOMPLETE | Hazard file, mitigations, verification, user studies |
| Clean-source reproducibility | OPEN | Clean checkout, fresh caches, exact source/environment hashes, reconciliation |
| Benchmark evaluation | PARTIAL | Reproducible analyses; benchmark limits acknowledged |
| Independent clinical reference standard | MISSING | Clinical protocol and adjudicated event timing |
| External validation | MISSING | New independent cohort and frozen protocol |
| Prospective silent-mode evaluation | NOT STARTED | Governance approvals, site, prospective protocol |
| Interventional clinical evidence | NOT STARTED | Approved study, power rationale, safety oversight |
| Regulatory submission/authorization | NOT STARTED | Jurisdiction-specific submission and required authorization |
| Post-market surveillance | NOT ESTABLISHED | Approved surveillance/vigilance and update procedures |

## 10. Immediate ordered actions

1. **Product decision:** approve the first intended use, patient population, workflow, output/claim, and first target jurisdiction.
2. **Appoint accountable experts:** clinical lead, independent statistician, regulatory/quality lead, and data-governance/ethics support.
3. **Freeze the research baseline:** complete clean-checkout/fresh-cache reproduction and resolve source/result discrepancies before using results in a regulatory dossier.
4. **Approve clinical evaluation protocol:** independent event definition, comparator, endpoints, sample-size rationale, subgroup plan, and analysis plan.
5. **Build controlled QMS and risk file:** requirements, traceability, hazard controls, cybersecurity, usability, data governance, and change control.
6. **Secure a new independent cohort and approvals:** no patient recruitment or prospective use until the responsible institutions and authorities confirm the required approvals.
7. **Run external then prospective studies:** preserve the frozen model and policy; do not reuse the already-inspected Set B for selection.
8. **Prepare the regulatory dossier and seek authorization:** only after the relevant evidence, quality, and governance requirements are met.

## Sources for initial regulatory planning

- CDSCO, Medical Devices Rules and current software guidance: https://cdsco.gov.in/opencms/opencms/en/Acts-and-rules/Medical-Devices-Rules and https://cdsco.gov.in/opencms/opencms/en/Medical-Device-Diagnostics/Medical-Device-Diagnostics/
- FDA, Clinical Decision Support Software guidance (January 2026): https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software
- FDA, Policy for Device Software Functions and Mobile Medical Applications: https://www.fda.gov/regulatory-information/search-fda-guidance-documents/policy-device-software-functions-and-mobile-medical-applications
- European Commission / MDCG, software qualification and classification guidance, revision 1 (June 2025): https://health.ec.europa.eu/system/files/2025-06/mdcg_2019_11_en.pdf
- IMDRF, Software as a Medical Device: Clinical Evaluation (N41): https://www.imdrf.org/documents/software-medical-device-samd-clinical-evaluation

**Final boundary:** This roadmap is a planning document, not legal advice, a regulatory classification, proof of standards conformity, ethics approval, or clinical validation. VITALIS must remain research-only until all applicable requirements have been independently assessed and satisfied.
