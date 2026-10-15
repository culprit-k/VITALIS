# Pinned clean-checkout full-cohort reproduction — reconciliation findings

**Date:** 2026-10-15  
**Workflow run:** [38679761894](https://github.com/culprit-k/VITALIS/actions/runs/38679761894)  
**Run commit:** `c20ed448ab3fbcfc6e6e35c73dd8b28a26950184`  
**Artifact:** [aggregate-only workflow artifact](https://github.com/culprit-k/VITALIS/actions/runs/38679761894/artifacts/11948141410)  
**Artifact SHA-256:** `480f3a18f2f35413984efa6d8be8bde3e44eb987554caacfa60cd57a2312cd1d`

## Decision

**The full-cohort execution completed; the reproducibility acceptance gate did not pass.** Do not mark Step 2 release-complete yet. The predeclared reconciliation rule remains unchanged: exact match after rounding each aggregate mean and sample standard deviation to six decimal places. The historical baseline was not changed.

## What this run verified

- Exact clean checkout at commit `c20ed448ab3fbcfc6e6e35c73dd8b28a26950184`; the source manifest reported a clean working tree and matching tracked source blobs before evaluation.
- Python 3.11.17 on the GitHub-hosted Linux x86_64 runner.
- Pinned environment: NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0, SciPy 1.17.0, joblib 1.5.3, threadpoolctl 3.6.0, plus the recorded full pip freeze in the retained artifact.
- Official Challenge 2019 cohorts audited before feature generation:
  - Set A: 20,336 patients, 790,215 hourly rows, 17,136 positive hourly labels.
  - Set B: 20,000 patients, 761,995 hourly rows, 10,780 positive hourly labels.
- Fresh Set A and Set B feature caches were built from disjoint chunks.
- All nine predeclared horizon/seed runs completed (1, 3, 6 hours × seeds 42, 123, 2026), producing 18 model evaluations.
- Set B was evaluation-only; no raw cohort files, feature caches, patient IDs, or row-level predictions were uploaded. The artifact retains aggregate outputs and provenance.
- The output reports 732,357 / 694,628 / 638,026 eligible Set B rows and 919 / 2,665 / 5,144 future-positive rows for the 1 / 3 / 6-hour horizons, matching the preserved baseline's cohort counts.

## Reconciliation result

The run compared 42 metric mean/SD pairs (7 metrics × 2 models × 3 horizons) with `results/horizon_cross_cohort_2026-10-14.json`.

- Pairs where both mean and SD matched: **37 / 42**.
- Individual scalar values matching: **75 / 84**.
- Five pairs failed at least one six-decimal comparison. All five are for the temporal model:

| Horizon | Metric | Fresh mean | Baseline mean | Fresh sample SD | Baseline SD | Failed fields |
|---:|---|---:|---:|---:|---:|---|
| 1 h | Specificity | 0.8424054169 | 0.842405 | 0.0146516690 | 0.014651 | SD |
| 1 h | Alerts / at-risk patient-day | 1.4615822611 | 1.461593 | 0.1132623320 | 0.113243 | Mean and SD |
| 3 h | Brier score | 0.1313454415 | 0.131344 | 0.0034725607 | 0.003472 | Mean and SD |
| 3 h | Alerts / at-risk patient-day | 1.2762744951 | 1.276286 | 0.0807039708 | 0.080706 | Mean and SD |
| 3 h | Future-positive-window coverage | 0.2937976061 | 0.293435 | 0.0151169140 | 0.014854 | Mean and SD |

The numerical differences are small in absolute terms, but the fixed acceptance test is exact at six decimals. They are failures under that rule; they must not be relabeled as passes.

## Interpretation and unresolved cause

This run establishes that the full-cohort pipeline can execute in the intended pinned Python 3.11 environment. It does **not** establish exact reproduction of the historical aggregate baseline.

The preserved baseline records an execution note saying the historical local run used a reconstruction of the evaluator and an optimized patient-cluster bootstrap because a full Git clone was unavailable. The older source-verified local run used Python 3.13.5, whereas this clean-checkout run used Python 3.11.17. These are provenance differences worth investigating, but the evidence currently available does not prove which difference caused each of the five mismatches. The mismatches are concentrated in temporal-model metrics, including warning metrics; do not infer a root cause from that pattern alone.

A direct comparison with the earlier unpinned clean-checkout artifact (run [#38677774161](https://github.com/culprit-k/VITALIS/actions/runs/38677774161), using NumPy 2.4.6 / pandas 3.0.6 / scikit-learn 1.9.1 / SciPy 1.17.1) shows the pinned run's aggregate means/SDs are closer to the preserved baseline for each of these five pairs, but the old artifact also differs from the pinned run at seed level. This is consistent with environment or numerical-path sensitivity, not proof of a specific cause. The baseline JSON stores aggregate mean/SD values rather than the historical per-seed metrics, so exact seed-by-seed attribution against the baseline cannot be recovered from that file alone.

No evidence here justifies overwriting the baseline, loosening the tolerance, changing the model based on Set B, or claiming clinical utility. The preserved baseline remains an immutable comparator, not yet an authoritative reference result.

## Required follow-up before Step 2 can be accepted

1. Reconstruct the historical run's exact executable code, dependency versions, split behavior, and aggregation/metric implementation from preserved artifacts and provenance; distinguish documented facts from unknowns.
2. Compare seed-level outputs and metric calculation paths for the five discrepancies, using only aggregate or suitably privacy-safe diagnostics.
3. Have an independent reviewer assess the proposed explanation and whether a new baseline can be generated from a provenance-complete run. Any new baseline must be introduced separately, reviewed, and retain the old file unchanged.
4. Keep Set B strictly evaluation-only. No fitting, feature selection, recalibration, threshold selection, or model changes based on Set B results.
5. Only mark the reproduction gate passed when the declared acceptance process is satisfied and independently reviewed. If exact historical reconciliation proves impossible because the baseline provenance is insufficient, document that limitation and use a separately reviewed baseline-replacement decision rather than silently changing the criterion.

## Scope and safety

This is retrospective cross-cohort software reproduction, not independent external validation or clinical validation. The target is entry into the Challenge SepsisLabel-positive window, not independently observed sepsis onset. VITALIS remains research-only and must not guide patient care.
