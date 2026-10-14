# Full-cohort horizon forecasting: Set A → Set B

**Status:** runner and synthetic tests added; full official-cohort run pending on the authorized local data.  
**Scope:** retrospective future-Challenge-label forecasting, not clinical onset prediction.

## Protocol

For each predeclared seed (42, 123, 2026) and horizon (1, 3, 6 hours):

1. Read the memory-mapped Set A and Set B feature caches from local paths outside the Git repository.
2. Verify cohort counts, binary labels, row counts, patient-group counts, and matching feature schemas. The runner requires the expected official Set A totals (20,336 patients, 790,215 rows, 17,136 positive hourly challenge labels) and Set B totals (20,000 patients, 761,995 rows, 10,780 positive hourly challenge labels).
3. Build horizon targets within each patient's contiguous chronological rows. Exclude rows already carrying a positive current label and each patient's final H rows. Never shift labels across patient boundaries.
4. Split eligible Set A rows by patient into a 60% training partition and a 40% unused holdout. The unused Set A holdout is not used for tuning.
5. Fit two models on the Set A training partition only: static baseline features and the full temporal feature set. Imputation, missingness indicators, scaling, and logistic regression are fitted only on training rows.
6. Evaluate on every eligible Set B patient. Set B is never used for fitting, feature selection, calibration, or threshold selection.
7. Report aggregate row-level AUROC/AUPRC/Brier and fixed-threshold metrics, plus patient-level alert burden, forecast-positive-window coverage, label-relative warning time, and patient-cluster percentile intervals.
8. Save aggregate JSON only. Raw patient data, caches, and row-level predictions remain outside Git.

## Build local feature caches

Use the checked-in cache builder sequentially. Each cache directory must be outside the repository and contain all chunks before evaluation. Do not run overlapping chunks against the same cache.

Example four-chunk schedule for each official cohort:

```bash
# Set A (20,336 patients)
python scripts/build_feature_cache.py /path/to/training_setA --cache-dir /path/outside/repo/cache_set_a --start 0 --end 5000
python scripts/build_feature_cache.py /path/to/training_setA --cache-dir /path/outside/repo/cache_set_a --start 5000 --end 10000
python scripts/build_feature_cache.py /path/to/training_setA --cache-dir /path/outside/repo/cache_set_a --start 10000 --end 15000
python scripts/build_feature_cache.py /path/to/training_setA --cache-dir /path/outside/repo/cache_set_a --start 15000 --end 20336

# Set B (20,000 patients)
python scripts/build_feature_cache.py /path/to/training_setB --cache-dir /path/outside/repo/cache_set_b --start 0 --end 5000
python scripts/build_feature_cache.py /path/to/training_setB --cache-dir /path/outside/repo/cache_set_b --start 5000 --end 10000
python scripts/build_feature_cache.py /path/to/training_setB --cache-dir /path/outside/repo/cache_set_b --start 10000 --end 15000
python scripts/build_feature_cache.py /path/to/training_setB --cache-dir /path/outside/repo/cache_set_b --start 15000 --end 20000
```

Only run each command after confirming the source path points to the correct official cohort. If a cache directory already contains data from a different archive, discard that local cache and rebuild into a fresh directory.

## Run the cross-cohort experiment

```bash
python scripts/evaluate_horizon_cross_cohort.py \
  --set-a-cache /path/outside/repo/cache_set_a \
  --set-b-cache /path/outside/repo/cache_set_b \
  --horizons 1 3 6 \
  --seeds 42 123 2026 \
  --threshold 0.5 \
  --refractory-hours 6 \
  --bootstrap-replicates 200 \
  --output /path/outside/repo/horizon_cross_cohort.json
```

The runner stops if cohort counts or schemas do not match expectations. Keep the output outside the repository initially; review it for identifiers or row-level information before sharing only the approved aggregate report.

## Interpretation guardrails

- Challenge 2019 SepsisLabel already incorporates a six-hour lead convention. An H-hour target means that the challenge label becomes positive within the next H rows; it is not independently observed onset within H hours.
- "Alerts outside future-positive windows" are not verified clinical false alarms. Warning time is relative to challenge-label entry, not biological onset.
- The 0.5 threshold and six-hour refractory interval are fixed research settings, not clinically selected alert policies.
- The patient-cluster intervals quantify uncertainty across sampled Set B patients for this retrospective cohort. They do not establish prospective validity, safety, or patient benefit.
- Set B must remain evaluation-only, even if metrics are disappointing. Do not change the model or threshold based on Set B and then report the same Set B results as unbiased evaluation.
- If a cohort count check fails, stop and reconcile the archive and cache provenance rather than bypassing the check.

## Completion checklist

- [ ] Both caches built from verified official cohorts; chunk completion and metadata checked.
- [ ] Cross-cohort CLI finishes for all nine seed × horizon combinations.
- [ ] Aggregate-only output reviewed and archived outside Git.
- [ ] Results and uncertainty reviewed without tuning on Set B.
- [ ] Independent statistical/clinical review completed before any clinical claim.
