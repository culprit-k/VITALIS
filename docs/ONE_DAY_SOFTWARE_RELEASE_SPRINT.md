# VITALIS one-day software-prototype sprint

**Owner:** project team  
**Target:** a defensible research-software release candidate, not clinical readiness  
**Status:** execution checklist; every item must be backed by an artifact or passing check.

## Non-negotiable scope boundary

VITALIS predicts a retrospective PhysioNet/CinC Challenge 2019 SepsisLabel-positive-window target. This is not independently adjudicated biological onset, prospective validation, or a clinical device. Do not use outputs for patient care. No claim of clinical benefit, patentability, or validated early warning is permitted without separate evidence.

## Priority order for the one-day push

### P0 — stop losing time to avoidable CI failures
- [ ] One canonical Python 3.11 full-cohort run per branch; duplicate runs are cancelled by workflow concurrency.
- [ ] Unit tests and dashboard tests pass on the same commit.
- [ ] Full-cohort run downloads official data into ephemeral runner storage, audits cache integrity, and emits aggregate-only artifacts.
- [ ] Source provenance and numerical-backend diagnostics are recorded. Diagnostics must not pretend that an unobserved library backend is a reproducibility pass.
- [ ] Historical reconciliation is reported honestly; never lower the six-decimal acceptance rule or overwrite the historical baseline to turn CI green.

### P1 — verify predictive experiment
- [ ] Confirm Set A/Set B cohort counts and target-window label semantics.
- [ ] Run the fixed 1/3/6-hour horizons and seeds 42/123/2026 with patient-disjoint fitting.
- [ ] Report AUROC, AUPRC, Brier/log loss where available, calibration intercept/slope, sensitivity, specificity, PPV, alert burden, lead/coverage metrics and patient-cluster uncertainty.
- [ ] Set B is frozen evaluation only: no fitting, calibration, threshold selection, feature selection, or model selection.
- [ ] If the historical baseline cannot be reproduced from its recorded provenance, preserve it and create a separately named clean-checkout reference only after the protocol is reviewed and a second independent run matches it.

### P2 — physiology-twin engineering verification
- [ ] Unit and property tests cover missing/invalid/out-of-order values, stale observations, unit validation, patient/session reset, baseline warm-up, outlier resistance, CUSUM, persistence, multisystem aggregation, and recovery/reset behavior.
- [ ] Verify every twin output is a deviation/trajectory heuristic, not a clinical probability or diagnosis.
- [ ] Synthetic demo is deterministic and labelled synthetic; no synthetic result is presented as cohort evidence.
- [ ] Confirm no row-level predictions, patient identifiers, raw data, or cache files enter Git or released artifacts.

### P3 — release candidate
- [ ] Run the documented local quickstart from a fresh environment.
- [ ] Generate a model card, data/protocol card, aggregate evaluation report, known-limitations list, and reproducibility manifest.
- [ ] Freeze source commit, dependency constraints, configurations, seeds, and artifact hashes.
- [ ] Keep pull request draft until gates pass; independent review is required before merge.

## Time-boxing and honest completion criteria

The one-day target is an engineering time-box, not permission to skip gates. If a full-cohort job exceeds the time window, finish code review, unit tests, synthetic tests, and release packaging, but mark cohort reproduction pending. A fast software release candidate can be completed in one day only if the expensive cohort workflow and review gates pass in that window.

## Release decision

**Release candidate:** all P0/P2/P3 checks pass and P1 outputs exist with limitations documented.  
**Research result reproduced:** exact approved-baseline reconciliation passes twice from clean checkouts.  
**Clinically validated:** out of scope for this sprint; requires independent prospective evidence, risk management, regulatory review, and clinical oversight.
