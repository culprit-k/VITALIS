# VITALIS release verification checkpoint — 18 October 2026

## Current source and standard CI

- **Repository:** `culprit-k/VITALIS`
- **Reviewed main commit:** `40d60c8a78694e2fb1cb91b4d6af8fff981ffc3d`
- **Standard CI:** [run #39065494202](https://github.com/culprit-k/VITALIS/actions/runs/39065494202) — **success** on the exact commit above.
- **Verified CI steps:** source-manifest verification, repository and reachable-history hygiene audits, synthetic twin and integrated-inference smoke tests, 1,000-frame aggregate-only synthetic replay benchmark, and the complete `pytest` suite all passed.
- **Retained CI artifact:** [source audit artifact #12113505620](https://github.com/culprit-k/VITALIS/actions/runs/39065494202/artifacts/12113505620). It contains the source/environment manifest, history audit, and synthetic benchmark report; it is not a full-cohort reproduction artifact.

## Frozen evaluation-source integrity

- The Git tree for reviewed `main` still records `scripts/evaluate_horizon_cross_cohort.py` at the protected baseline blob `891b84ad4a5da039f1dc38411211c503c971167c`.
- Do not edit that evaluator, relax the six-decimal mean/sample-SD reconciliation tolerance, or use Set B for model fitting, calibration, feature selection, or threshold selection.
- The latest recorded successful extended full-cohort reproduction is [run #39057821508](https://github.com/culprit-k/VITALIS/actions/runs/39057821508) on commit `14440230ff19bd1ade378374c47158cda321f628): 42/42 metric mean/sample-SD pairs and 84/84 scalar values matched; Set A and Set B integrity audits passed; retained outputs were aggregate-only.
- **Important scope limit:** that full-cohort run predates the latest ESP32 gateway changes. Current standard CI passed after those changes, and the frozen evaluator blob is unchanged, but a full-cohort reproduction on exact commit `40d60c8a78694e2fb1cb91b4d6af8fff981ffc3d` has not yet been verified. Do not describe the full-cohort result as having run on the current commit.

## Software-only gateway status

The ESP32-S3 gateway sends generated heart-rate and SpO₂ values over USB serial to the Python stream/twin. Automated tests cover duplicate/regressed frames, timestamps, end-to-end synthetic replay, and gateway restart handling. This does not yet constitute a physical hardware bench, real sensor integration, or clinical validation.

## Remaining release gates

1. **Exact-current-main full-cohort reproduction:** rerun the existing strict workflow on the current reviewed commit, with extended analyses enabled where supported; confirm baseline blob, unchanged six-decimal reconciliation, Set B evaluation-only, and aggregate-only artifact contents.
2. **Independent methods review:** obtain written findings from an independent qualified clinician/statistician/methods reviewer.
3. **Physical synthetic bench:** test USB serial with the selected board, dummy/synthetic inputs, disconnect/reconnect and reboot recovery; record device, host, power and safety checks. No patient or clinical sensor connection.
4. **External cohort and governance:** establish an independent cohort and document institutional/ethics, privacy, security, and applicable safety/regulatory determinations before any clinical translation.

## Research boundary

VITALIS remains a research prototype, not a clinically validated medical device or decision-support system. The prediction endpoint is entry into the Challenge `SepsisLabel` positive window, not independently adjudicated sepsis onset. No output from the current prototype should guide patient care.
