# Temporal-model reproduction discrepancy audit — 15 October 2026

## Status

**Open investigation; Step 2 is not accepted.** This note records the first dependency-pinned clean-checkout run and the next diagnostic actions. It does not change the baseline, tolerance, models, or evaluation protocol.

## Evidence inspected

- Repository: `culprit-k/VITALIS`
- Evaluated commit: `c20ed448ab3fbcfc6e6e35c73dd8b28a26950184`
- Workflow: https://github.com/culprit-k/VITALIS/actions/runs/38679761894
- Aggregate-only artifact: https://github.com/culprit-k/VITALIS/actions/runs/38679761894/artifacts/11948141410
- Downloaded artifact SHA-256: `480f3a18f2f35413984efa6d8be8bde3e44eb987554caacfa60cd57a2312cd1d`
- Runtime: Python 3.11.17, GitHub-hosted Ubuntu x86_64.
- Key packages: NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, SciPy 1.17.0, joblib 1.5.3, threadpoolctl 3.6.0.
- The artifact's pre-evaluation manifest reports a clean working tree and matching Git blob IDs for all required source files.
- The run completed the official cohort audits, fresh feature-cache builds, all nine horizon/seed combinations, 18 model evaluations, aggregate-only output validation, and artifact upload.

The workflow output contains no raw cohort rows, caches, patient identifiers, or row-level predictions. Set B was evaluation-only.

## Acceptance result

The predeclared rule requires exact agreement after rounding every aggregate mean and sample standard deviation to six decimal places. Result: **37/42 mean–SD pairs matched; 75/84 scalar values matched; five pairs failed.**

| Horizon | Temporal metric | Fresh mean | Baseline mean | Fresh sample SD | Baseline SD |
|---:|---|---:|---:|---:|---:|
| 1 h | Specificity | 0.8424054169 | 0.842405 | 0.0146516690 | 0.014651 |
| 1 h | Alerts / at-risk patient-day | 1.4615822611 | 1.461593 | 0.1132623320 | 0.113243 |
| 3 h | Brier score | 0.1313454415 | 0.131344 | 0.0034725607 | 0.003472 |
| 3 h | Alerts / at-risk patient-day | 1.2762744951 | 1.276286 | 0.0807039708 | 0.080706 |
| 3 h | Future-positive-window coverage | 0.2937976061 | 0.293435 | 0.0151169140 | 0.014854 |

The discrepancies are small in absolute magnitude but are failures under the existing rule. The baseline remains immutable. The preserved baseline does retain per-seed AUROC, AUPRC, Brier score, alert-rate, and coverage values (rounded to six decimals), but it does not retain per-seed specificity/sensitivity or the full per-seed probability outputs. Seed-level comparison is therefore possible for some metrics, not for every discrepancy.

## Interpretation: facts versus hypotheses

### Established facts

1. The pinned clean-checkout pipeline executes successfully through the full cohort experiment.
2. The declared cohort totals and target-eligible row counts agree with the preserved baseline.
3. All five aggregate discrepancies involve the temporal model; they affect one fixed-threshold specificity SD, two alert-burden summaries, one Brier summary, and one forecast-window coverage summary.
4. The earlier historical run used a reconstructed local evaluator and an optimized patient-cluster bootstrap. Its execution provenance differs from the clean-checkout workflow.
5. The available evidence does **not** identify a proven root cause.

### Hypotheses to test, not conclusions

- Differences in cache contents, feature-column ordering, imputation/scaling inputs, or temporal-feature construction between the historical reconstruction and checked-in source.
- Differences in the patient-disjoint training split or fitted temporal-model coefficients/probabilities.
- Numerical-path or convergence differences between environments.
- Sensitivity of thresholded alert counts and forecast-window coverage to predictions near the fixed threshold and to refractory-window behavior.

Do not attribute the issue to any one hypothesis without evidence.

## Required diagnostic sequence

1. **Repeat the exact pinned run** at the same source commit and environment. Compare aggregate outputs and SHA-256 hashes. Identical results would support determinism of the current pinned pipeline; it would not by itself explain the historical baseline discrepancy.
2. **Compare current-run seed-level metrics** between repeated pinned executions. The historical baseline does not preserve seed-level metrics, so do not imply a historical per-seed comparison is possible.
3. **Audit feature/cache provenance**: verify 109-column schema, exact column order, cache builder blob, cohort source fingerprint, per-patient row ordering, and target-eligible counts. Keep any row-level data and cache fingerprints private where required.
4. **Audit model fitting**: compare split indices/seed semantics, preprocessing fit scope, convergence warnings, fitted coefficients and prediction summaries using privacy-safe aggregate diagnostics. Do not export patient-level predictions.
5. **Audit alert metrics** separately from probability metrics: verify fixed threshold, six-hour refractory policy, per-patient time indices, ordering, and definitions of positive windows.
6. If the old execution cannot be reconstructed because required provenance is absent, preserve both outputs and request independent statistical review of a **separately versioned replacement baseline**. Keep the old baseline unchanged and document the decision; never loosen tolerance post hoc.

## Guardrails

- Keep Set B evaluation-only: no feature selection, calibration, threshold tuning, model selection, or policy tuning from its outcomes.
- Do not change the predeclared six-decimal rule to obtain a pass.
- Do not commit raw patient data, caches, identifiers, or row-level predictions.
- Do not claim clinical validation or biological sepsis-onset prediction.
- Keep the PR draft/unmerged pending resolution and independent review.

## Exit criteria

Step 2 may be accepted only after the repeat run and discrepancy investigation are documented, the declared acceptance process is satisfied or a separately reviewed replacement-baseline decision is approved, and an independent reviewer signs off. This is computational reproducibility only; independent clinical/statistical review, governance/ethics determination, and a genuinely new external cohort remain separate gates.


## Follow-up: partial seed-level comparison

The preserved JSON contains rounded per-seed summaries for some metrics, so these can be compared directly without accessing patient-level predictions. On the first clean-checkout run, the following temporal-model differences are visible in the stored per-seed summaries:

| Horizon | Seed | Metric | Fresh clean-checkout | Preserved per-seed summary |
|---:|---:|---|---:|---:|
| 1 h | 42 | Alerts / at-risk patient-day | 1.330859 | 1.330892 |
| 3 h | 2026 | Brier score | 0.132716 | 0.132712 |
| 3 h | 2026 | Alerts / at-risk patient-day | 1.285430 | 1.285465 |
| 3 h | 2026 | Future-positive-window coverage | 0.301415 | 0.300326 |

These are descriptive comparisons of rounded stored summaries. The 3-hour/seed-2026 coverage difference is larger than the other listed differences and deserves targeted investigation of predictions near the fixed 0.5 threshold and the six-hour refractory rule. Small Brier-score differences alongside matching AUROC/AUPRC to six decimals are consistent with a numerical-path hypothesis, but do not prove it. Do not infer an exact number of changed alerts or windows without the source-run outputs needed to establish that.

A same-commit, same-pinned-environment repeatability check completed on 15 October 2026. The aggregate-only artifacts from attempts 1 and 2 of workflow run `38679761894` (artifact IDs `11948141410` and `11949006910`) have byte-identical reconciliation JSON (SHA-256 `04c1b12ae9385dd04ade591503504715862a0c2f2c0407e792c725715f1a05a8`). The full result JSON differs only in fit-time/runtime fields; all 18 model fits' reported evaluation metrics, warning metrics, bootstrap intervals, row counts, and cohort counts are identical. This establishes repeatability of the current clean-checkout metric outputs under the pinned Python 3.11.17 environment. Both artifacts are retained in the GitHub Actions run.


## Confirmed repeatability finding

**The same five baseline discrepancies recur exactly in the second clean-checkout attempt.** The reconciliation outputs from attempts 1 and 2 are byte-identical and both report 37/42 mean–SD pairs matching and 75/84 scalar comparisons matching. This rules out a one-off nondeterministic rerun as the explanation for those five discrepancies.

The current checkout's evaluation outputs are repeatable under the pinned environment. The unresolved difference is specifically between those repeatable outputs and the historical baseline. The baseline's own provenance note says its evaluator was reconstructed locally and was not byte-identically verified against the checked-in evaluator. Therefore, the most defensible current explanation is a baseline provenance/implementation mismatch, potentially compounded by numerical differences in the threshold-sensitive temporal model. The available aggregate artifacts cannot prove which historical code or numerical detail caused each mismatch.

No acceptance criteria or baseline values have been changed. Do not label historical-baseline reconciliation as passed. A resolution requires a reviewed decision on the non-byte-verified historical reference or a recoverable, source- and environment-identical historical execution—not tuning the current implementation until it matches rounded numbers.
