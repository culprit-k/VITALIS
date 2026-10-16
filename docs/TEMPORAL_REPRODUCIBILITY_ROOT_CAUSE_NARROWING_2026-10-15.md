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

## Latest pinned Python 3.13 clean-checkout run — 15 October 2026

Run [38702163220](https://github.com/culprit-k/VITALIS/actions/runs/38702163220) completed with reconciliation **FAIL** on exact source commit `a445b2b38a045c7cb2b27ad99687912ac951b16d`, Python 3.13.5, and the pinned environment. The retained aggregate-only artifact is [11957298608](https://github.com/culprit-k/VITALIS/actions/runs/38702163220/artifacts/11957298608), ZIP SHA-256 `8d8635345592516051218c35ad94e72aa8eb501042d4eb04e43ba7dc80c57670`.

The fixed six-decimal gate reported 37/42 mean–SD pairs and 75/84 scalar values matching, with these five temporal-model discrepancies:
- 1-hour specificity: mean rounds identically, sample SD does not (`0.0146516690` vs baseline `0.014651`).
- 1-hour alerts per at-risk patient-day: fresh mean `1.461582`, SD `0.113262`; baseline `1.461593`, `0.113243`.
- 3-hour Brier score: fresh mean `0.131345`, SD `0.003473`; baseline `0.131344`, `0.003472`.
- 3-hour alerts per at-risk patient-day: fresh mean `1.276274`, SD `0.080704`; baseline `1.276286`, `0.080706`.
- 3-hour future-positive-window coverage: fresh mean `0.293798`, SD `0.015117`; baseline `0.293435`, `0.014854`.

The source manifest verified a clean checkout and exact Git blob matches for the evaluator (`891b84ad4a5da039f1dc38411211c503c971167c`), horizon implementation (`7d275dfb23ec86be25bdca26b9c30fc639887630`), and other manifest-listed files. The cache-builder blob also matches the historical result's recorded SHA `eba7dda1532675c2e3f21476b0bba2cead537e78`. The cohort source audit passed expected patient, row, and positive-label totals. These checks narrow the cause but do not prove that the historical local reconstruction used identical feature values, patient ordering, split membership, fit inputs, or temporal alarm summaries.

**Updated disposition:** the earlier successful run on another commit does not close the gate; this newer Python 3.13 run fails. Do not label the gate passed, alter the six-decimal rule, overwrite the 14 October baseline, or tune against Set B. The next diagnostic must add aggregate-only cache/schema fingerprints and split/fit/alarm summaries to a fresh run, then compare them with any available historical evidence. If the historical execution cannot be reconstructed, propose a separately versioned replacement baseline for independent review rather than pretending the discrepancy is fixed. Set B remains evaluation-only and no row-level output may be uploaded.
