# VITALIS reproducibility and independent review package

**Prepared:** 15 October 2026  
**Repository:** `culprit-k/VITALIS`  
**Working branch:** `work/strict-reproducibility-gate`  
**Purpose:** Give an independent reviewer a compact, privacy-safe route to assess the full-cohort reproduction and its limits.

## Current checkpoint — 17 October 2026

This section supersedes earlier statements below where run/commit status differs. The historical failure reports remain preserved; none has been overwritten.

- **Latest standard software CI:** [run #39020038010](https://github.com/culprit-k/VITALIS/actions/runs/39020038010) passed all 16 steps on main documentation commit `154a096bd1b9051b1c563af1c02993340d05e213`. Core code merge commit `4eb3d15c024b2a1d295f657c2cb96e7eb9ff16bd` passed 249 tests on [run #39018965402](https://github.com/culprit-k/VITALIS/actions/runs/39018965402).
- **Calibration diagnostics:** PR #19 added calibration intercept/slope point estimates. PR #21 added patient-cluster sandwich standard errors and asymptotic 95% intervals with explicit undefined statuses for non-identifiable fits. PR #22 added artifact-level checks for valid interval fields, Set B isolation and exclusion of row-level predictions; PR #23 extended those checks to all three declared models including the static baseline. Both workflow-guard PRs passed standard and dashboard CI 16/16 steps per run ([#39019540766](https://github.com/culprit-k/VITALIS/actions/runs/39019540766), [#39019558153](https://github.com/culprit-k/VITALIS/actions/runs/39019558153), [#39020467567](https://github.com/culprit-k/VITALIS/actions/runs/39020467567), [#39020476558](https://github.com/culprit-k/VITALIS/actions/runs/39020476558)).
- **Current code snapshot reproduction:** [full-cohort run #39019018791](https://github.com/culprit-k/VITALIS/actions/runs/39019018791) is running from temporary trigger-branch commit `424365d0823e58df4d5c6715149cbce26406dc2a`; the analysis source corresponds to code commit `4eb3d15c024b2a1d295f657c2cb96e7eb9ff16bd` including the calibration coefficient intervals. Spot-checking the run branch against current `main` confirmed identical blobs for `scripts/evaluate_physiological_features.py` (`c81bac5480c648a59744bed81bf5dac33fdec46f`), `src/vitalis/calibration_uncertainty.py` (`85c5e7992b018ba657bc4bffcfe8500d323d9000`), `scripts/evaluate_horizon_cross_cohort.py` (`891b84ad4a5da039f1dc38411211c503c971167c`), and `scripts/evaluate_set_a_platt_calibration.py` (`c4804c78e31e71cd7f45d2774d41fc62f6bdb5e6`). Checkout, CPU/backend preflight, pinned dependencies, source manifests, tests, cohort audits, fresh Set A/Set B caches, cache-integrity checks and the core nine-run horizon evaluation have passed. The patient-relative physiology ablation is active; Set A calibration, threshold sweep, artifact checks and frozen-baseline reconciliation are pending. Do not claim the current-snapshot reproduction passed until the workflow is complete and its artifact has been inspected.
- **Artifact guard limitation:** run #39019018791 began before PR #22's workflow guard was merged, so the new guard was not executed within that run. Manually verify the artifact schema and calibration intervals in addition to checking the strict reconciliation report. A later workflow run will enforce the merged guard automatically.
- **Research boundary:** Set B is another cohort from the same PhysioNet/CinC Challenge 2019 benchmark, not an external clinical cohort. No threshold, calibration, model or feature selection may use Set B. The Challenge target is entry into its `SepsisLabel`-positive window, not independently adjudicated biological sepsis onset. Calibration-coefficient intervals are conditional retrospective diagnostics, not prospective performance estimates.
- **Independent review remains outstanding:** no independent qualified reviewer sign-off is claimed. This package is ready for review but is not itself an external assessment. The review must cover the earlier five-metric mismatch reports, source/environment provenance, patient-disjoint splits, endpoint semantics, calibration/uncertainty, alert burden, privacy and release claims.


## Verification status update — 16 October 2026

- Python 3.11 clean-checkout full-cohort run [38843467722](https://github.com/culprit-k/VITALIS/actions/runs/38843467722) passed on exact source commit `62fe82e1dc1c8ea06fe8c8f74d495d935d8b8db7`. It rebuilt fresh Set A and Set B caches, passed cohort/cache audits, completed all nine horizon/seed evaluations, and reconciled **42/42 mean/sample-SD pairs and 84/84 scalar values with zero mismatches** under the unchanged six-decimal rule. The pre-reproduction test step passed **218 tests**. Aggregate-only artifact: [12022973310](https://github.com/culprit-k/VITALIS/actions/runs/38843467722/artifacts/12022973310).
- Python 3.13 diagnostic run [38843467715](https://github.com/culprit-k/VITALIS/actions/runs/38843467715) also completed successfully on the same source commit and matched **42/42 pairs, 84/84 scalars, zero mismatches** against the unchanged historical reference. Aggregate-only artifact: [12023100824](https://github.com/culprit-k/VITALIS/actions/runs/38843467715/artifacts/12023100824). This diagnostic workflow is not itself the acceptance gate.
- I compared the two retained aggregate JSON files: Set B test metrics and patient-warning metrics for all nine horizon/seed runs and both baseline models were identical between these Python 3.11 and Python 3.13 executions. This closes the same-source cross-runtime comparison for this pair of runs; it does not establish cross-hardware determinism or explain the earlier five mismatches.
- Mean temporal-model Set B metrics across seeds (research threshold 0.5): 1 h AUROC 0.656890, AUPRC 0.003170, Brier 0.131964, sensitivity 0.400798, PPV 0.003191, alerts per at-risk patient-day 1.4616, future-positive-window coverage 0.1172; 3 h AUROC 0.680004, AUPRC 0.012639, Brier 0.131344, sensitivity 0.415134, PPV 0.010771, alerts/day 1.2763, coverage 0.2934; 6 h AUROC 0.686375, AUPRC 0.026433, Brier 0.142186, sensitivity 0.445697, PPV 0.022373, alerts/day 1.2566, coverage 0.5680. The very low PPV and alert burden are important limitations; these results do not establish clinical utility.
- At the time of this update, the push-triggered extended-analysis run was still in progress. Its final status and results are recorded in the separate 16 October section above.
- Set A remains the model-development/calibration cohort and Set B remains evaluation-only. No raw cohort data, patient identifiers, caches, or row-level predictions are included in the retained artifacts. The historical baseline and six-decimal acceptance rule were not changed.

## Extended-analysis results and reproducibility discrepancy — 16 October 2026

The extended run [#38843462832](https://github.com/culprit-k/VITALIS/actions/runs/38843462832), on source commit `62fe82e1dc1c8ea06fe8c8f74d495d935d8b8db7`, completed both the predeclared physiology ablation and Set A calibration experiment and uploaded aggregate-only artifacts. However, its core baseline reconciliation **failed**: 37/42 mean/sample-SD pairs and 75/84 scalar values matched; five temporal-model metrics failed the six-decimal acceptance rule. This run must be retained as a failure, not relabeled as a pass. The passing core run [#38843467722](https://github.com/culprit-k/VITALIS/actions/runs/38843467722) and this failing extended run used the same source commit.

The numerical-backend diagnostics show a different runner/backend configuration: the failing extended run used an AMD EPYC 7763 host with OpenBLAS architecture dispatch `Haswell`; the successful run's recorded backend used an Intel Xeon Platinum 8573C host with OpenBLAS `SkylakeX`. This is a plausible contributor to numerical variation, not proof that CPU dispatch alone caused every mismatch. Do not change the acceptance rule or baseline to hide the discrepancy. The currently running core reproduction on the documentation commit must also be checked before the reproduction gate is considered robust.

### Fresh physiology-ablation result (extended run #38843462832)

| Horizon | Temporal baseline AUROC / AUPRC / Brier | Temporal + patient-relative physiology AUROC / AUPRC / Brier | Sensitivity baseline → candidate | PPV baseline → candidate |
|---:|---:|---:|---:|---:|
| 1 h | 0.656890 / 0.003170 / 0.131964 | 0.666282 / 0.003479 / 0.138077 | 0.400798 → 0.428364 | 0.003191 → 0.003248 |
| 3 h | 0.680004 / 0.012639 / 0.131345 | 0.689820 / 0.013419 / 0.135656 | 0.415134 → 0.440400 | 0.010771 → 0.011123 |
| 6 h | 0.686375 / 0.026433 / 0.142186 | 0.695591 / 0.027696 / 0.145114 | 0.445697 → 0.465526 | 0.022373 → 0.023065 |

Values are means across seeds. The candidate improves ranking and sensitivity modestly, but worsens Brier score at every horizon. PPV remains very low. Decision: **do not promote the physiology candidate as the best model**; probability quality and alert burden still need work.

### Fresh Set A calibration comparison (extended run #38843462832)

The experiment successfully used patient-disjoint Set A fit/calibration/unused-holdout partitions and kept Set B evaluation-only. It compared balanced and unweighted objectives for the temporal baseline and physiology model. Under the fixed 0.5 diagnostic threshold, Platt scaling often compresses probabilities so strongly that sensitivity is zero or nearly zero. The unweighted models already produce low Brier scores largely because predicted probabilities are tiny in this rare-label setting, while sensitivity at 0.5 is zero or nearly zero. Brier improvement alone therefore does **not** demonstrate useful calibration. The monotone Platt transform does not materially improve AUROC/AUPRC, and no Set B threshold tuning was performed.

Decision: **do not promote the Platt-calibrated outputs for alerts**. Next model experiment should use a predeclared, prevalence-aware objective and choose any candidate operating point using only patient-disjoint Set A validation, then freeze it before a single Set B evaluation. Report calibration intercept/slope, Brier, log loss, AUROC/AUPRC, sensitivity, PPV, alerts per at-risk patient-day, and patient-cluster uncertainty together.

These findings are retrospective research metrics against Challenge `SepsisLabel` window-entry targets, not clinical sepsis onset. Set B is not an external clinical validation cohort; no alert threshold here is clinically approved.

## Historical verification status update — 15 October 2026, 11:00 Uzbekistan time

- Python 3.13.5 clean-checkout run [38705107992](https://github.com/culprit-k/VITALIS/actions/runs/38705107992) completed successfully on the diagnostic workflow: all 42 mean/sample-SD pairs and 84 scalar values matched the preserved aggregate at six decimals; the cache-integrity audit and aggregate-only artifact upload passed. Artifact SHA-256: `6f910a4831d38d49ea1c78c7b460d67c046062a80f7768569bf23fcec55e4170`.
- A subsequent Python 3.13.5 run [38706807345](https://github.com/culprit-k/VITALIS/actions/runs/38706807345) is still in progress at the source-cohort download step. It is not counted as a pass yet.
- The corrected Python 3.11.17 workflow now checks out the exact source commit rather than a synthetic PR merge commit. At that time the Python 3.11 same-source result had not yet been verified. The 16 October update above supersedes that interim status.
- The immutable baseline and six-decimal acceptance rule remain unchanged. The successful Python 3.13 result does not by itself establish cross-runtime agreement or explain the earlier five temporal-metric discrepancies.
- Historical next-gate note (superseded): the exact-source Python 3.11.17 run and artifact were still awaited. The 16 October update above records the completed result. Independent review and extended-analysis interpretation remain outstanding.

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

The Python 3.11 workflow now explicitly checks out `github.event.pull_request.head.sha || github.sha` to avoid synthetic PR merge commits. Cross-runtime completion requires Python 3.11 and Python 3.13 runs to report the identical source commit SHA, both pass the predeclared aggregate comparison, and their metric outputs agree. The 16 October runs on commit `62fe82e1dc1c8ea06fe8c8f74d495d935d8b8db7` satisfy this same-source comparison for the retained aggregates. This does not establish cross-hardware determinism or explain the earlier discrepancy.

No model, threshold, seeds, horizons, metrics, baseline, or acceptance tolerance may be changed for this gate. Set B remains evaluation-only. No patient-level data or predictions may be published. This retrospective software reproduction is not clinical validation.


## Root-cause update — 16 October 2026 (supersedes interim Haswell hypothesis)

The retained passing and failing artifacts distinguish the kernel configurations. The successful reference run [#38843467722](https://github.com/culprit-k/VITALIS/actions/runs/38843467722) records Intel Xeon Platinum 8573C / OpenBLAS `SkylakeX` and passes 42/42 pairs, 84/84 scalars. The two repeated failures [#38855115107](https://github.com/culprit-k/VITALIS/actions/runs/38855115107) and [#38855119347](https://github.com/culprit-k/VITALIS/actions/runs/38855119347) use OpenBLAS `Haswell` and reproduce the same five mismatches. The strongest current explanation is CPU-kernel-dependent floating-point variation during temporal-model fitting that affects Brier score and threshold-based alert metrics.

The workflow now targets the reference `SkylakeX` kernel and fails early on hosts without AVX-512F, before downloading data. It verifies the actual loaded OpenBLAS architecture, not just the environment variable. This is an evidence-led root-cause mitigation, **not yet an accepted fix** until a clean Python 3.11 run on a compatible host passes the unchanged reconciliation and a repeat run also passes. The baseline and six-decimal acceptance rule remain immutable. If an AMD/non-AVX-512 host is assigned, the preflight failure is expected and no results from that host count toward the reproduction gate.


## First passing run with the matched numerical kernel — 16 October 2026

The first fresh Python 3.11 clean-checkout run with the historical OpenBLAS kernel passed the unchanged reconciliation: [workflow run #38857500125](https://github.com/culprit-k/VITALIS/actions/runs/38857500125), source commit `08f47f5613be539a2743f8629405cae52339ef16`. Results: 42/42 mean/sample-SD pairs, 84/84 scalar values, zero mismatches. Aggregate-only artifact: [12027304973](https://github.com/culprit-k/VITALIS/actions/runs/38857500125/artifacts/12027304973), SHA-256 `deaf2a49f1e3469bd2c4feaaeb186aff682e422ecf21063e2435ecfb94c99ec6`.

Its backend record confirms Python 3.11.17 / NumPy 2.3.5 / OpenBLAS 0.3.30, Intel Xeon Platinum 8573C, environment setting `OPENBLAS_CORETYPE=SkylakeX`, and loaded OpenBLAS architecture `SkylakeX`. Fresh source cohort audits, caches, cache-integrity audit, and all nine horizon-by-seed evaluations passed. The historical baseline, evaluator, fixed threshold, patient-disjoint split, seeds, horizons, tolerance, and evaluation-only Set B boundary were unchanged.

The root-cause mitigation is now supported by **two successful controlled clean-checkout Python 3.11 reproductions**, each passing 42/42 mean/sample-SD pairs and 84/84 scalar values with zero mismatches under the unchanged six-decimal rule. See runs [#38857500125](https://github.com/culprit-k/VITALIS/actions/runs/38857500125) and [#38857522352](https://github.com/culprit-k/VITALIS/actions/runs/38857522352). The follow-on workflow with the CPU guard placed before NumPy-based tests is still being verified; this is a workflow-safety check. If the assigned runner lacks SkylakeX-compatible AVX-512F, the expected safe outcome is an early preflight failure; do not relax the reference kernel or reconciliation rule.


## Repeatable baseline reproduction evidence — 16 October 2026

Both current clean-checkout Python 3.11 result artifacts independently pass the reference reconciliation with zero mismatches:

| Run | Source commit | Pairs / scalars | Result artifact |
|---|---|---:|---|
| [#38857500125](https://github.com/culprit-k/VITALIS/actions/runs/38857500125) | `08f47f5613be539a2743f8629405cae52339ef16` | 42/42, 84/84 | [Artifact 12027304973](https://github.com/culprit-k/VITALIS/actions/runs/38857500125/artifacts/12027304973) |
| [#38857522352](https://github.com/culprit-k/VITALIS/actions/runs/38857522352) | `af597e866fa1fa62bfe504807f534064d30ea58e` | 42/42, 84/84 | [Artifact 12028541322](https://github.com/culprit-k/VITALIS/actions/runs/38857522352/artifacts/12028541322) |

Both artifact diagnostics report Intel Xeon Platinum 8573C, OpenBLAS 0.3.30, `OPENBLAS_CORETYPE=SkylakeX`, and loaded architecture `SkylakeX`. Both also record matching ordered source-file fingerprints for official Set A and Set B. The first passing artifact digest is `deaf2a49f1e3469bd2c4feaaeb186aff682e422ecf21063e2435ecfb94c99ec6`; the second is `f18089da065bd6f01cc874752b0a09cc598a0a5113bc92da713301cc4e4f84e6`.

These repeat runs support CPU-kernel dispatch as the cause of the earlier discrepancies. No historical baseline, acceptance tolerance, model, feature matrix, seeds, horizons, split, threshold, or evaluation cohort changed to achieve these passes.
