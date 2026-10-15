# Targeted root-cause narrowing: five temporal reproduction discrepancies

Date: 15 October 2026
Status: **Root cause not yet proven; one proposed cause has been narrowed.**

## Objective

Investigate the five mismatches against the immutable aggregate in `results/horizon_cross_cohort_2026-10-14.json`. The acceptance rule in `docs/HORIZON_RECONCILIATION_ACCEPTANCE_RULE.md` remains unchanged.

## New code-history evidence

The historical result records bootstrap optimization commit `3b3dca5f32f96b34c80ab743409c72f75e878596`. The GitHub commit diff for that change modifies `patient_cluster_bootstrap_horizon_alerts` in `src/vitalis/horizon.py`: it replaces the Python-loop implementation of patient-cluster percentile intervals with vectorized resampling of precomputed per-patient sufficient statistics.

That function computes uncertainty intervals. It is separate from the point-metric path in `evaluate_horizon_alerts`, and it initializes its own local random generator with `np.random.default_rng(seed)`. Therefore, **the bootstrap vectorization change alone cannot explain differences in the reported across-seed point estimates for specificity, Brier score, alert rate, or future-positive-window coverage**. It may affect interval endpoints, but those are not the five failed baseline mean/SD pairs.

This narrows one hypothesis; it does not identify the root cause.

## What the evidence currently supports

- The historical baseline was produced from a reconstructed local execution, not a verified full Git checkout. Its provenance notes that the optimized patient-cluster bootstrap was used.
- The checked-in evaluator blob SHA recorded in the historical output matches the current evaluator file's Git blob SHA. This metadata does not prove the historical process executed that exact byte sequence.
- A Python 3.11 clean-checkout workflow produced the five reported failures; a Python 3.13 diagnostic also showed them, so Python minor version alone is not a sufficient explanation.
- The source cohort archive hash and aggregate cohort counts match the recorded historical values, but this does not prove feature-cache values, feature ordering, patient-row ordering, or fitted predictions were identical.
- The historical aggregate does not retain enough per-seed values to compare every failed metric seed-by-seed. Do not manufacture missing per-seed evidence.

## Next diagnostic sequence

1. **Verify the feature-cache builder and feature matrix contract.** In a clean run, capture the 109-column ordered schema hash, each cohort's cache-builder Git blob SHA, row/patient counts, per-patient row-order checks, and aggregate-only feature/cache fingerprints. Keep source files, caches, patient IDs, and row-level diagnostics on ephemeral/private storage.
2. **Verify the split and fit path.** Record the train/holdout patient counts per seed, split index hashes that do not expose patient IDs, class counts, selected feature indices, preprocessing parameters, convergence status, and aggregate coefficient/prediction summaries. Do not export patient-level predictions.
3. **Target the threshold-sensitive outputs.** For the temporal model at 1 h and 3 h, report aggregate counts of scores in narrow, predeclared bands around 0.5, and verify the exact patient-time ordering, fixed threshold comparison (`>= 0.5`), and six-hour refractory implementation. This is diagnostic only; do not change the threshold.
4. **Separate probability and alarm discrepancies.** If Brier differs while AUROC/AUPRC round identically, compare aggregate probability-distribution moments and fit/preprocessing manifests first. If alert rates/coverage differ, compare threshold-crossing and per-patient refractory-summary aggregates. Never upload row-level scores.
5. **If the historical run cannot be reconstructed**, do not overwrite it or call the discrepancy fixed. Preserve the historical baseline, the clean-checkout result, and a separately versioned replacement-baseline proposal for independent statistical review.

## Explicit non-actions

- No baseline, threshold, seed, horizon, model, metric, or six-decimal acceptance rule was changed.
- Set B remains evaluation-only.
- No model or evaluation code was changed in this diagnostic note.
- No raw patient data, caches, identifiers, or row-level predictions are committed.
- Step 2 remains **not accepted** until evidence explains the discrepancies or an independently reviewed replacement-baseline decision is approved.

## New evidence: pinned clean-checkout run

The full-cohort workflow on commit `627b0d5b0f06f6d178a16e2d38f8b6f21c141160` completed successfully on 15 October 2026 (run [38692360591](https://github.com/culprit-k/VITALIS/actions/runs/38692360591)). Under the workflow's pinned Python 3.11 environment and fresh feature caches, the predeclared reconciliation reported **42/42 mean/sample-SD pairs matched**, **84/84 scalar values matched**, and **zero mismatches** after rounding to six decimals. The cache-integrity audit also passed: both cohorts had the expected patient/row/positive-label counts, 109 features, contiguous patient blocks, and patient block lengths consistent with metadata.

This is strong evidence that the five discrepancies are **not reproduced by the current pinned clean-checkout workflow**. It is not sufficient to claim the historical cause is definitively identified: the prior failing Python 3.11 run's exact dependency set and execution artifacts must be compared against this passing run. The preserved 14 October baseline remains unchanged. The current workflow is being updated to retain the cache audit JSON as an aggregate-only artifact so reviewers can inspect the fingerprints without access to patient-level material.

## Current status and next action

- Current pinned clean-checkout acceptance result: **PASS (42/42 pairs)**.
- Historical cause of the earlier failures: **not yet proven**; dependency/environment drift is a leading hypothesis, not a confirmed explanation.
- Historical baseline: unchanged.
- Set B: evaluation-only.
- Next: retain and inspect the passing run's cache/environment fingerprints, compare the earlier run's available environment logs, then require a second fresh pinned run on the updated workflow before declaring the reproduction gate stable.
