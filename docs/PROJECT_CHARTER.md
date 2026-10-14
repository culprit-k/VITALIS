# VITALIS — Project Charter

## Purpose
VITALIS is a research-first project exploring adaptive physiological modeling for early prediction of sepsis-related clinical deterioration using longitudinal patient observations.

## Research principles
- Treat this as a research prototype, not a clinically validated decision-support system.
- Use patient-level separation for model development and evaluation to reduce leakage.
- Document cohort definitions, label timing, missing-data handling, feature availability, and alert burden.
- Report discrimination, calibration, sensitivity, specificity, lead time, and patient-level uncertainty where appropriate.
- Never commit identifiable patient data, secrets, access tokens, or raw clinical datasets to this repository.
- Make no claims of clinical utility, novelty, or patentability without appropriate validation and review.

## Initial scope
1. Reproducible cohort and data validation pipeline.
2. Baseline and temporal-feature models.
3. Patient-level validation and alert-burden analysis.
4. Tests, documentation, and reproducible experiment configuration.
5. A dashboard only after the data and evaluation pipeline is reliable.

## Dataset note
The PhysioNet/CinC Challenge 2019 data may be used locally under its applicable terms. The challenge's `SepsisLabel` already incorporates a six-hour lead convention; do not shift it a second time. A positive label is not equivalent to independently observed clinical onset.

## Current status
This repository is being initialized. No model performance or clinical readiness is asserted by this charter.
