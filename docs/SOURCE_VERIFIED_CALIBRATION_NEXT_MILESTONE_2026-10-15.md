# Next milestone: source-verified calibration and operating-point reproduction

Date: 15 October 2026
Status: **Protocol prepared; full-cohort execution not yet verified from this commit.**

## Why this is the next milestone

Calibration and operating-point analyses already exist in the repository, including `scripts/evaluate_horizon_calibration.py`, `src/vitalis/calibration.py`, and aggregate summaries dated 15 October. However, the existing report/artifact metadata identifies important calibration/utility outputs as produced by a reconstructed local working copy that was not byte-identically verified against the checked-in source. Those outputs are exploratory and must not be promoted to source-verified evidence without a clean-checkout run.

This milestone does not declare the earlier five baseline discrepancies solved. The strict reproduction gate remains open. Calibration/utility work is a separate research track and must not be used to excuse or overwrite the failed baseline reconciliation.

## Locked protocol

- Source: clean checkout of `work/strict-reproducibility-gate`; record exact commit SHA and Git blob SHAs for the runner and all imported project modules before execution.
- Runtime: Python 3.11 using the repository's declared reproduction constraints; record resolved dependency and BLAS/thread manifests.
- Cohorts: Set A = 20,336 patients / 790,215 rows / 17,136 positive hourly Challenge labels; Set B = 20,000 patients / 761,995 rows / 10,780 positive hourly Challenge labels. Validate official counts and the 109-feature schema before fitting.
- Horizons: 1, 3, and 6 hours.
- Seeds: 42, 123, and 2026.
- Models: static and temporal.
- Within Set A, use patient-disjoint 60% model-training / 20% calibration / 20% untouched operating-point holdout partitions. Fit the Platt recalibrator on calibration patients only. Do not select thresholds using the calibration partition.
- Prespecified reporting grid: thresholds 0.001, 0.005, 0.01, 0.05, and 0.5; six-hour refractory interval. Report all grid results rather than claiming a clinically optimal threshold.
- Set B is evaluation-only: no fitting, recalibration, feature selection, model selection, or threshold selection from Set B outcomes.
- Preserve aggregate-only outputs. No row-level probabilities, patient identifiers, source patient records, or caches may be committed or uploaded as workflow artifacts.

## Required run outputs

1. A pre-run source/environment manifest with commit and source blob hashes.
2. Official cohort/schema validation results and cache-build provenance.
3. Aggregate-only calibration and operating-point summaries.
4. Patient-cluster uncertainty summaries with replicate counts and a clear description of what the intervals cover.
5. A comparison of the new output to the existing 15 October aggregate, explicitly labelled as a provenance comparison—not a pass/fail equality gate unless a matching historical source run is demonstrated.
6. Post-run source/environment manifest and output SHA-256 hashes.
7. Test results for the runner and calibration/utility functions.

## Acceptance gates

- Fail closed if source blobs differ from the checked-out source, cohort counts/schema do not match, patient partitions overlap, either class is absent from the calibration split, or Set B enters fitting/threshold-selection paths.
- Repeated clean-checkout runs should reproduce aggregate outputs under the same locked environment; retain all artifacts and record any non-determinism.
- Any discrepancy against prior exploratory summaries must be reported, not fixed by tuning on Set B or editing prior results.
- Mark this milestone **source-verified** only after a clean-checkout run finishes, manifests and aggregate-only artifacts are retained, and the privacy/evaluation-only checks pass.

## Interpretation limits

The target is future entry into the PhysioNet/CinC Challenge 2019 hourly `SepsisLabel`-positive window, not independently observed biological sepsis onset. Thresholds and assumed alert/missed-window costs are research scenarios, not clinically validated operating points. Even a successful reproduction is not evidence of clinical utility or safety. Prospective evaluation on a genuinely new cohort and independent statistical/clinical review remain separate gates.

## Current status

- Existing calibration/operating-point code and tests are present.
- Existing aggregate outputs are available but some have reconstructed-local provenance.
- Standard CI tests passed on commit `ac443cff20a35e85ffdd7dda095af3945ca42fb5` (workflow run [38689874123](https://github.com/culprit-k/VITALIS/actions/runs/38689874123)).
- No clean-checkout, locked-environment calibration reproduction is confirmed by this status check.
- Historical baseline reconciliation still has five unresolved temporal-model discrepancies; Step 2 remains not accepted.
