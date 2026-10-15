# Reproduction failure triage — 15 October 2026

## Current observed state

Python 3.13 clean-checkout run #38702163220 on source commit `a445b2b38a045c7cb2b27ad99687912ac951b16d` produced 37/42 matching mean/sample-SD pairs (75/84 scalar values). The preserved baseline is unchanged. The five differences are temporal-model metrics at horizons 1 h and 3 h.

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
