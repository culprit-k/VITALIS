# VITALIS independent scientific review invitation pack

**Updated:** 18 October 2026  
**Purpose:** help the project owner invite an unaffiliated reviewer and make the review bounded, reproducible, and candid. This is not a reviewer sign-off and does not imply that a reviewer has agreed to participate.

## Who to invite

Invite one or more people who have not authored the VITALIS analysis and have no material conflict that would undermine independence. Suitable backgrounds include:

- clinical informatics / critical-care prediction;
- biostatistics or machine-learning evaluation for rare outcomes;
- sepsis prediction methods and temporal-label design;
- reproducible research and dataset leakage audits.

A reviewer who has relevant experience with the PhysioNet Challenge can assess endpoint semantics, but should disclose any prior involvement with the source dataset or Challenge. Ask permission before publishing a reviewer’s name, employer, affiliation, comments, or review letter. Do not upload confidential data or private correspondence to the public repository without permission.

## Copy-ready invitation

**Subject:** Request for independent methods review of VITALIS sepsis-prediction research prototype

Hello,

I am seeking an independent methods review of VITALIS, a research-only software prototype that evaluates retrospective forecasting against the PhysioNet/CinC Challenge 2019 sepsis labels. I am looking for critical feedback, not endorsement.

The full-cohort reproduction passed on source commit `14440230ff19bd1ade378374c47158cda321f628`, including its frozen six-decimal baseline reconciliation: 42/42 mean/sample-SD pairs and 84/84 scalar values matched, with zero mismatches. The current repository tip is `f13bb5edd448d8ba160538257523187b335cc3dc`; the commits after the reproduced source are documentation-only, and standard CI passed on the current tip. The aggregate-only artifact and provenance are linked below.

Would you be willing to review the protocol, code, and aggregate results, or recommend an appropriate reviewer? A useful review can be bounded to the checklist below and can conclude with blocking concerns or “not ready”; a positive conclusion is not expected or presumed.

The most important questions are whether the temporal target and patient splits are defensible, whether calibration and threshold selection are properly isolated to Set A, how to interpret the very low PPV and static-versus-temporal comparisons, and what claims are justified. Set B is a Challenge benchmark cohort, not an external clinical validation cohort. No operating threshold has been selected because a supervisor-approved alert-budget/utility objective is not yet available.

I can provide the public repository and review checklist. Please let me know whether you have capacity and whether any conflicts of interest should be disclosed. I will not publish your identity or comments without your permission.

Thank you.

## Review evidence links

- Repository: https://github.com/culprit-k/VITALIS
- Strict full-cohort reproduction on source commit `14440230ff19bd1ade378374c47158cda321f628`: https://github.com/culprit-k/VITALIS/actions/runs/39057821508
- Aggregate/provenance artifact for that run: https://github.com/culprit-k/VITALIS/actions/runs/39057821508/artifacts/12111943281
- Artifact ZIP SHA-256: `565f0ccecb900c6d41566de8e0dfbc61e79793874079c9bd124b8c4a8f05980e`
- Standard CI on the reproduced source commit: https://github.com/culprit-k/VITALIS/actions/runs/39057821517
- Standard CI on current main `f13bb5edd448d8ba160538257523187b335cc3dc`: https://github.com/culprit-k/VITALIS/actions/runs/39063755743
- Independent methods review checklist: `docs/INDEPENDENT_METHODS_REVIEW_CHECKLIST_2026-10-16.md`
- Reproducibility review package: `docs/VITALIS_REPRODUCIBILITY_INDEPENDENT_REVIEW_PACKAGE_2026-10-15.md`
- Tracking issue: https://github.com/culprit-k/VITALIS/issues/4

The artifact is aggregate/provenance-only and has a limited GitHub retention period; reviewers should retrieve it from the workflow link while it is available. The current main tip has not had a new full-cohort run after the documentation-only commits; do not describe the run above as if it executed on `f13bb5e`.

## Reviewer response template

Please mark each item **PASS**, **CONCERN**, or **NOT ASSESSED** and cite the evidence inspected.

1. Target definition and time alignment:  
2. Patient-level split integrity and leakage:  
3. Set B isolation and interpretation:  
4. Calibration, uncertainty, prevalence and cohort shift:  
5. Alert burden, sensitivity, PPV and static-vs-temporal comparison:  
6. Reconciliation/provenance and reproducibility:  
7. Privacy and artifact handling:  
8. Claims and limitations:  
9. Blocking issues / required changes:  
10. Overall disposition: **PASS WITH LIMITATIONS / REVISION REQUIRED / NOT READY / UNABLE TO ASSESS**

Please state relevant expertise, any conflicts, the exact commit/artifact reviewed, and review date. Do not provide patient-care recommendations or treat this retrospective benchmark as clinical validation.

## Non-negotiable interpretation limits

- The target is entry into the Challenge `SepsisLabel` positive window, not independently adjudicated biological sepsis onset.
- Set B remains evaluation-only and is not a genuinely external cohort.
- No diagnosis, triage, treatment, clinical utility, medical-device readiness, or prospective performance claim is supported.
- Do not change the evaluator, historical baseline, six-decimal reconciliation rule, or threshold based on Set B.
- Independent review must be performed by someone who did not produce the analysis; project-author self-review is not a substitute.
