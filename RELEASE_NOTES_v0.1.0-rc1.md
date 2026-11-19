# VITALIS v0.1.0-rc1 — Research Release Candidate

**Status:** Release candidate in review; not a stable release  
**Date:** 19 November 2026  
**Branch:** `release/v0.1.0-rc1`

## Summary

This candidate packages the VITALIS research prototype for reproducibility and independent review. It includes an adaptive physiological deviation twin, separate retrospective Challenge-label forecasting experiments, synthetic streaming demonstrations, aggregate-only reporting, and research protocols.

## Changes in this candidate

- Corrected the adaptive-twin persistence classification so a multisystem persistence state requires persistent deviations across distinct physiological systems.
- Added the separate `persistent_channel_deviation` state for persistent channels confined to one system.
- Added regression coverage for the single-system versus multisystem distinction.
- Exposed persistent channel/system counts in the synthetic twin dashboard.
- Clarified the bounded unitless score and persistence semantics in the implementation specification.
- Added a formal RC1 readiness gate and candidate status to the README.
- Enabled the strict full-cohort workflow to run on the RC1 branch when its configured path trigger is met.

## Verification

The adaptive-twin code and regression test passed standard CI on code snapshot `01d6845245edf6dfa55e49a4b58993f8eb790213` in [run #44467431900](https://github.com/culprit-k/VITALIS/actions/runs/44467431900). The RC1 branch includes subsequent documentation and workflow-trigger changes; final candidate CI and full-cohort reproduction must be checked on the final branch commit before acceptance.

## Important limitations

- Set B is a held-out Challenge benchmark cohort, not independent external clinical validation.
- The supervised target is entry into the Challenge `SepsisLabel` positive window, not independently adjudicated biological sepsis onset.
- The adaptive twin emits a unitless heuristic, not a sepsis probability or clinical risk score.
- Historical temporal-model metric discrepancies and probability-quality limitations remain unresolved.
- No physical wearable, sensor system, PCB or bedside device has been validated.
- Independent statistical/clinical review, institutional governance, genuinely external validation, prospective evaluation and hardware safety review remain outstanding.

## Intended use and safety

Research and education only. This candidate is not a medical device or clinically validated decision-support system. Do not use its outputs to diagnose, triage, monitor or treat any person. Do not connect the prototype to a patient.

See [RC1 readiness and acceptance gates](docs/RC1_READINESS.md) before describing or distributing this candidate.
