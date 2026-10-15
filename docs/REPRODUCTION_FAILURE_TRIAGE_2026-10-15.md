# Reproduction failure triage — 15 October 2026

## Latest evidence update — run #38714974286

The latest clean-checkout Python 3.13 diagnostic on source commit `3cec7115cb030c67c11a1b28f8baea1f901ba0b5` completed successfully and reports **42/42 mean/sample-SD pairs and 84/84 scalar values matching** the preserved baseline under the unchanged six-decimal diagnostic comparison. The run is diagnostic-only and is not the pinned Python 3.11 acceptance gate.

The retained artifact includes `vitalis-cache-integrity-audit.json`. Both cohort audits passed and report the expected totals and 109 features. Privacy-safe cache fingerprints:
- Set A schema SHA-256: `980504b21cc0b14cf20ef3c3374d9d51de82691c13b1cbc82246fc9904a366dc`
- Set A X/y/group array SHA-256: `9f9379097b68581c9fdf7806a6b4dcb95e3a6e358b8fcefe0306845acf11c3fc` / `5678668bd7f97a21fe5f52fbd5a3ac8f5084802165a7355f113ee93770bd0de6` / `82c3c9aa39deae8deed1881edb3fb721ab7c05140c65d08e8a9b6e195f358298`
- Set B schema SHA-256: `980504b21cc0b14cf20ef3c3374d9d51de82691c13b1cbc82246fc9904a366dc`
- Set B X/y/group array SHA-256: `584ec01e021767e9065b5d8df305ce7a580bd3726b3a33683b3378455b4ef6d6` / `d7d714f5021ebfed38417a949c730d9c26c332b2f8c6b06be7cd185374957034` / `f0e6353406dfc7b6366aa890e350bae76f08cb499cba230cd79578ee715c5b00`

These hashes are aggregate provenance, not patient data. They establish the latest run's cache identity but do not establish equality with the older Python 3.11 passing run because that artifact did not include this cache audit. Next action is to run the pinned Python 3.11 workflow on a revision containing the current diagnostics, then compare cache and per-model fingerprints only when artifacts are from matching source revisions and construction protocols.

Run: https://github.com/culprit-k/VITALIS/actions/runs/38714974286

## Earlier observed discrepancy

Python 3.13 clean-checkout run #38702163220 on source commit `a445b2b38a045c7cb2b27ad99687912ac951b16d` produced 37/42 matching mean/sample-SD pairs (75/84 scalar values). Five differences were temporal-model metrics at horizons 1 h and 3 h. The later #38714974286 result above matched all pairs; do not generalize the earlier mismatch to the latest run.

## Cross-runtime comparison after the pinned Python 3.11 pass

The retained artifact for pinned Python 3.11 run #38692360591 reports 42/42 mean/sample-SD pairs and 84/84 scalar matches. The retained Python 3.13 artifact for run #38712336504 reports 37/42 pairs and 75/84 scalar matches. The two runs have the same audited cohort totals and predeclared protocol, but the Python 3.13 artifact has no counterpart Python 3.11 cache fingerprint from that passing run, so cache equality between those exact runs is not established.

Direct aggregate-output comparison showed small per-seed differences in temporal-model probabilities/metrics, with threshold-sensitive alert differences at 1 h and 3 h; even static-model Brier values differed at machine precision. This was consistent with numerical/runtime drift being a contributor, but did not prove whether the cause was BLAS/runtime, feature matrix differences, or fit-path differences. Python 3.13 remains diagnostic-only; pinned Python 3.11 is the declared acceptance gate.

Commit `798de0c420d8de3d9bd433a7cb1a40d192f5550a` adds privacy-safe per-run diagnostics to the aggregate evaluator: schema and selected-feature hashes, split/training-target hashes, imputer/scaler/model parameter hashes, convergence iterations, prediction-array hash, aggregate prediction moments, and fixed score-band counts around 0.5. It does not export patient identifiers, feature rows, or row-level predictions and does not alter the model, threshold, seeds, horizons, or acceptance rule.

## Next diagnostic

The Python 3.11 workflow already invokes `scripts/audit_reproduction_cache.py`; the current Python 3.13 diagnostic workflow also now retains the same cache-integrity audit. The latest artifact's cache hashes must be compared with a fresh pinned Python 3.11 artifact generated on a matching source revision. If cache fingerprints match but model fingerprints differ, investigate split ordering and dependency/runtime effects. If probabilities match but alert metrics differ, test temporal alarm/refractory/window summaries against small synthetic fixtures.

No patient-level predictions or identifiers may be exported. Set B remains evaluation-only; diagnostics must not be used to tune the model or threshold.

## Decision rules

1. If cache/schema fingerprints differ, investigate cache construction/order before model code.
2. If cache fingerprints match but split or coefficient hashes differ, investigate split ordering and dependency/runtime effects.
3. If probabilities differ while fitted model summaries match, inspect prediction chunking and preprocessing behavior.
4. If probabilities match but alert metrics differ, test the temporal alarm/refractory/window summary implementation against small synthetic fixtures.
5. If the historical local run cannot be reconstructed, preserve it as historical evidence and request independent review of a separately versioned replacement baseline. Do not silently replace the baseline.

The acceptance rule in `docs/HORIZON_RECONCILIATION_ACCEPTANCE_RULE.md` remains unchanged. VITALIS remains research-only and is not clinically validated.
