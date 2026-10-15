# VITALIS reproducibility and independent review package

**Prepared:** 15 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Working branch:** `work/strict-reproducibility-gate`  
**Purpose:** Give an independent reviewer a compact, privacy-safe route to assess the full-cohort reproduction and its limits.

## Verification status update — 15 October 2026, 11:00 Uzbekistan time

- Python 3.13.5 clean-checkout run [38705107992](https://github.com/culprit-k/VITALIS/actions/runs/38705107992) completed successfully on the diagnostic workflow: all 42 mean/sample-SD pairs and 84 scalar values matched the preserved aggregate at six decimals; the cache-integrity audit and aggregate-only artifact upload passed. Artifact SHA-256: `6f910a4831d38d49ea1c78c7b460d67c046062a80f7768569bf23fcec55e4170`.
- A subsequent Python 3.13.5 run [38706807345](https://github.com/culprit-k/VITALIS/actions/runs/38706807345) is still in progress at the source-cohort download step. It is not counted as a pass yet.
- The corrected Python 3.11.17 workflow now checks out the exact source commit rather than a synthetic PR merge commit. The Python 3.11 same-source result for the current head has **not been verified from available run evidence**. Do not close Stage 2 until its current-head run and retained reconciliation artifact are inspected.
- The immutable baseline and six-decimal acceptance rule remain unchanged. The successful Python 3.13 result does not by itself establish cross-runtime agreement or explain the earlier five temporal-metric discrepancies.
- Next gate: verify the exact current-head Python 3.11.17 run, confirm the 42/42 + 84/84 result and cache audit, and confirm artifact privacy. If the Python 3.11 run fails, preserve the failure and investigate rather than changing the protocol. Stage 3 physiological-algorithm comparisons remain blocked until this gate and independent review are complete.

## Executive status

- The initial clean-checkout full-cohort run [38692360591](https://github.com/culprit-k/VITALIS/actions/runs/38692360591), at commit `627b0d5b0f06f6d178a16e2d38f8b6f21c141160`, passed the predeclared aggregate reconciliation: **42/42 mean/sample-SD pairs and 84/84 scalar values matched** after rounding to six decimal places; its fresh cache-integrity audit passed for both cohorts.
- A second clean-checkout run [38695459518](https://github.com/culprit-k/VITALIS/actions/runs/38695459518), at commit `a3b7ab933931a231406b7abbfda305dfdaa3236c`, also passed: **42/42 pairs, 84/84 scalar values, zero mismatches**, fresh cache audit passed, and the aggregate/provenance artifact uploaded successfully.
- The second run's pre-reproduction test step passed **193 tests**. The separate tests workflow on commit `a3b7ab933931a231406b7abbfda305dfdaa3236c` also passed: [run 38695459400](https://github.com/culprit-k/VITALIS/actions/runs/38695459400).
- These are two successful runs, but the second run is a repeatability check on the updated workflow, not proof that the historical five-mismatch root cause is known.
- The five mismatches in the earlier run remain unexplained at root-cause level. Environment/dependency drift is plausible, not proven.
- The preserved historical aggregate `results/horizon_cross_cohort_2026-10-14.json` is immutable for this investigation. No thresholds, seeds, horizons, metrics, or acceptance tolerances were changed to achieve the pass.

## Reproduction protocol

| Item | Locked setting |
|---|---|
| Source data | Official PhysioNet/CinC Challenge 2019 training Set A and Set B |
| Set A | 20,336 patients; 790,215 hourly rows; 17,136 positive Challenge labels |
| Set B | 20,000 patients; 761,995 hourly rows; 10,780 positive Challenge labels |
| Feature matrix | 109 features |
| Horizons | 1, 3, and 6 hours |
| Seeds | 42, 123, and 2026 |
| Models | Static and temporal logistic-regression baselines |
| Train/holdout split | Patient-disjoint 60% train / 40% unused holdout on Set A |
| Evaluation cohort | All eligible Set B patients; evaluation-only |
| Alert threshold | 0.5, fixed before evaluation |
| Refractory interval | 6 hours |
| Cluster bootstrap | 200 patient-level replicates |
| Environment | Python 3.11.17 with pins in `constraints/reproduction-py311.txt`; BLAS/OpenMP threads fixed to one |
| Acceptance | Each mean and sample SD must match the preserved baseline after rounding to six decimal places |
| Metrics | AUROC, AUPRC, Brier score, sensitivity, specificity, alerts per at-risk patient-day, future-positive-window coverage |

The target is entry into the Challenge `SepsisLabel`-positive window, not independently observed biological sepsis onset. Set B is a second Challenge training cohort and is **not** a prospective or independent clinical validation cohort.

## Evidence to retain and inspect

1. **Exact source revision:** record the tested commit SHA and verify source manifests.
2. **Environment:** inspect the retained `vitalis-pip-freeze.txt`, Python version, package-pin check, and pre-/pre-evaluation source manifests in the GitHub Actions artifact.
3. **Cohort audit:** verify the aggregate patient, row, label, schema, and ordered source-file fingerprints.
4. **Cache integrity:** inspect `vitalis-cache-integrity-audit.json` for the 109-feature schema hash, ordered file-list fingerprints, hashes of the aggregate cache arrays, finite-value counts, feature-summary hashes, and patient-block checks.
5. **Evaluation and reconciliation:** inspect `horizon_cross_cohort_clean_checkout.json`, `vitalis-reconciliation.json`, and the concise Markdown report.
6. **Privacy check:** confirm the artifact contains no raw PSV source files, feature caches, patient identifiers, or row-level predictions.

The aggregate cache hashes are fingerprints, not a substitute for a historical cache fingerprint. Since the historical run did not retain an equivalent verified cache manifest, the current audit cannot prove byte-for-byte identity with that historical cache.

## Independent reviewer checklist

Please record each item as **Pass**, **Fail**, or **Not assessable**, with a short rationale and a reference to the evidence.

- [ ] The commit SHA, source manifests, and environment are unambiguous.
- [ ] Both cohort counts and source-label audits agree with the protocol.
- [ ] Feature construction and the ordered 109-feature schema are reviewed.
- [ ] Patient-disjoint split semantics are verified; no patient crosses train/holdout.
- [ ] Set B is used only for final evaluation, not fitting, calibration, feature selection, model selection, or threshold selection.
- [ ] Horizon target construction does not use future information beyond the explicitly defined target label.
- [ ] Metrics, patient-level alert counting, refractory handling, and patient-cluster uncertainty calculations are independently checked.
- [ ] The 42 mean/SD comparisons use the predeclared six-decimal acceptance rule without exceptions.
- [ ] The retained artifacts contain aggregate results only and no prohibited patient-level data.
- [ ] The earlier five mismatches are addressed honestly; no unsupported root-cause claim is made.
- [ ] Limitations are clear: Challenge-label target, retrospective data, no external clinical validation, and no claim of clinical utility.
- [x] A second clean run on the updated workflow completed and passed: [run 38695459518](https://github.com/culprit-k/VITALIS/actions/runs/38695459518).

## Questions the review must answer

1. Can the reviewer reproduce the aggregate report from the exact source commit and pinned environment?
2. Are the split, label horizon, and alert metrics implemented as described?
3. Is the initial 42/42 pass repeatable on the updated workflow?
4. What evidence, if any, identifies the root cause of the earlier five mismatches? If not identifiable, state that explicitly.
5. Are any protocol, documentation, privacy, or statistical issues unresolved before this reproduction milestone is accepted?

## Decision rule

Two clean-checkout runs now pass the predeclared aggregate reconciliation, including a repeat on the updated workflow. Final independent acceptance still requires review of the retained evidence and a written reviewer disposition. If the historical discrepancy cannot be explained, preserve both records and document the uncertainty; do not rewrite the historical baseline to fit the new run.

## Clinical and engineering boundary

This is a retrospective software-reproducibility exercise. It does not establish safe alarm settings, prospective clinical performance, clinical utility, or readiness for hardware integration. External validation and a separately reviewed clinical-risk plan are prerequisites before making clinical claims or translating the model into a medical device.

## Same-source cross-runtime gate — 15 October 2026

Python 3.13 run [#38705107992](https://github.com/culprit-k/VITALIS/actions/runs/38705107992) passed the unchanged reconciliation rule: 42/42 mean–sample-SD pairs and 84/84 scalar values matched; the privacy-safe cache-integrity audit also passed. The result is attached as aggregate-only artifact [11958357679](https://github.com/culprit-k/VITALIS/actions/runs/38705107992/artifacts/11958357679).

The Python 3.11 workflow now explicitly checks out `github.event.pull_request.head.sha || github.sha` to avoid synthetic PR merge commits. Cross-runtime completion requires Python 3.11 and Python 3.13 runs to report the identical source commit SHA, both pass the same predeclared acceptance rule, and their aggregate metric outputs agree. The Python 3.11 run has not yet been verified; do not mark this gate closed until that evidence is recorded.

No model, threshold, seeds, horizons, metrics, baseline, or acceptance tolerance may be changed for this gate. Set B remains evaluation-only. No patient-level data or predictions may be published. This retrospective software reproduction is not clinical validation.
