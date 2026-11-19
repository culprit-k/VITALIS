# VITALIS community review guide

**Purpose:** invite independent clinical, scientific, statistical, software, and engineering scrutiny of the public VITALIS research prototype.

VITALIS is a developing research project, not a validated medical device or clinical decision-support system. A review is not an endorsement, and participation does not imply institutional support.

## Project snapshot

VITALIS explores an adaptive physiological digital twin: a software representation that compares incoming observations with an individual's prior accepted measurements and tracks deviations, persistence, and data quality.

The repository currently contains:

- retrospective PhysioNet/CinC Challenge 2019 cohort-analysis workflows;
- an experimental adaptive-twin software component and synthetic streaming demonstration;
- separate retrospective supervised experiments;
- tests, reproducibility workflows, research reports, a model card, and a proposed hardware integration blueprint.

The repository does **not** contain a validated patient-monitoring device or completed external/prospective clinical validation. The current synthetic streaming demonstration does not connect to a person or acquire real patient signals.

## Important interpretation boundaries

1. The adaptive-twin trajectory output is a unitless heuristic, not a calibrated probability of sepsis or deterioration.
2. The supervised retrospective experiments use the Challenge `SepsisLabel` target. This label is not independently adjudicated biological sepsis onset.
3. Set B is a held-out Challenge cohort, not an independent external clinical cohort.
4. Historical metric/reproducibility discrepancies are documented and must not be concealed, overwritten, or resolved by relaxing predeclared acceptance criteria.
5. No result in this repository establishes clinical utility, prospective performance, patient benefit, or a safe clinical operating threshold.

Please read [PROJECT_STATUS.md](PROJECT_STATUS.md), [MODEL_CARD.md](MODEL_CARD.md), [RELEASE_READINESS_AUDIT.md](RELEASE_READINESS_AUDIT.md), and [INDEPENDENT_EVALUATION_PROTOCOL.md](INDEPENDENT_EVALUATION_PROTOCOL.md) before reviewing claims.

## Review tracks

### A. Clinical and physiological review

We welcome review from clinicians, intensivists, emergency physicians, nurses, physiologists, and clinical researchers.

Questions to consider:

- Are the selected physiological channels and their proposed groupings justified?
- Are the units, sampling/update frequencies, missingness, and measurement contexts represented correctly?
- Could baseline adaptation learn illness, treatment effects, or sensor artefacts as a new normal?
- Are the proposed trajectory descriptions clinically interpretable without implying diagnosis?
- Which patient populations, care settings, or workflows would make the concept inappropriate?
- What outcomes and prediction horizons would be clinically meaningful to evaluate?

### B. Statistics and machine-learning review

We welcome review from biostatisticians, epidemiologists, ML researchers, and clinical informaticians.

Please assess:

- patient-level split integrity and possible leakage;
- source-data and cohort provenance;
- preprocessing and feature fitting confined to training data;
- target definition and the Challenge label's lead-time convention;
- discrimination, calibration, uncertainty intervals, missingness, and subgroup performance;
- threshold selection, sensitivity/PPV trade-offs, alert burden, and decision-curve or utility analysis where appropriate;
- whether conclusions are supported by the actual experiments and their limitations.

The current priority is the unresolved independent reconciliation described in [Issue #4](https://github.com/culprit-k/VITALIS/issues/4).

### C. Hardware and embedded-systems review

We welcome biomedical engineers, electronics developers, embedded-systems engineers, and hardware prototypers.

Start with [HARDWARE_INTEGRATION_BLUEPRINT.md](HARDWARE_INTEGRATION_BLUEPRINT.md). Review the proposed **bench-only** architecture and identify missing interface or verification requirements:

- exact sensor/device model and documented data access;
- signal name, unit, sampling/update frequency, timestamp source and clock synchronisation;
- quality indicators, artefact handling, dropout detection, stale-data behaviour and recovery;
- intermittent versus continuous measurements;
- power budget, charging, thermal constraints, enclosure and maintainability;
- communication security, device identity, data minimisation and local storage;
- electrical isolation, patient-connected-part classification, applicable safety standards, and qualified review;
- bench verification of accuracy, latency, packet loss, clock drift, dropout recovery, and fail-safe behaviour.

Do not connect a person to a DIY prototype. A future hardware prototype must remain on a simulator or appropriate non-human bench setup until qualified experts have assessed safety and regulatory requirements.

### D. Software and reproducibility review

We welcome Python developers, software testers, ML platform engineers, and research-software specialists.

Review:

- reproducibility from an exact commit and declared environment;
- causal feature construction and session/patient separation;
- input validation for timestamps, units, quality, missingness, and stale data;
- test coverage for edge cases and failure states;
- model/configuration versioning and provenance;
- whether synthetic demonstrations are clearly distinguished from real observations.

## How to submit a useful review

Open an issue using the appropriate template, or comment on the existing review gates:

- [Independent statistical and methods review — Issue #4](https://github.com/culprit-k/VITALIS/issues/4)
- [Next-phase reproducibility and bench-prototype gate — Issue #6](https://github.com/culprit-k/VITALIS/issues/6)

Please include:

1. **Scope reviewed:** documents, files, workflow run, commit, or experiment.
2. **Finding:** confirmed issue, potential concern, or recommendation.
3. **Evidence:** citation, calculation, code location, test, or rationale.
4. **Impact:** scientific, clinical, engineering, privacy, or reproducibility consequence.
5. **Suggested next step:** a practical test, correction, or decision.
6. **Reviewer context:** relevant expertise and any conflicts of interest (optional).

Do not include patient-level data or private institutional information. Reviewer names and affiliations will only be published with explicit permission.

## What a review does not mean

A review does not establish clinical validation, safety, efficacy, regulatory compliance, patentability, or endorsement by the reviewer's institution. Do not use the project or its outputs in patient care.

## Contribution and licensing note

The repository currently has no top-level `LICENSE` file. Public GitHub visibility is not a reuse licence. Feedback and review are welcome, but prospective code or hardware contributions should first be discussed with the maintainer so that software and hardware licensing, attribution, and intellectual-property expectations can be made explicit. See [CONTRIBUTING.md](../CONTRIBUTING.md).
