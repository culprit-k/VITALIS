# Reproduction failure triage — 15 October 2026

## Latest same-source diagnostic comparison — run #38718273571

The Python 3.13 diagnostic on current source commit `aa9f7a0d75b3c1f27a869ca853510ee160d02f23` completed successfully as a workflow, but the metric reconciliation is **37/42 mean/sample-SD pairs and 75/84 scalar values**; five pairs mismatch the unchanged historical reference. This remains diagnostic-only and is not the Python 3.11 acceptance gate.

The cache-integrity audit in this run reports the same schema, ordered source-file list, X/y/group array hashes, feature summary hashes, cohort counts, and patient-block checks as the earlier Python 3.13 diagnostic artifact from run #38714974286, which reported 42/42 pairs. Thus the compared runs have matching audited cache identities, but not matching fitted model fingerprints or predictions. In the run metadata, OpenBLAS reports architecture `Haswell` for the latest run and `SkylakeX` for the earlier 42/42 run, while both report one BLAS/OpenMP thread. This is a plausible numerical-runtime contributor, not proof of root cause.

The aggregate-only comparison found differences in coefficient/intercept/prediction hashes for both static and temporal models. Temporal-model score summaries and threshold-adjacent score-band counts differ as well; at least one horizon has alert-count changes. No patient-level values were exported. Next step is to run the pinned Python 3.11 acceptance workflow on this current source revision, then compare cache and model diagnostics across runtimes. Do not change the baseline, threshold, seeds, horizons, or acceptance rule.

Current run: https://github.com/culprit-k/VITALIS/actions/runs/38718273571
Earlier diagnostic: https://github.com/culprit-k/VITALIS/actions/runs/38714974286

## Prior cache fingerprints (same values in both compared Python 3.13 artifacts)

Both cohort audits passed and report the expected totals and 109 features. Privacy-safe cache fingerprints:
- Set A schema SHA-256: `980504b21cc0b14cf20ef3c3374d9d51de82691c13b1cbc82246fc9904a366dc`
- Set A X/y/group array SHA-256: `9f9379097b68581c9fdf7806a6b4dcb95e3a6e358b8fcefe0306845acf11c3fc` / `5678668bd7f97a21fe5f52fbd5a3ac8f5084802165a7355f113ee93770bd0de6` / `82c3c9aa39deae8deed1881edb3fb721ab7c05140c65d08e8a9b6e195f358298`
- Set B schema SHA-256: `980504b21cc0b14cf20ef3c3374d9d51de82691c13b1cbc82246fc9904a366dc`
- Set B X/y/group array SHA-256: `584ec01e021767e9065b5d8df305ce7a580bd3726b3a33683b3378455b4ef6d6` / `d7d714f5021ebfed38417a949c730d9c26c332b2f8c6b06be7cd185374957034` / `f0e6353406dfc7b6366aa890e350bae76f08cb499cba230cd79578ee715c5b00`

These hashes are aggregate provenance, not patient data. They establish cache identity for these two Python 3.13 artifacts, but not cache equality with the older Python 3.11 passing run because that artifact did not include this cache audit.

## Earlier observed discrepancy

Python 3.13 clean-checkout run #38702163220 on source commit `a445b2b38a045c7cb2b27ad99687912ac951b16d` produced 37/42 matching mean/sample-SD pairs (75/84 scalar values). Five differences were temporal-model metrics at horizons 1 h and 3 h. Run #38714974286 later matched all pairs; run #38718273571 on the current source revision again reported 37/42. Do not generalize either diagnostic outcome as acceptance.

## Cross-runtime comparison after the pinned Python 3.11 pass

The retained artifact for pinned Python 3.11 run #38692360591 reports 42/42 mean/sample-SD pairs and 84/84 scalar matches. The retained Python 3.13 artifact for run #38712336504 reports 37/42 pairs and 75/84 scalar matches. The two runs have the same audited cohort totals and predeclared protocol, but the Python 3.13 artifact has no counterpart Python 3.11 cache fingerprint from that passing run, so cache equality between those exact runs is not established.

Direct aggregate-output comparison showed small per-seed differences in temporal-model probabilities/metrics, with threshold-sensitive alert differences at 1 h and 3 h; even static-model Brier values differed at machine precision. This was consistent with numerical/runtime drift being a contributor, but did not prove whether the cause was BLAS/runtime, feature matrix differences, or fit-path differences. Python 3.13 remains diagnostic-only; pinned Python 3.11 is the declared acceptance gate.

Commit `798de0c420d8de3d9bd433a7cb1a40d192f5550a` adds privacy-safe per-run diagnostics to the aggregate evaluator: schema and selected-feature hashes, split/training-target hashes, imputer/scaler/model parameter hashes, convergence iterations, prediction-array hash, aggregate prediction moments, and fixed score-band counts around 0.5. It does not export patient identifiers, feature rows, or row-level predictions and does not alter the model, threshold, seeds, horizons, or acceptance rule.

## Next diagnostic

The Python 3.11 workflow already invokes `scripts/audit_reproduction_cache.py`; the Python 3.13 diagnostic workflow also retains the same cache-integrity audit. The next required step is a fresh pinned Python 3.11 artifact from the current source revision. Compare its cache hashes with the same-revision Python 3.13 artifact. If cache fingerprints match but model fingerprints differ, investigate split ordering, solver convergence, dependency/runtime effects, and CPU/BLAS behavior. If probabilities match but alert metrics differ, test temporal alarm/refractory/window summaries against small synthetic fixtures.

No patient-level predictions or identifiers may be exported. Set B remains evaluation-only; diagnostics must not be used to tune the model or threshold.

## Decision rules

1. If cache/schema fingerprints differ, investigate cache construction/order before model code.
2. If cache fingerprints match but split or coefficient hashes differ, investigate split ordering and dependency/runtime effects.
3. If probabilities differ while fitted model summaries match, inspect prediction chunking and preprocessing behavior.
4. If probabilities match but alert metrics differ, test the temporal alarm/refractory/window summary implementation against small synthetic fixtures.
5. If the historical local run cannot be reconstructed, preserve it as historical evidence and request independent review of a separately versioned replacement baseline. Do not silently replace the baseline.

The acceptance rule in `docs/HORIZON_RECONCILIATION_ACCEPTANCE_RULE.md` remains unchanged. VITALIS remains research-only and is not clinically validated.


## Same-cache comparison: current Python 3.13 diagnostic vs earlier Python 3.11 pass — 16 October 2026

The completed Python 3.13 diagnostic workflow [#38831794049](https://github.com/culprit-k/VITALIS/actions/runs/38831794049) used source commit `33fa7f6362e44ee126ddbebd20be6dc9738a12cb`. It completed source/cohort audits, rebuilt both caches, ran all nine horizon/seed combinations, and retained aggregate-only outputs. Its diagnostic comparison is 37/42 mean/sample-SD pairs and 75/84 scalar matches; this is not the acceptance gate.

The previously successful pinned Python 3.11 run [#38748749241](https://github.com/culprit-k/VITALIS/actions/runs/38748749241) reports 42/42 pairs and 84/84 scalar matches, but it used source commit `d0c149a0941ba26139ec6793436896f504be8bd6`. Its source manifest records the evaluator blob for `scripts/evaluate_horizon_cross_cohort.py` as `5739a64807b970f0c945404896fc5536dba687da`; the current branch and the Python 3.13 run use blob `891b84ad4a5da039f1dc38411211c503c971167c`. Therefore, the earlier Python 3.11 pass is not a same-source reproduction of the current evaluator and must not be used to claim the current acceptance gate passes.

There is useful positive evidence: the cache-integrity audit hashes are identical between these artifacts for both cohorts, including schema, ordered source file list, X/y/group arrays, feature summaries, cohort counts, and patient-block checks. The source cohort fingerprints also match. Thus the audited data/cache identity is consistent, while the evaluator source revision differs. This isolates the next required experiment: run the pinned Python 3.11 acceptance workflow against the current evaluator source blob `891b84ad4a5da039f1dc38411211c503c971167c`, then compare its aggregate output and model diagnostics with the Python 3.13 run on the same source. Do not attribute the discrepancy to Python/BLAS until this same-source comparison is complete.

The concurrency-only workflow maintenance commit `b626ca6f723b293820a17175a11396018112ab29` fixed duplicate concurrency configuration and was intended to allow a fresh pinned workflow to run without cancelling another expensive cohort job. Preserve both prior artifacts; do not overwrite the historical baseline or relax the six-decimal acceptance rule.


## Same-commit Python 3.11 CPU-dispatch comparison — 16 October 2026

Two fresh full-cohort runs of the same source commit `dfe00af5dd5611b82a27381c9bf9841b37e5e0ca`, both using Python 3.11.17 and the same pinned scientific package versions, produced different baseline reconciliation outcomes:

- Passing PR-triggered run [#38837327041](https://github.com/culprit-k/VITALIS/actions/runs/38837327041): 42/42 mean/sample-SD pairs and 84/84 scalar values matched at six decimal places.
- Failing push-triggered run [#38837321948](https://github.com/culprit-k/VITALIS/actions/runs/38837321948): 37/42 pairs and 75/84 scalar values matched; five temporal-model pairs failed.
- The two artifacts have identical Set A/Set B cache-array hashes (X, y, and patient groups), schema hashes, ordered source-file hashes, and cohort audit counts. Their `pip freeze` outputs match, and neither artifact reports model-fit warnings.
- The captured OpenBLAS 0.3.30 runtime dispatch differs: the failing run reports `Haswell`; the passing run reports `SkylakeX`. Both report one BLAS thread. NumPy's build configuration lists the same OpenBLAS build, but runtime CPU dispatch selects different kernels.

This is stronger evidence for hardware-dependent floating-point differences than the prior cross-Python comparison. It still does not prove that CPU dispatch is the sole cause of every mismatch. Differences in temporal score metrics and threshold-based alert counts indicate that small numerical changes can cross the fixed 0.5 threshold and affect downstream warning metrics.

### Current decision

- The optional extended-analysis CI condition is fixed in commit `dfe00af5dd5611b82a27381c9bf9841b37e5e0ca`; that correction does not resolve the same-commit numerical variation.
- Keep the six-decimal rule and the 14 October historical baseline unchanged pending independent review. Do not count one successful run as proof of reliable reproducibility when another run of the same commit fails.
- Next, make the numerical backend/runner policy explicit and validate it in a controlled experiment. Any choice that changes numerical results or requires a new reference aggregate must be documented as a separately versioned baseline with independent review; never overwrite the historical file silently.
- Set B remains evaluation-only. No model, threshold, or feature changes may be selected based on Set B. Do not export patient-level predictions or identifiers.

VITALIS remains a retrospective research prototype, not clinically validated and not for patient-care decisions.


## Current-source clean-checkout reproduction — 16 October 2026

The latest pinned Python 3.11 full-cohort workflow [#38840196351](https://github.com/culprit-k/VITALIS/actions/runs/38840196351) completed successfully on exact source commit `2de041462e2ff4df2872dbcd98983ed3e121b86b` (workflow event SHA `f30d7e07dd52f64e578f7c26fb46e707b4f548f5`). It rebuilt both feature caches from the official cohort source in ephemeral runner storage, passed cohort/cache audits, completed all nine horizon/seed evaluations (18 model fits), verified aggregate-only outputs, and passed the unchanged six-decimal reconciliation: **42/42 mean/sample-SD pairs and 84/84 scalar values matched**. The optional physiology-ablation and Platt-calibration analyses were skipped because extended analyses were not enabled; this does not affect the core acceptance run.

The same-source Python 3.13 diagnostic [#38840196302](https://github.com/culprit-k/VITALIS/actions/runs/38840196302) also completed and reported 42/42 pairs and 84/84 scalar matches, but remains diagnostic-only and is not an acceptance gate.

The two artifacts have matching official source-cohort content fingerprints and matching audited cache fingerprints for both Set A and Set B, including schema, ordered source-file list, X/y/group arrays, feature summaries, cohort counts, and patient-block checks. The metric tables in the two reports also agree at the reported precision. This is positive evidence that the current source and cache construction reproduce the preserved aggregate under these runs, including across the two tested Python versions. It does **not** resolve the previously observed same-commit Python 3.11 CPU-dispatch discrepancy from commit `dfe00af5dd5611b82a27381c9bf9841b37e5e0ca`; that historical evidence remains valid and should not be deleted or rewritten.

### Decision and next stage

- Record the pinned Python 3.11 acceptance gate as **passed for source commit `2de041462e2ff4df2872dbcd98983ed3e121b86b` in this run**. Do not generalize this to a guarantee of deterministic reproduction on every runner.
- Preserve the historical baseline and six-decimal rule unchanged.
- Preserve both aggregate-only artifacts and their provenance. No raw data, row-level predictions, patient identifiers, or feature caches are committed.
- Next stage is a reproducibility-hardening review: compare numerical-backend diagnostics from the two new artifacts, determine whether the workflow captures enough runtime/CPU-dispatch metadata to explain the earlier same-commit variance, and add a controlled synthetic regression test for threshold-adjacent alert/refractory behavior if needed. Any model/threshold change or replacement baseline requires a separate reviewed protocol.
- Extended physiology ablation and Platt calibration have **not** been run in this workflow; they remain separate research analyses, not prerequisites to claiming the core reproduction gate passed.
- Independent statistical/clinical review and genuinely external validation remain open. Set B is still evaluation-only, and VITALIS remains a retrospective research prototype, not clinically validated and not for patient-care decisions.
