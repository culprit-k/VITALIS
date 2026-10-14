# Uzbekistan research-readiness dossier for VITALIS

**Version:** 0.1  
**Review date:** 15 October 2026  
**Market:** Republic of Uzbekistan  
**Initial deployment category:** research only  
**Current decision:** **NOT CLEARED FOR HUMAN-SUBJECT OR CLINICAL-WORKFLOW USE**

This is a preliminary regulatory and governance planning artifact, not legal advice, an official classification, ethics approval, permission to process health data, medical-device registration, or clinical validation. The legal texts and authority procedures must be checked again by qualified Uzbekistan counsel and the responsible institutions before each study.

## 1. Proposed first-stage boundary

For the first Uzbekistan-based activity, define VITALIS as an **offline retrospective research prototype** that analyzes already-authorized, de-identified datasets in a controlled research environment.

Permitted within this proposed boundary, subject to data-access terms and institutional approval:
- Synthetic-data engineering and software tests.
- Reproducible retrospective analysis of datasets for which the team has documented lawful access and permission for the intended analysis.
- Aggregate-only reporting, with small-cell suppression and no public patient-level outputs.
- Research outputs that are not displayed to treating clinicians and are not used to make, prioritize, delay, or change patient-care decisions.

Out of scope until separately reviewed and approved:
- Prospective collection of patient data, recruitment, or intervention.
- Live hospital feeds, shadow-mode monitoring of real patients, or display of individual risk scores to clinical staff.
- Diagnosis, triage, treatment recommendation, escalation, discharge, or clinical alarm use.
- Claims of sepsis-onset prediction: the current benchmark target forecasts entry into the Challenge SepsisLabel-positive window, whose label construction includes a six-hour lead convention.
- Any claim that VITALIS is registered, certified, regulator-approved, clinically validated, or safe for care.

“Research only” is not a blanket exemption from data-protection, research-ethics, institutional, or medical-device requirements. The applicable pathway depends on the actual activity and intended purpose.

## 2. Current Uzbekistan-specific regulatory findings

### 2.1 Personal data and health data — blocking gate

The Law of the Republic of Uzbekistan “On Personal Data” (Law No. ZRU-547, 2 July 2019; use the current consolidated text, including amendments) applies to processing of personal data, including by information technology. The current LexUZ English page identifies health-related information as special personal data. The law states that:
- Article 16 defines anonymization as making attribution to a specific person impossible and requires anonymization when personal data are processed for historical, statistical, sociological, or scientific research.
- Article 18 includes processing for statistical or other research purposes subject to mandatory anonymization.
- Article 25 treats health information as special personal data and restricts its processing, with written consent and statutory conditions relevant to the analysis.
- Article 15 regulates cross-border transfers; the team must not assume that uploading data to a foreign cloud, GitHub, or other external service is permitted.
- The applicable registration, security, retention, and data-controller/operator obligations must be assessed for the actual database and processing arrangement.

**Implementation rule for this project:** no identifiable or pseudonymized Uzbek patient-level data may be placed in this public repository, public issue tracker, public cloud workspace, or AI/chat service. A pseudonymized record is not automatically anonymous. Before receiving any local cohort, obtain written institutional authorization and a data-protection determination; keep the linkage key separate and local if a lawful approved design requires one. Prefer data minimization, de-identification before researcher access, access-controlled storage in an institution-approved location, retention/deletion rules, and aggregate-only publication.

### 2.2 Ethics and research governance — blocking gate for human data

A 2024 peer-reviewed analysis of Uzbekistan’s biomedical research ethics system reported that the National Ethics Committee had a central role and identified gaps around institutional review and non-clinical trials. This publication is a secondary description, not binding law, and does not determine the pathway for VITALIS. It does mean the team must **ask the competent national and host-institution authorities in writing** which review body, approvals, consent or waiver, and monitoring apply to:
1. retrospective use of de-identified clinical data;
2. a prospective observational or silent-mode software study;
3. any study in which software output could influence clinical care.

Do not assume that a university supervisor’s permission alone is ethics approval, or that a retrospective study is automatically exempt. No patient recruitment, live-data connection, or prospective silent-mode evaluation should begin until the responsible institution and competent authority have confirmed the requirements in writing.

### 2.3 Medical-software / medical-device status — formal determination required

Cabinet of Ministers Resolution No. 738 of 24 November 2025, effective 26 February 2026, approved updated procedures for state registration of medicinal products and medical equipment. The prior Resolution No. 213 of 23 March 2018 is marked as having lost force from 26 February 2026. The competent medical-technology authority is identified by the official regulator site as the Committee on New Medical Technology within the Center for Pharmaceutical Product Safety under the Ministry of Health.

The official regulator also reported in January 2026 that additional medical-device and medical-software requirements—covering areas such as clinical evaluation, risk management, labeling, unique identification, and cybersecurity—were planned for development during 2026. Therefore, this dossier does **not** infer that the older software document list or another country's SaMD classification can be relied upon as the current Uzbekistan pathway.

**Required written question to the authority:** does the proposed offline retrospective research use fall outside state medical-device registration, and what exact intended-use, distribution, pilot, or clinical-workflow changes would trigger classification, registration, clinical-evaluation, quality-system, labeling, or other obligations? Ask the authority to identify the current binding instruments and the current software-specific requirements, including any implementing acts adopted after the January 2026 announcement.

Official starting points:
- Cabinet of Ministers Resolution No. 738, effective 26 February 2026: https://lex.uz/en/docs/7861699
- Center for Pharmaceutical Product Safety / official site: https://www.uzpharm-control.uz/en/
- Committee on New Medical Technology: https://en.regmed.uz/department_cnmt.php

### 2.4 Cross-border data and hosting

The Personal Data Law contains rules for cross-border transfer. Before any transfer outside Uzbekistan, the data controller and qualified counsel must document the applicable legal basis, recipient-country adequacy/conditions, any consent or other statutory condition, security measures, contracts, and whether separate localization or registry requirements apply to the actual dataset and system. Do not infer a blanket rule from a generic cloud provider's location statement.

**Default project posture:** keep any locally sourced identifiable or pseudonymized clinical data within an institution-approved environment in Uzbekistan until a written legal and institutional assessment authorizes otherwise. Public GitHub should contain code, synthetic fixtures, documentation, and authorized aggregate-only results—not local patient records or row-level predictions.

## 3. Research deployment modes and gates

| Mode | Initial position | Minimum gate before starting |
|---|---|---|
| Synthetic-only development | Allowed within repo controls | Tests, current-tree artifact guard, no real patient data |
| Retrospective analysis of already-authorized, de-identified data | Proposed first study mode; not yet approved | Data-owner permission, lawful-access evidence, written ethics/governance determination, data-management plan, dataset license/access-term review |
| Retrospective data still linkable to a person | Not permitted by this project default | Written legal/data-protection review, applicable consent or statutory basis, approved anonymization workflow and controlled access |
| Prospective observational collection or silent mode | Blocked | Written ethics/authority determination, site and sponsor approvals, protocol, consent/waiver determination, data agreements, risk and monitoring plans |
| Scores shown to clinicians or used in care | Prohibited at current maturity | Formal regulatory pathway and authorization as applicable, adequate clinical evidence, QMS/risk/usability/cybersecurity evidence, approved clinical protocol and governance |
| Commercial distribution, marketing, procurement, or clinical deployment | Not in scope | Jurisdiction-specific legal/regulatory assessment and all required authorizations |

## 4. Uzbekistan readiness register

The machine-readable companion is \`configs/regulatory/uzbekistan_research_readiness.json\`. Statuses are deliberately conservative; “open” or “blocked” means the evidence is not in this repository, not that an authority has rejected the project.

| Gate | Status | Required evidence | Accountable role |
|---|---|---|---|
| Freeze exact research intended-use statement | OPEN | Signed statement specifying retrospective offline research only, inputs, outputs, population, exclusions, and no care influence | Product owner + clinical lead |
| Data access and lawful basis | BLOCKED | Dataset provenance/license, data-owner authorization, approved protocol and data-use agreement | Data custodian + institutional legal/privacy lead |
| Anonymization method | BLOCKED for Uzbek patient data | Documented re-identification risk assessment and validated anonymization procedure before researcher access | Data protection lead + data custodian |
| Ethics/governance route | OPEN | Written determination from host institution and competent Uzbekistan ethics authority on whether review, consent, waiver, or notification is required | PI/sponsor + ethics liaison |
| Cross-border transfer/hosting | BLOCKED for local patient data | Written legal review of storage location, transfer, recipients, contracts, and any database registration/localization requirements | Data controller + legal/privacy lead |
| Medical-software classification | OPEN | Written regulator response on research-only software status and triggers for device classification/registration | Uzbekistan regulatory affairs lead |
| Security and access controls | PARTIAL | Threat model, access list, encryption, audit, retention/deletion, incident response, backup/recovery | Security lead + institution IT |
| Research protocol and statistical plan | PARTIAL | Independent event reference standard, cohort eligibility, endpoints, analysis plan, model/threshold freeze, subgroup and uncertainty plan | PI + independent statistician |
| Clean-checkout reproducibility | OPEN | Fresh checkout/cache, commit/source hashes, environment lock, exact commands, reconciled results | Engineering lead |
| Clinical validation and approval | NOT ESTABLISHED | New independent cohort, adjudicated event timing, external and appropriate prospective evidence, regulatory and ethics approvals | Clinical sponsor + regulator |

No status in this register constitutes an approval.

## 5. Immediate workplan

1. **Confirm the research-only intended-use statement.** Proposed text: “VITALIS is an offline research prototype for retrospective analysis of authorized, de-identified physiological time-series data. It generates research metrics and experimental forecasts for evaluation only. It is not provided to treating clinicians and must not influence diagnosis, triage, treatment, monitoring, escalation, or other patient-care decisions.”
2. **Name the host institution, principal investigator, data controller, and data custodian.** The repository currently has no approved Uzbekistan study site or named accountable legal entity.
3. **Request written determinations before accessing local patient data.** Send the same one-page protocol summary to the host institution's legal/privacy function and ethics liaison, and ask the Center for Pharmaceutical Product Safety / Committee on New Medical Technology for a software-status determination.
4. **Build a study-specific data-management plan.** Specify provenance, data fields, anonymization, access roles, storage country, transfer restrictions, retention, destruction, incident handling, and aggregate release review.
5. **Keep the first study retrospective and offline.** Do not connect live hospital feeds or display patient-level scores.
6. **Close software reproducibility and independent methods review.** Existing Set B has already been inspected and cannot be repurposed for threshold selection; a new independent cohort with independently defined/adjudicated event timing is needed for external clinical evidence.
7. **Reassess the regulatory position on every scope change.** Live feeds, patient-level output, clinical workflow integration, distribution, or marketing require a fresh determination.

## 6. Questions to send to Uzbekistan authorities/institution

### To the host institution / ethics authority
- Which committee or authority must review a retrospective study of de-identified physiological time-series data and a research-only sepsis forecasting algorithm?
- Is a written ethics exemption/determination available, and what documentation is required?
- What consent or waiver rules apply to retrospective records, and what additional approvals apply to prospective silent-mode studies?
- Which institutional approvals, data-use agreements, site permissions, monitoring, and reporting are required?

### To the data-protection/legal function
- Is the proposed de-identification method sufficient to make the dataset anonymous under current Uzbekistan law, given longitudinal physiological sequences and re-identification risk?
- Which database registration, security, retention, and controller/operator requirements apply?
- Are any cross-border transfers permitted for this study, and what conditions and approvals would apply? Until answered, no transfer is assumed permissible.

### To the Center for Pharmaceutical Product Safety / Committee on New Medical Technology
- How is offline software that forecasts future Challenge-label entry, used solely for retrospective research and not for patient care, treated under the currently effective Resolution No. 738 and other current rules?
- Which current binding instrument and criteria govern medical software/SaMD classification as of the response date?
- At what point would prospective silent-mode use, clinical display, decision support, or distribution require registration, clinical evaluation, QMS evidence, labeling, cybersecurity documentation, or other authorization?
- What official pre-submission route and written classification/consultation process are available?

Keep authority responses and signed determinations in the controlled study file. Do not place personal data, confidential correspondence, or legal advice in the public repository without authorization.

## 7. Sources checked for this initial version

1. **Law of the Republic of Uzbekistan No. ZRU-547, “On Personal Data,” current consolidated LexUZ page** (reviewed 15 October 2026; page includes amendments and identifies Articles 15, 16, 18, and 25 as relevant): https://lex.uz/en/acts/4396428
2. **Cabinet of Ministers Resolution No. 738, 24 November 2025**, effective 26 February 2026, on state registration procedures for medicinal products and medical equipment: https://lex.uz/en/docs/7861699
3. **Center for Pharmaceutical Product Safety**, official regulator website: https://www.uzpharm-control.uz/en/
4. **Committee on New Medical Technology**, official regulator page: https://en.regmed.uz/department_cnmt.php
5. **“Ethics Review of Biomedical Research in Uzbekistan: Policy and Program Gaps,”** peer-reviewed article (2024), used as context about governance uncertainty, not as binding law: https://pmc.ncbi.nlm.nih.gov/articles/PMC11464834/
6. Official regulator announcement, 8 January 2026, describing planned 2026 development of additional medical-device/software requirements: https://www.uzpharm-control.uz/en/news/view/2026-01-08-Farmatsevtik-preparatlar

The legal text and implementation status must be rechecked before any real study. This document does not decide whether VITALIS is legally a medical device, does not establish an exemption, and does not replace written advice from qualified Uzbekistan counsel or the competent authorities.
