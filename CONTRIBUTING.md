# Contributing to VITALIS

Thank you for your interest in VITALIS. Contributions that improve scientific clarity, reproducibility, safety, software quality, or the feasibility of a bench prototype are welcome.

VITALIS is a **research prototype**. It is not a medical device or a clinically validated decision-support system. Its outputs must not be used for diagnosis, triage, monitoring, treatment, or patient-care decisions.

## Start here

Before opening an issue or pull request, read:

1. [Project status and evidence boundaries](docs/PROJECT_STATUS.md)
2. [Model card](docs/MODEL_CARD.md)
3. [AI mathematics and algorithms](docs/AI_MATHEMATICS_AND_ALGORITHMS.md)
4. [Hardware integration blueprint](docs/HARDWARE_INTEGRATION_BLUEPRINT.md)
5. [Community review guide](docs/COMMUNITY_REVIEW_GUIDE.md)
6. [Open reproducibility review, Issue #4](https://github.com/culprit-k/VITALIS/issues/4)
7. [Next-phase gate, Issue #6](https://github.com/culprit-k/VITALIS/issues/6)

Please distinguish implemented software from proposed architecture and planned experiments. The current adaptive-twin trajectory score is a unitless heuristic, not a sepsis probability. The supervised benchmark experiments target entry into the PhysioNet/CinC Challenge 2019 `SepsisLabel` positive window, not independently adjudicated biological sepsis onset. Set B is a held-out Challenge cohort, not an independent external clinical cohort.

## Ways to contribute

- **Clinical and physiology review:** challenge assumptions, channel definitions, endpoint meaning, interpretation, workflow relevance, and failure modes.
- **Statistics and machine learning:** review patient-level splitting, leakage controls, calibration, uncertainty, missingness, subgroup evaluation, alert burden, and reproducibility.
- **Biomedical hardware:** review the proposed bench architecture, interfaces, signal acquisition, timestamps, data quality, power, electrical safety, and verification requirements.
- **Software engineering:** improve tested, documented, hardware-independent components; preserve causal and patient/session boundaries.
- **Documentation and education:** clarify methods, limitations, reproducibility instructions, and technical diagrams.

Small, specific contributions are useful. A well-supported criticism or a reproducible bug report is as valuable as a feature.

## How to contribute

1. Search existing issues to avoid duplicates.
2. For scientific or hardware feedback, use the matching GitHub issue form or comment on the relevant open issue.
3. For code or documentation, open an issue first when the change affects algorithm semantics, data contracts, outputs, experiment protocols, or hardware interfaces.
4. Fork the repository and create a focused branch.
5. Keep each pull request limited to one concern. Explain the motivation, assumptions, validation performed, and known limitations.
6. Run the relevant checks locally. For the standard Python development checks:

   ```bash
   python -m pip install -e ".[dev]"
   pytest
   ```

7. Open a pull request against `main`. Do not include datasets, patient-level records, credentials, private keys, or generated files that are not required by the change.

## Scientific review expectations

Please state:

- which file, claim, method, or experiment you reviewed;
- what evidence or reasoning supports your comment;
- whether the point is a confirmed defect, a concern, or a suggestion;
- the likely impact and a practical way to test or resolve it;
- any relevant expertise, conflicts of interest, or limitations you wish to disclose.

Do not describe a review as an endorsement. Reviewer identity and affiliation will only be published with the reviewer's explicit permission.

## Hardware and human-safety boundaries

Hardware contributions must remain **bench-only** and use synthetic signals, simulators, or approved non-human test equipment. Do not connect DIY circuitry or an unverified sensor system to a person. ECG front ends and patient-connected equipment require qualified biomedical/electrical safety review and appropriate isolation. No hardware design in this repository is approved for human use.

Before proposing components, document the exact part number, interface, available fields, units, sampling/update rate, timestamp behaviour, quality flags, data-export restrictions, and power requirements. Do not imply that intermittent cuff blood-pressure readings are continuous measurements.

## Data protection and research governance

- Never upload identifiable patient data, medical record numbers, dates of birth, row-level patient data, private clinical datasets, credentials, or access tokens.
- Do not put patient-specific examples in public issues, pull requests, screenshots, or logs.
- Do not access or analyse a new clinical cohort without the required dataset permissions, institutional approvals, ethics/governance determinations, and an approved data-management plan.
- Public aggregate metrics still require provenance and disclosure review before publication.
- Do not use VITALIS outputs to guide patient care.

## Licensing and intellectual property — important

At the time this guide was added, the repository had **no top-level `LICENSE` file**. Public visibility on GitHub does not by itself grant permission to reuse, modify, redistribute, or commercially exploit the code or hardware designs.

Until the maintainer publishes an explicit software licence and, where appropriate, a separate hardware-design licence:

- feedback, review comments, and issue discussions are welcome;
- do not assume that source code or hardware drawings are licensed for reuse;
- do not submit third-party, proprietary, confidential, or restricted material;
- contact the maintainer through the repository before making a contribution that depends on a particular licence or ownership arrangement.

The project maintainer must choose and publish appropriate licence terms before representing VITALIS as an unrestricted open-source or open-hardware project. Contributors should retain rights to their own work and clearly identify third-party material and its licence.

## Communication

Keep discussions respectful, evidence-focused, and specific. Please report security vulnerabilities privately through GitHub's security reporting mechanism where available; do not publish exploitable details in an ordinary issue.

Thank you for helping make VITALIS more rigorous, transparent, and useful as a research project.
