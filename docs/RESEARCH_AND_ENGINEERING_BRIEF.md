# VITALIS — Research and Engineering Concept Brief

**Version:** 1.0  
**Date:** 19 November 2026  
**Project lead:** Abhijith Premjithlal, MBBS student, Bukhara State Medical Institute, Uzbekistan  
**Repository:** https://github.com/culprit-k/VITALIS

## Project concept

VITALIS explores an **Adaptive Physiological Digital Twin for Early Prediction of Clinical Deterioration**.

The research question is whether a software representation can learn a person's reference physiology from earlier accepted observations, compare new measurements with that reference, and describe the magnitude, persistence, and cross-system pattern of deviations over time.

The long-term concept is to investigate whether such an adaptive representation, connected to reliable physiological data acquisition, could support research into clinical deterioration trajectories. This is a research question, not an established clinical benefit.

## Conceptual data flow

1. **Observe:** receive time-stamped physiological measurements.
2. **Validate:** check units, time, quality, missingness, ordering, and freshness.
3. **Model:** compare observations with personal reference patterns and calculate temporal deviation features.
4. **Review:** present data quality and trajectory summaries for research evaluation and independent review.

Parameters considered in the research architecture include ECG/heart-rate variability, heart rate, SpO₂, respiratory rate, blood pressure, temperature, peripheral perfusion, laboratory values, fluid balance, and medication history. Availability, update frequency, quality indicators, and clinical interpretation differ by device and data source; no single prototype currently acquires all of these.

## What exists in the repository

- Retrospective PhysioNet/CinC Challenge 2019 cohort-analysis and machine-learning workflows.
- An experimental adaptive-twin software component with robust-baseline, deviation, persistence, and trajectory heuristics.
- A timestamped, unit-checked stream contract and synthetic streaming demonstration.
- Separate retrospective supervised experiments and documented evaluation protocols.
- Tests, continuous-integration workflows, research reports, a model card, and reproducibility documentation.
- A proposed sensor-to-gateway hardware integration blueprint and synthetic gateway examples.

The software demonstrations use generated/synthetic signals. The repository does not contain a completed integrated wearable, custom validated PCB, or physical patient-monitoring device.

## Evidence and interpretation boundaries

- The adaptive-twin trajectory score is a **unitless heuristic**, not a calibrated probability of sepsis or deterioration.
- The retrospective supervised experiments target entry into the PhysioNet/CinC Challenge 2019 `SepsisLabel` positive window. This is not independently adjudicated biological sepsis onset.
- Set B is a held-out cohort from the same Challenge, not an independent external clinical cohort.
- Historical metric/reproducibility discrepancies remain documented and require independent investigation; acceptance criteria must not be relaxed to make results match.
- Retrospective benchmark results do not establish clinical utility, prospective performance, patient benefit, subgroup safety, or a clinically appropriate operating threshold.
- No VITALIS output is approved for diagnosis, triage, monitoring, treatment, or patient-care decisions.

Read [PROJECT_STATUS.md](PROJECT_STATUS.md), [MODEL_CARD.md](MODEL_CARD.md), [RELEASE_READINESS_AUDIT.md](RELEASE_READINESS_AUDIT.md), and [INDEPENDENT_EVALUATION_PROTOCOL.md](INDEPENDENT_EVALUATION_PROTOCOL.md) for detailed status and protocols.

## Collaboration opportunities

### Clinical and physiological review
Clinicians, intensivists, emergency physicians, nurses, physiologists, and clinical researchers can assess channel selection, baseline adaptation, signal interpretation, clinical endpoints, prediction horizons, workflow relevance, and unsafe or misleading interpretations.

### Statistics and machine learning
Biostatisticians, epidemiologists, ML researchers, and clinical informaticians can review data provenance, patient-level splits, leakage controls, target semantics, calibration, uncertainty, missingness, subgroup performance, and alert burden.

### Biomedical hardware and embedded systems
Biomedical engineers, electronics developers, and embedded engineers can review sensor data access, interface contracts, timestamp synchronisation, quality flags, gateway architecture, power, cybersecurity, and bench verification.

### Software and research engineering
Software contributors can improve causal feature construction, stream validation, test coverage, experiment provenance, reproducibility, and documentation.

## Proposed development stages

1. **Independent review:** challenge the methods, cohort provenance, evaluation, target meaning, and claims.
2. **Bench requirements:** freeze a non-clinical data dictionary, supported input fields, units, update rates, timestamp strategy, quality flags, and failure states before selecting components.
3. **Synthetic/replay bench prototype:** test a gateway with generated signals or suitable non-human bench equipment; measure latency, packet loss, clock drift, dropout recovery, and fail-safe behaviour.
4. **Independent evidence pathway:** only after permissions and governance determinations, plan evaluation on an independently collected cohort.
5. **Future prospective research:** only after separate ethics, privacy, institutional, safety, and regulatory review; any initial prospective evaluation should be silent-mode and must not influence care.

## How to participate

- [Community review guide](COMMUNITY_REVIEW_GUIDE.md)
- [Contributing guide](../CONTRIBUTING.md)
- [Hardware integration blueprint](HARDWARE_INTEGRATION_BLUEPRINT.md)
- [Independent methods review — Issue #4](https://github.com/culprit-k/VITALIS/issues/4)
- [Next-phase gate — Issue #6](https://github.com/culprit-k/VITALIS/issues/6)
- [Community call for clinical/statistical/ML reviewers — Issue #49](https://github.com/culprit-k/VITALIS/issues/49)
- [Hardware architecture review challenge — Issue #50](https://github.com/culprit-k/VITALIS/issues/50)
- [Licensing decision — Issue #51](https://github.com/culprit-k/VITALIS/issues/51)

Please submit specific findings with the reviewed file/commit, evidence, impact, and suggested next step. Reviewer identities and affiliations will only be published with explicit permission.

## Safety, governance, and licensing

All hardware work is **bench-only** and must use synthetic signals, simulators, or appropriate non-human test equipment. Do not connect a person to DIY or unverified hardware.

Do not publish identifiable patient data, patient-level records, credentials, private datasets, or confidential institutional information. New cohort research requires the relevant dataset permissions, institutional governance and ethics determinations, and an approved data-management plan.

The repository currently has no top-level `LICENSE` file. Public GitHub visibility does not grant blanket reuse rights. Feedback and review are welcome, but contributors should read [CONTRIBUTING.md](../CONTRIBUTING.md) and discuss licensing and intellectual-property expectations with the maintainer before submitting code or hardware designs.

**VITALIS is a research prototype, not a clinically validated medical device or clinical decision-support system.**
