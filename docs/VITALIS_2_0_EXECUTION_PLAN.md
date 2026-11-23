# VITALIS 2.0 — Integrated Research and Product Execution Plan

**Status:** planning baseline for review; research and bench engineering only  
**Created:** 23 November 2026  
**Parent snapshot:** `a4d4d2641ffe13383960d5094ca6791e55befe1c` (VITALIS v0.1.0-rc1 candidate)  
**Working branch:** `research/vitalis-2.0-execution-plan`

## 1. North-star objective

Develop VITALIS as an evidence-led adaptive physiological research platform that can ingest timestamped physiological observations, estimate an individual's changing reference state, describe persistent deviations and data quality, and support separately validated research on deterioration trajectories.

The long-term product concept is a modular wearable/gateway/software system. The immediate deliverable is **not** a patient-ready device: it is a reproducible software research platform plus a non-human bench acquisition prototype.

## 2. Non-negotiable boundaries

- Research and education only. No diagnosis, triage, treatment, patient monitoring, or patient-care use.
- Do not connect DIY or unreviewed electronics to a person.
- Keep the adaptive twin's unitless heuristic separate from supervised model probabilities.
- The Challenge 2019 `SepsisLabel` target is entry into a benchmark positive window, not independently adjudicated biological sepsis onset.
- Set B is a held-out cohort from the same Challenge, not independent external validation; do not tune on it.
- Preserve historical evaluator source, baselines, six-decimal reconciliation rule, and old artifacts. Never silently overwrite unfavorable results.
- Keep raw patient data, identifiers, patient-level features, caches, row-level predictions, credentials, and restricted logs out of GitHub/public artifacts.
- A SHA-256 digest derived from patient data is still patient-derived material; hashing alone does not establish anonymisation.
- No clinical utility, patient benefit, novelty, patentability, or medical-device readiness claims without appropriate evidence and review.

## 3. Workstreams

### A — Software and adaptive engine

**Objective:** improve the quality, interpretability, robustness and reproducibility of longitudinal physiological modelling.

Tasks:
1. Map the existing stream contract, adaptive twin, feature generators, dashboards, tests and benchmark evaluator before changing code.
2. Specify a versioned observation schema covering channel, value, unit, timestamp, source, quality, freshness, missingness and session boundaries.
3. Add explicit signal-quality and missingness states; fail closed on invalid units, stale/out-of-order samples, schema mismatch and insufficient history.
4. Evaluate baseline adaptation, warm-up, drift, persistence, cross-system concordance and reset/session isolation using synthetic and authorised replay data.
5. Compare candidate models against simple static and temporal baselines using patient-level partitions and predeclared metrics.
6. Investigate the negative patient-relative physiology ablation. Do not promote it or claim improvement unless a new experiment supports that conclusion.
7. Keep calibration and threshold selection on development data only. Require an independently reviewed alert-budget/utility objective before choosing an operating point.
8. Add explainability that reports contributing channels, data quality, baseline coverage and reasons a trajectory is unavailable.
9. Add deterministic tests for dropout, missingness, clock skew, reconnection, drift, unit errors, corrupted inputs and model/schema mismatch.

**Acceptance:** versioned feature/stream contract, test coverage, reproducible experiment report, explicit negative findings and no regression to the preserved benchmark evaluator.

### B — Hardware and embedded systems

**Objective:** build a modular, non-human bench prototype that can safely transport documented test signals into the existing software interface.

Initial architecture:
- Sensor/signal simulator or dummy fixture.
- Documented sensor modules only after interface and data-export review.
- Embedded acquisition/gateway with sequence tracking and timestamps.
- Canonical observation adapter with unit, quality, freshness and ordering checks.
- Local compute and research dashboard.
- Local-first storage, access control and audit logging.

Tasks:
1. Freeze the bench requirements and data dictionary before purchasing components.
2. Compare candidate modules by exact model, manufacturer documentation, accessible fields, sample/update rates, units, quality flags, interface, power, cost and licence/data-export restrictions.
3. Start with synthetic signal replay and a gateway; add one sensor channel at a time.
4. Specify time synchronisation, clock drift, packet loss, buffering, reconnect, stale data and missingness behaviour.
5. Define bench tests for signal fidelity against a simulator/reference, end-to-end latency, throughput, dropout recovery, timestamp integrity, power and thermal behaviour.
6. Document electrical isolation, EMC, enclosure, battery, cybersecurity and risk questions for qualified reviewers before any human-connected design.
7. Do not freeze a BOM or claim a wearable exists until parts and tests have been independently reviewed.

**Acceptance:** reviewed bench requirements, reproducible synthetic/replay demonstration, measured bench report, risk register and explicit list of unimplemented sensor interfaces.

### C — Clinical research and independent validation

**Objective:** establish whether the research outputs generalise and provide information beyond established baselines.

Tasks:
1. Obtain independent clinical, statistical and ML-methods review of cohort provenance, split integrity, target semantics, missingness, calibration, uncertainty, alert burden and claims.
2. Define a clinically meaningful event and prediction index time with an independent clinical endpoint owner. Do not equate the Challenge label with biological onset.
3. Identify a genuinely independent cohort and document data provenance, overlap checks, permissions, governance and access conditions before outcome access.
4. Draft a protocol and machine-checkable lockfile: population, inclusion/exclusion, index time, endpoint, model hash, features, thresholds, calibration, primary metrics, subgroup plan, uncertainty, stopping rules and sign-offs.
5. Freeze the model and analysis plan before opening independent evaluation outcomes.
6. Report AUROC/AUPRC with prevalence, Brier/log loss, calibration-in-the-large and slope, sensitivity/specificity/PPV/NPV, alert burden per patient-day, event-level lead time, missingness and subgroup uncertainty.
7. Consider prospective silent-mode work only after institutional, ethics, privacy, security and safety approvals. No outputs should influence care in such a study.
8. Treat clinical impact evaluation as a separate later study requiring its own approvals and design.

**Acceptance:** signed independent review, documented governance/ethics determination, frozen protocol and model, and a genuinely independent evaluation report. If access or approval is unavailable, report the gate as blocked rather than implying validation.

### D — Manuscript and dissemination

**Objective:** prepare a transparent, reproducible first paper and a responsible publication strategy.

Tasks:
1. Freeze the manuscript research question and contribution statement.
2. Build a provenance matrix mapping each claim/table/figure to exact source commit, workflow run, artifact and analysis.
3. Report the adaptive twin and supervised benchmark models as separate methods and outputs.
4. Describe the Challenge target precisely as entry into the `SepsisLabel` positive window.
5. Include negative physiology-ablation results, calibration limitations, lack of a selected operating threshold and the privacy qualification.
6. Include cohort flow, patient-level splits, missingness, uncertainty, software environment, reproducibility and data governance.
7. Prepare a methods supplement and a research-software description.
8. Shortlist venues only after checking scope, indexing, peer-review model, reporting requirements, publication fees, preprint rules and data/code policies.
9. Obtain independent statistical and clinical review before submission.

**Acceptance:** complete manuscript draft with claim-to-evidence traceability, transparent limitations and a documented venue decision. Submission is a separate approval.

## 4. Immediate release and governance gates

These precede any public artifact redistribution or stable release:

1. **RC1 artifact privacy:** inspect every patient-derived fingerprint in run #44467873336 artifact #14509017475; obtain independent privacy/data-governance review; minimise or remove linkable digests in a new candidate if required; inspect the replacement artifact. Preserve the historical artifact and its provenance.
2. **Independent methods review:** use the reviewer package and existing community call; reviewers must be independent of the original analysis.
3. **Current-main reproduction:** run the strict full-cohort workflow on the exact current main SHA when the authorised data environment is available. The RC1 result is not a substitute for current-main reproduction.
4. **Licensing:** decide software, documentation/assets and hardware-design terms before inviting code/design contributions or claiming open-source/open-hardware status.
5. **Release decision:** keep RC1 draft; no stable tag or clinical claim until the applicable gates are satisfied.

## 5. First 90-day sequence

Dates are planning targets, not evidence of completion.

| Period | Priority deliverables | Exit condition |
|---|---|---|
| Days 1–14 | Artifact privacy inventory; reviewer outreach; repository architecture audit; bench requirements and data dictionary; manuscript outline | Risks and interfaces documented; no unsafe hardware procurement |
| Days 15–30 | Software quality/missingness test plan; synthetic gateway specification; candidate component comparison; protocol/endpoint consultation | Reviewed specs and test plans |
| Days 31–60 | Implement only approved software changes on a research branch; synthetic/replay gateway; bench tests; methods draft and figures | CI/replay evidence and reviewable manuscript draft |
| Days 61–90 | Independent code/methods review; bench report; independent-cohort feasibility/governance package; venue shortlist | Decision on next research stage, with blockers explicit |

## 6. Decision gates

- **G0 — Integrity:** exact source, environment and historical baseline preserved.
- **G1 — Privacy:** artifact and data-flow review accepted by an independent reviewer.
- **G2 — Software:** stream contracts, tests and replay reproducibility pass.
- **G3 — Bench:** non-human hardware/gateway tests pass against predeclared acceptance criteria.
- **G4 — Methods:** independent clinical/statistical review and protocol freeze.
- **G5 — External evidence:** authorised genuinely independent cohort evaluated with frozen model and analysis plan.
- **G6 — Product translation:** separate safety, regulatory, security, usability and clinical impact work; outside the current research prototype.

A gate cannot be declared passed by a plan, a synthetic demo, a successful CI run alone, or the project author reviewing their own work.

## 7. Existing GitHub tracking

- [RC1 release candidate — PR #48](https://github.com/culprit-k/VITALIS/pull/48)
- [Independent scientific review package — PR #56](https://github.com/culprit-k/VITALIS/pull/56)
- [Overall next-phase gate — Issue #6](https://github.com/culprit-k/VITALIS/issues/6)
- [Independent review gate — Issue #4](https://github.com/culprit-k/VITALIS/issues/4)
- [Community clinical/statistical/ML review — Issue #49](https://github.com/culprit-k/VITALIS/issues/49)
- [Hardware architecture challenge — Issue #50](https://github.com/culprit-k/VITALIS/issues/50)
- [Licensing decision — Issue #51](https://github.com/culprit-k/VITALIS/issues/51)
- [RC1 artifact privacy review — Issue #57](https://github.com/culprit-k/VITALIS/issues/57)
- [First manuscript — Issue #58](https://github.com/culprit-k/VITALIS/issues/58)

## 8. Immediate next actions

1. Complete the artifact fingerprint inventory and privacy reviewer brief.
2. Review the current software stream and twin implementation against the hardware blueprint; produce a gap matrix before coding.
3. Create the bench observation schema and synthetic/replay acceptance test matrix.
4. Draft the first manuscript abstract, methods outline and claim-to-evidence matrix.
5. Prepare a concise, technically specific request for independent reviewers and hardware contributors.

**Safety statement:** VITALIS remains a research and education prototype. Do not connect it to a person or use it for patient-care decisions.
