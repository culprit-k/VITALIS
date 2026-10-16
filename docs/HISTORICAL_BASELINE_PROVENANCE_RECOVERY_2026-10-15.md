# Historical baseline provenance recovery — 15 October 2026

## Decision

**Historical provenance is not recovered. Step 2 remains not accepted.** The uploaded migration bundle contains useful earlier research artifacts, but it does not establish the source/environment identity of the later Set A → Set B, 1/3/6-hour experiment represented by `results/horizon_cross_cohort_2026-10-14.json`.

This document records the evidence found and the remaining provenance gap. It does not alter model code, baseline values, Set B use, or the predeclared six-decimal acceptance rule.

## Uploaded artifact inventory and hashes

SHA-256 values computed from the uploaded files:

| Artifact | SHA-256 |
|---|---|
| `VITALIS_complete_migration_bundle.zip` | `e4d86e500f0c179d94a1fda4b706fd6886c259d395c47a89b9096e0b56ac963d` |
| `VITALIS_research_project_bundle.zip` | `97c0bd7f84f0db999fa861afb48081dc12198e0718097de7a5c73b625f4d27f2` |
| `VITALIS_full_cohort_metrics.json` | `cca0b21a440e78458c83ad5402a306b59132fc04e5fd0145778ab30692f069d4` |
| `VITALIS_full_cohort_integrity_checks.json` | `a8fead9e891490db653c3c7bf55e7d857fa36a307937981b6732a4b1bb848bbd` |

The complete migration bundle contains preliminary, repeated-validation, patient-bootstrap, alert-burden, verification, and single-split full-cohort reports/results, plus an earlier research scaffold. The bundle README explicitly says no GitHub push/commit is included and the raw cohort and patient-level predictions are excluded.

## Provenance evidence found

1. The earlier scaffold's `pyproject.toml` uses open-ended dependency ranges (for example, NumPy `>=1.24`, pandas `>=2.0`, and scikit-learn `>=1.3`). It is not an exact lockfile for the later pinned reproduction environment.
2. The historical full-cohort report documents one patient-level split (seed 42), 20,336 Set A patients, and `SGDClassifier(loss='log_loss')` with only five iterations and convergence warnings. It describes the scores as preliminary.
3. The newer reconciliation protocol instead covers Set A and Set B, three prediction horizons (1/3/6 hours), seeds 42/123/2026, static and temporal models, and aggregate comparisons against the preserved horizon baseline.
4. The uploaded bundle does not contain an execution manifest tying that newer historical horizon run to an exact Git commit, exact resolved environment, exact evaluation command, and checksummed input/cache artifacts.
5. Existing audit evidence says the historical evaluator was reconstructed locally and was not verified byte-for-byte against the checked-in evaluator. Current pinned clean-checkout runs repeat the same five differences, and the Python 3.13 diagnostic shows Python minor version alone is unlikely to explain them. This does not identify the historical implementation difference.

## Hashes of selected source files in the uploaded bundle

These are hashes of the files as packaged in the upload, not proof that those exact bytes generated the later horizon baseline.

| File | SHA-256 |
|---|---|
| `project/pyproject.toml` | `c01d86ff7f8fe8f4677f33b8d935b0a7dd9fac31f3300a2cccae8b957c92a957` |
| `project/scripts/train_compare.py` | `c5a02a7f1749cd1be8d706b4cb8a1b5f468fb316a41c299fe713031a9c369a75` |
| `project/scripts/build_cohort.py` | `df48c7c6a9735d72c864e5f83f887c59a14e60b797fe34e5244865b6554fe831` |
| `project/src/vitalis/features.py` | `5a5e444277b44dd30678f574166641fe05b85b1f62fdd47215f3e18367aab72f` |

## Conclusion

The uploaded files are valid evidence for earlier VITALIS experiments, but they are not sufficient to reconstruct the exact historical execution behind the newer cross-cohort horizon baseline. No verified source/environment identity or causal explanation for the five discrepancies has been recovered.

## Next required actions

1. Seek the original execution record for the horizon baseline: exact command, checkout/commit, dependency lock or resolved package manifest, runtime/BLAS details, and cache/source fingerprints.
2. If the original record is unavailable, ask an independent statistical/reproducibility reviewer to review a **separately versioned replacement baseline** produced by the checked-in protocol. Preserve the current historical baseline unchanged and document the supersession rationale; do not silently overwrite it.
3. Keep Set B evaluation-only. Do not fit, tune, calibrate, select thresholds, or choose model variants using Set B outcomes.
4. Do not export or commit raw patient records, caches, identifiers, or row-level predictions.
5. Keep the pull request draft/unmerged and Step 2 marked **not accepted** until the documented review/acceptance gate is met.

## Guardrails

A reproducible retrospective benchmark is not evidence of clinical validity, clinical utility, safe alarm thresholds, or prediction of independently observed biological sepsis onset. Prospective/external clinical validation and governance review remain separate requirements.
