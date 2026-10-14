# VITALIS

**VITALIS** is a research-first platform exploring adaptive physiological modeling for early prediction of sepsis-related clinical deterioration from longitudinal observations.

> **Research prototype only.** VITALIS is not a medical device or a clinically validated decision-support system. Do not use it to guide patient care.

## Research goals

- Build a reproducible, auditable cohort pipeline.
- Compare transparent baselines with temporal and patient-specific physiological features.
- Prevent patient leakage and label-timing errors.
- Evaluate discrimination, calibration, sensitivity, specificity, lead time, and alert burden.
- Document uncertainty and limitations before considering any clinical translation.

## Repository layout

```text
docs/                 Research protocol and data dictionary
src/vitalis/          Reusable feature and validation code
tests/                Unit tests
scripts/              Reproducible command-line workflows
configs/              Experiment configuration examples
```

## Data and privacy

The PhysioNet/CinC Challenge 2019 dataset may be used locally subject to its access terms. **Do not commit raw patient data, derived patient-level records, model outputs tied to individuals, credentials, or tokens.** Keep local datasets outside this repository.

The challenge `SepsisLabel` already uses a six-hour lead convention. Do not shift it a second time. A positive label should not be described as independently observed clinical onset.

## Development status

The repository is being rebuilt from a clean, documented foundation. No performance, novelty, patentability, or clinical utility claim is made until the relevant analysis is independently verified.

## Development setup

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
# Activate the environment, then:
pip install -e ".[dev]"
pytest
```

See [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md), [`docs/COHORT_PROTOCOL.md`](docs/COHORT_PROTOCOL.md), and [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).
