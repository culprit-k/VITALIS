# VITALIS external validation and governance execution plan

**Status:** protocol scaffold; no external cohort has been accessed or evaluated under this plan, and no ethics or institutional approval is claimed.  
**Scope:** retrospective research validation planning only. Not authorization for clinical use.

## 1. Why this gate is separate

The PhysioNet/CinC Challenge 2019 Set A and Set B results establish a reproducible benchmark experiment, not independent external clinical validity. Set B is another Challenge training cohort and must remain evaluation-only under the frozen existing protocol. The endpoint is entry into the Challenge `SepsisLabel`-positive window, not independently adjudicated biological sepsis onset.

A genuinely external cohort must have a distinct provenance and cohort governance path, with an endpoint that is clearly defined and clinically reviewed. Do not describe the current results as external validation.

## 2. Before data access

- [ ] Identify the intended external institution/cohort and accountable data custodian.
- [ ] Confirm data-use terms, permitted research purpose, access approvals, retention/deletion rules, and publication restrictions.
- [ ] Obtain institutional research/ethics determination or approval as required by the relevant jurisdiction and institution; document whether consent, waiver, or other legal basis applies.
- [ ] Complete privacy impact/data protection review, data minimization, access controls, encryption, audit logging, and incident-response plan.
- [ ] Define whether the cohort is retrospective or prospective, inclusion/exclusion criteria, study dates, care setting, sampling frequency, and patient-level unit of analysis.
- [ ] Define a data dictionary and harmonization plan for units, timestamps, missingness, device provenance, measurement quality, treatment/context variables, and label availability.
- [ ] Have a qualified clinical/research supervisor review endpoint definition and study protocol before inspecting outcome-linked performance.
- [ ] Pre-register or version-lock the protocol and analysis plan before evaluation.

No raw patient data, row-level predictions, identifiers, or feature caches may be committed to Git or retained in ordinary CI artifacts.

## 3. Freeze before evaluation

Record immutable hashes for:
- repository commit and evaluator source;
- model and feature configuration;
- preprocessing and missing-data policy;
- calibration method, if any;
- forecast horizon and endpoint definition;
- any operating threshold and alert-episode/refractory definition;
- metric list, uncertainty method, subgroup plan, and exclusion rules.

The threshold and calibration configuration must be selected using development data independent of the external test cohort. If a clinically/research-supervisor-approved alert-budget/utility objective is unavailable, report threshold trade-offs without naming a preferred operating point. Never tune a model, threshold, calibration map, alert budget, feature, or stopping rule after looking at external test results.

## 4. Minimum analysis plan

Report, with patient-cluster uncertainty intervals where appropriate:
- cohort flow and exclusions;
- endpoint prevalence and label/temporal alignment;
- AUROC and AUPRC alongside a constant-prevalence reference;
- Brier score and log loss;
- calibration intercept/slope and reliability summaries, including uncertainty and non-identifiable fits;
- sensitivity, specificity, PPV, NPV at the pre-frozen operating point;
- alert episodes per at-risk patient-day and the exact episode/refractory definition;
- lead-time/coverage summaries only where the endpoint supports them;
- performance by site/device/time period and predeclared clinically relevant subgroups when sample size and governance permit;
- missingness, measurement-frequency, sensor/source-change, and data-quality sensitivity analyses;
- all prespecified models/configurations, including failed or degenerate fits;
- limitations from case mix, prevalence shift, treatment patterns, coding, label uncertainty, and transportability.

Do not interpret alerts outside the dataset's positive label window as verified clinical false alarms without an adjudicated reference. Do not equate Challenge labels with independent clinical onset adjudication.

## 5. Security and privacy controls

- Keep the cohort in an institution-approved, access-controlled environment.
- Use least-privilege accounts and record access.
- Avoid exporting identifiers, timestamps that can re-identify, free text, row-level scores, and small cells.
- Retain only reviewed aggregate tables and non-identifying provenance records in the repository.
- Scan outputs for accidental row-level data before upload; retain an audit log of data transfers.
- Define retention/deletion and incident reporting before analysis.
- Review dependency/supply-chain security and access to any external compute environment.

## 6. Review and release decision

Required sign-offs before claiming external validation:
- [ ] Data custodian confirms permitted use and provenance.
- [ ] Institutional ethics/research governance determination documented.
- [ ] Privacy/security review completed.
- [ ] Independent statistician/methods reviewer signs the analysis review.
- [ ] Qualified clinical reviewer signs the endpoint/interpretation review.
- [ ] Frozen evaluation run reproduces from the named commit in a clean environment.
- [ ] Aggregate-only artifact and provenance hashes are verified.
- [ ] Results and limitations are approved for the intended publication/research release.
- [ ] Any prospective shadow-mode work has a separate protocol, oversight, monitoring, incident response, and stop rules.

This plan does not itself satisfy any approval, access, or validation requirement. Until the gate's evidence exists, Gate 4 remains open and VITALIS remains research-only—not for diagnosis, triage, or treatment decisions.
