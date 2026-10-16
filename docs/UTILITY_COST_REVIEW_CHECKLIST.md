# Independent review checklist: VITALIS utility operating points

**Purpose:** structured review of the retrospective cost-sensitivity framework before anyone discusses a frozen alert policy. This checklist is not a substitute for a qualified independent review, ethics/governance approval, or prospective validation.

## Reviewer record

- Reviewer name and role:
- Clinical/statistical expertise relevant to ICU early-warning models:
- Institution / affiliation:
- Date:
- Conflicts of interest or prior involvement with VITALIS:
- Documents and commit SHA reviewed:

## 1. Target and label semantics

- [ ] Confirm that the target means future entry into the PhysioNet/CinC Challenge 2019 `SepsisLabel`-positive window, not independently observed sepsis onset.
- [ ] Confirm the six-hour lead convention is not being applied a second time.
- [ ] Assess whether a future-positive *window* is a meaningful unit for the intended research question, including how overlapping or adjacent positive windows are defined.
- [ ] Identify label noise, censoring, and timing assumptions that could distort missed-window counts.

Reviewer notes:

## 2. Split integrity and selection discipline

- [ ] Verify that training, Platt calibration, and operating-point development holdout are patient-disjoint within Set A.
- [ ] Verify preprocessing and model fitting use training patients only and calibration is fit only on the calibration partition.
- [ ] Verify cost ranking uses only the Set-A development holdout.
- [ ] Confirm Set B has not been used for threshold or cost-ratio selection and must not be reused for tuning after results have been inspected.
- [ ] Recommend a defensible protocol for a new independent evaluation cohort after a policy is frozen.

Reviewer notes:

## 3. Utility definition and cost assumptions

The current proxy is:

`weighted_cost = missed_window_cost × uncovered_future_positive_windows + alert_cost × all_alerts`

`weighted_cost_per_patient_day = weighted_cost / eligible_at_risk_patient_days`

- [ ] Assess whether charging every alert—including alerts within a target-positive window—is appropriate for the research question.
- [ ] Decide whether the cost unit should represent staff attention, alarm review, or another explicitly defined resource. Do not treat an abstract unit as money or clinical harm.
- [ ] Provide a defensible source or elicitation process for the relative cost of a missed forecast-positive window versus one alert.
- [ ] Consider a sensitivity range broad enough to show when candidate rankings change. Explain why the range is credible; do not select a ratio because it favors one model.
- [ ] Identify omitted effects: alarm fatigue, staffing capacity, treatment harms, delayed treatment, patient preferences, competing outcomes, and the consequences of false reassurance.
- [ ] State whether the utility score should remain a descriptive development aid or whether a different decision-analytic method is needed.

Reviewer notes:

## 4. Metrics and interpretation

- [ ] Interpret row-level sensitivity and PPV separately from patient-level alert burden and forecast-window coverage.
- [ ] Assess whether alerts per at-risk patient-day is the right burden denominator and whether any alternative denominators are required.
- [ ] Assess the six-hour refractory interval and whether it should be fixed before development or varied in a predeclared sensitivity analysis.
- [ ] Confirm that alerts outside forecast-positive windows are not labelled clinical false alarms without adjudicated event data.
- [ ] Review calibration limitations and the possibility that class weighting plus Platt recalibration still yields inadequate absolute risk estimates.
- [ ] Review uncertainty reporting. The current utility ranking is deterministic conditional on each split and cost assumption; ancillary 20-replicate bootstrap summaries are preliminary and are not uncertainty intervals for utility ranking.

Reviewer notes:

## 5. Evidence and governance

- [ ] Confirm the clean-checkout/source-provenance gate is addressed before describing the full-cohort results as exact-source reproduction.
- [ ] Confirm the aggregate artifact contains no patient identifiers, row-level predictions, raw records, or local caches.
- [ ] Define minimum evidence required before prospective silent-mode evaluation, including protocol preregistration, data governance, monitoring, and stopping rules.
- [ ] Confirm that no current result supports clinical deployment or patient-care use.

## Reviewer conclusion

- [ ] Accept the utility proxy for continued **exploratory research only**.
- [ ] Revise the utility definition or assumptions before further analysis.
- [ ] Do not proceed to policy selection until cost assumptions and label semantics are resolved.
- [ ] Additional requirements:

**Conclusion and rationale:**

**Required changes / evidence:**

**Reviewer sign-off:**

---

## Non-negotiable boundary

This review can support a research protocol decision only. It cannot establish clinical validity, clinical utility, patient benefit, or readiness for diagnosis, triage, treatment, or patient-care decisions. Any future policy must be frozen before evaluation on a new independent cohort. VITALIS remains research-only.
