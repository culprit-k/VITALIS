# VITALIS combined framework and retrospective evaluation study — protocol v0.1

**Status:** protocol draft for independent clinical/statistical review; not preregistered  
**Study type:** research software description plus retrospective secondary analysis of a public benchmark cohort  
**No clinical deployment or patient-care use**

## 1. Publication strategy

Prepare one combined manuscript only if the final word count and journal scope can accommodate both:
1. the adaptive physiological digital-twin software architecture and its synthetic/replay engineering evaluation; and
2. the retrospective supervised forecasting experiments and their reproducibility, calibration and limitations.

Keep the two components analytically distinct. The adaptive twin is a unitless, causal deviation heuristic. The supervised models estimate a benchmark target. A synthetic bench result is not clinical validation, and a retrospective benchmark result is not hardware validation.

If the combined manuscript becomes unfocused or exceeds a target journal's scope, split into:
- Paper A: VITALIS research software, observation contract, adaptive twin and synthetic/bench verification.
- Paper B: retrospective benchmark prediction analysis and probability-quality findings.

Do not split solely to inflate publication count; each paper must have a distinct research question and sufficient independent contribution.

## 2. Primary objectives

### Objective 1 — Software framework
Describe the modular architecture, versioned observation contract, timestamp/unit/quality/freshness validation, causal robust reference estimation, missingness behaviour, persistence and drift summaries, and separation from supervised forecasting.

### Objective 2 — Synthetic/replay engineering evaluation
Evaluate deterministic correctness and robustness under predeclared synthetic scenarios: nominal input, missingness, stale/future timestamps, duplicates, out-of-order data, sequence gaps, packet loss, reconnect, source replacement, flatline, spikes, drift, malformed frames and session reset.

Primary engineering outcomes: accepted/rejected frame counts, sequence integrity, missingness correctness, state carryover errors, end-to-end latency distribution, throughput, recovery time and resource use. These are software/bench outcomes, not clinical performance metrics.

### Objective 3 — Retrospective supervised analysis
Report the existing retrospective prediction experiments using PhysioNet/CinC Challenge 2019 data, including exact source provenance, patient-level split design, 1/3/6-hour future positive-window target, calibration and threshold-selection safeguards, probability metrics, uncertainty and unfavorable ablation findings.

The Challenge repository describes two training parts, Set A (20,336 subjects) and Set B (20,000 subjects), with hourly time series and a SepsisLabel column. The target definition and its limitations must be described exactly from the dataset documentation; do not imply independent endpoint adjudication beyond what the source provides.

## 3. Prespecified research questions

- RQ1: Can the adaptive twin process synthetic longitudinal streams causally and deterministically while correctly handling missing, stale, invalid and out-of-order observations?
- RQ2: What are the computational and data-quality characteristics of the software pipeline under predeclared replay conditions?
- RQ3: How do the existing supervised models perform on the specified retrospective Challenge target, including calibration and alert-burden trade-offs?
- RQ4: Does the tested patient-relative physiology feature ablation improve the temporal baseline? Existing evidence is unfavorable; this question must be reported honestly, not reframed after results.

## 4. Cohort and target

- Dataset: PhysioNet/Computing in Cardiology Challenge 2019.
- Set A and Set B are parts of the Challenge training data, not a new independent external hospital cohort.
- Existing exact RC1 audit counts: Set A 20,336 patients / 790,215 rows; Set B 20,000 / 761,995 rows.
- Target: future entry into the Challenge `SepsisLabel`-positive window at 1, 3 and 6 hourly prediction horizons, as defined by the existing frozen workflow. Confirm the exact row-shift and censoring implementation from source before manuscript finalization.
- Explicitly state that this is a benchmark label target and not a prospectively observed deterioration event with an independently adjudicated onset time.
- No Set B data may be used for fitting, recalibration, threshold selection or model selection. Do not call Set B external clinical validation.

## 5. Analysis populations and split discipline

Before publication, reproduce the exact split manifest and confirm:
- patient-disjoint partitions;
- preprocessing fitted only on development/training partitions;
- calibration on its designated patient-disjoint Set A partition;
- threshold selection, if ever justified, on a separate patient-disjoint Set A partition;
- Set B retained only for the frozen evaluation described in the existing workflow;
- no patient overlap or preprocessing leakage across partitions;
- no silent cohort exclusions or post-hoc feature changes.

Any new analysis must use a new versioned protocol and code/configuration hash. Do not revise the RC1 result in place.

## 6. Outcomes and statistical reporting

### Retrospective prediction
Report, by horizon and seed:
- prevalence and number of patients/rows/events;
- AUROC and AUPRC with prevalence context;
- Brier score and log loss;
- calibration-in-the-large, calibration slope and reliability plots where estimable;
- sensitivity, specificity, PPV, NPV and confusion counts only at explicitly justified thresholds;
- alerts per patient-day and event-level lead time where the data support a defensible definition;
- patient-clustered uncertainty intervals;
- missingness and subgroup analyses with denominators and uncertainty.

Do not use row-level independent bootstrap resampling when rows are clustered within patients. Do not treat a low Brier score as proof of a useful operating point, particularly under severe class imbalance.

### Adaptive twin and synthetic engineering
Report the exact generator seed, scenario definitions, expected outcomes, software commit, schema version, hardware/host configuration, clock assumptions, and all observed failures. Report median/p95/max latency, frame loss, sequence gaps, CPU/memory and thermal observations. Do not translate synthetic deviations into clinical sensitivity/specificity.

## 7. Negative findings and current limitations

The tested patient-relative physiology ablation had worse Brier score than the temporal baseline in all nine horizon/seed comparisons in the exact RC1 evidence. This must be reported with the exact estimates and patient-cluster intervals copied from the retained aggregate artifact after re-verification.

No operating threshold has been selected because no independently approved alert-budget/utility objective exists. Do not invent one in the manuscript.

The adaptive twin's score is unitless and uncalibrated. It does not estimate sepsis probability or time-to-deterioration.

## 8. Reporting and risk-of-bias framework

- Use **TRIPOD+AI** as the reporting checklist for the prediction-model development/evaluation component. It supersedes TRIPOD 2015 for prediction models using regression or machine learning.
- Use **PROBAST+AI** as a structured risk-of-bias/applicability assessment for the prediction-model component; complete it with an independent reviewer.
- Use a software-engineering reproducibility checklist for the software component: source identity, dependency/environment lock, configuration, deterministic seeds, test results, data provenance, artifact manifest and reproduction instructions.
- Do not claim checklist compliance until every applicable item is completed and checked.

## 9. Manuscript structure

1. Title and structured abstract.
2. Introduction: longitudinal physiology, within-person reference context, research gap and cautious contribution statement.
3. Methods:
   - study design and data sources;
   - VITALIS software architecture;
   - observation schema and stream validation;
   - adaptive twin mathematics and parameter semantics;
   - synthetic replay design;
   - supervised benchmark models, target, splits and leakage controls;
   - metrics, uncertainty and calibration;
   - reproducibility, privacy and governance.
4. Results:
   - software and test coverage;
   - synthetic replay/bench performance;
   - cohort flow and provenance;
   - retrospective model performance and calibration;
   - negative ablation and threshold findings;
   - reproducibility audit.
5. Discussion:
   - what was demonstrated;
   - what was not demonstrated;
   - relation to prior work;
   - limitations and risks;
   - next independent-cohort and bench validation steps.
6. Conclusion: research software and retrospective benchmark evidence only.
7. Data/code availability, ethics/governance, funding, conflicts, author contributions and acknowledgements.

## 10. Claims policy

Permitted only when supported:
- “A research software framework was implemented.”
- “The exact candidate reproduced the specified aggregate benchmark under the frozen workflow.”
- “Synthetic tests demonstrated specified software behaviours.”
- “The tested patient-relative feature ablation did not improve the reported Brier score.”

Not permitted on current evidence:
- “Clinically validated,” “detects sepsis early,” “improves patient outcomes,” “medical-grade,” “real-time clinical monitoring,” “superior to standard care,” “patentable,” or “ready for hospitals.”
- “External validation” for Set B.
- Any claim that the unitless adaptive score is a risk probability.

## 11. External validation and prospective work

A genuinely independent cohort requires a different data source/population with documented governance, permissions, endpoint definitions, overlap checks, frozen model/configuration and a pre-specified analysis plan. Prospective silent-mode work requires institutional approvals and cannot influence care. These are future studies and are not part of the present manuscript unless completed.

## 12. Sources and reporting guidance

- PhysioNet/Computing in Cardiology Challenge 2019 dataset: https://www.physionet.org/content/challenge-2019/1.0.0/
- TRIPOD+AI statement (BMJ 2024): https://www.bmj.com/content/385/bmj-2023-078378
- PROBAST+AI (BMJ 2025): https://www.bmj.com/content/388/bmj-2024-082505

**Safety:** VITALIS remains research and education software. No patient connection or patient-care use is permitted by this protocol.
