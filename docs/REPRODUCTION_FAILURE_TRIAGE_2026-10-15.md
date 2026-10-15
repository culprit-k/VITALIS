# Reproduction failure triage — 15 October 2026

## Current observed state

Python 3.13 clean-checkout run #38702163220 on source commit `a445b2b38a045c7cb2b27ad99687912ac951b16d` produced 37/42 matching mean/sample-SD pairs (75/84 scalar values). The preserved baseline is unchanged. The five differences are temporal-model metrics at horizons 1 h and 3 h.

## Cross-runtime comparison after the pinned Python 3.11 pass

The retained artifact for pinned Python 3.11 run #38692360591 reports 42/42 mean/sample-SD pairs and 84/84 scalar matches. The retained Python 3.13 diagnostic artifact for run #38712336504 reports 37/42 pairs and 75/84 scalar matches. The two runs have the same audited cohort totals and predeclared protocol, but the Python 3.13 artifact has no counterpart Python 3.11 cache fingerprint from that passing run, so cache equality between those exact runs is not established.

Direct aggregate-output comparison shows small per-seed differences in temporal-model probabilities/metrics, with threshold-sensitive alert differences at 1 h and 3 h; even static-model Brier values differ at machine precision. This is consistent with numerical/runtime drift being a contributor, but it does **not** prove whether the cause is BLAS/runtime, feature matrix differences, or fit-path differences. Python 3.13 is diagnostic only; pinned Python 3.11 remains the declared acceptance gate.

Commit `798de0c420d8de3d9bd433a7cb1a40d192f5550a` adds privacy-safe per-run diagnostics to the aggregate evaluator: schema and selected-feature hashes, split/training-target hashes, imputer/scaler/model parameter hashes, convergence iterations, prediction-array hash, aggregate prediction moments, and fixed score-band counts around 0.5. It does not export patient identifiers, feature rows, or row-level predictions and does not alter the model, threshold, seeds, horizons, or acceptance rule.

The new diagnostics must be reviewed from a fresh pinned Python 3.11 run and a matching Python 3.13 diagnostic run. Compare fingerprints only within the same source revision and matching cohort/cache construction; do not infer cache equivalence from cohort totals alone.

## Highest-value next experiment

The Python 3.11 workflow already invokes `scripts/audit_reproduction_cache.py`; the Python 3.13 diagnostic workflow does not. Add that exact cache-integrity audit step after both fresh cache builds and before evaluation, and include its aggregate-only JSON in the retained artifact. This is a diagnostic-only workflow change: it must not change feature construction, model fitting, threshold, seed, metric, baseline, or acceptance tolerance.

Compare the resulting Set A and Set B audit fields with the earlier passing Python 3.11 artifact and any retained historical metadata. Cache audit output must not contain patient IDs, raw records, row-level predictions, or cache arrays.

## Next diagnostic if cache fingerprints match

Instrument the evaluator to emit aggregate-only per-horizon/per-seed/per-model diagnostics:
- train and unused-holdout patient counts and target counts;
- ordered feature-schema hash and selected feature-index hash;
- imputer/scaler/model convergence status and coefficient-vector hash;
- aggregate prediction moments and counts in predeclared score bands around 0.5;
- confusion counts and aggregate alarm/refractory/window summaries.

No patient-level predictions or identifiers may be exported. Set B remains evaluation-only; these diagnostics must not be used to tune the model or threshold.

## Decision rules

1. If cache/schema fingerprints differ, investigate cache construction/order before model code.
2. If cache fingerprints match but split or coefficient hashes differ, investigate split ordering and dependency/runtime effects.
3. If probabilities differ while fitted model summaries match, inspect prediction chunking and preprocessing behavior.
4. If probabilities match but alert metrics differ, test the temporal alarm/refractory/window summary implementation against small synthetic fixtures.
5. If the historical local run cannot be reconstructed, preserve it as historical evidence and request independent review of a separately versioned replacement baseline. Do not silently replace the baseline.

The acceptance rule in `docs/HORIZON_RECONCILIATION_ACCEPTANCE_RULE.md` remains unchanged. VITALIS remains research-only and is not clinically validated.
