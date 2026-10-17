# VITALIS independent scientific review invitation pack

**Prepared:** 17 October 2026  
**Purpose:** help the project owner invite an unaffiliated reviewer and make the review bounded, reproducible, and candid. This is not a reviewer sign-off and does not imply that a reviewer has agreed to participate.

## Who to invite

Invite one or more people who have not authored the VITALIS analysis and have no material conflict that would undermine independence. Suitable backgrounds include:

- clinical informatics / critical-care prediction;
- biostatistics or machine-learning evaluation for rare outcomes;
- sepsis prediction methods and temporal-label design;
- reproducible research and dataset leakage audits.

Ask permission before publishing a reviewer’s name, employer, affiliation, comments, or review letter. Do not upload confidential data or private correspondence to the public repository without permission.

## Copy-ready invitation

**Subject:** Request for independent methods review of VITALIS sepsis-prediction research prototype

Hello,

I am seeking an independent methods review of VITALIS, a research-only software prototype that evaluates retrospective forecasting against the PhysioNet/CinC Challenge 2019 sepsis labels. I am looking for critical feedback, not endorsement.

The current reproducibility checkpoint is on commit `eefad3664019a690c4520986875e05a9c9fe0b6f`. The clean-checkout full-cohort workflow passed, including its frozen six-decimal baseline reconciliation (42/42 mean/sample-SD pairs and 84/84 scalar values matched; zero mismatches). The aggregate-only artifact and provenance are linked below.

Would you be willing to review the protocol, code, and aggregate results, or recommend an appropriate reviewer? A useful review can be bounded to the checklist below and can conclude with blocking concerns or “not ready”; a positive conclusion is not expected or presumed.

The most important questions are whether the temporal target and patient splits are defensible, whether calibration and threshold selection are properly isolated to Set A, how to interpret the very low PPV and static-versus-temporal comparisons, and what claims are justified. Set B is a Challenge benchmark cohort, not an external clinical validation cohort.

I can provide the public repository and review checklist. Please let me know whether you have capacity and whether any conflicts of interest should be disclosed. I will not publish your identity or comments without your permission.

Thank you.

## Review evidence links

- Repository: https://github.com/culprit-k/VITALIS
- Latest post-merge strict full-cohort reproduction: https://github.com/culprit-k/VITALIS/actions/runs/39041430942
- Latest aggregate/provenance artifact: https://github.com/culprit-k/VITALIS/actions/runs/39041430942/artifacts/12105668062
- Standard CI on the same source commit: https://github.com/culprit-k/VITALIS/actions/runs/39041430943
- Independent methods review checklist: `docs/INDEPENDENT_METHODS_REVIEW_CHECKLIST_2026-10-16.md`
- Reproducibility review package: `docs/VITALIS_REPRODUCIBILITY_INDEPENDENT_REVIEW_PACKAGE_2026-10-15.md`
- Tracking issue: https://github.com/culprit-k/VITALIS/issues/4

The artifact is aggregate/provenance-only. Its ZIP SHA-256 is `df475890f4671b215a1b3fa25e0affa34cd7b078f23c110b20104c974379f245`. It expires 16 November 2026 at 15:51:36 UTC, so reviewers should retrieve it before expiration if they need the exact retained file.

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
