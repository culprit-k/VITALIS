# VITALIS Leakage and Evaluation Audit

**Date:** 2026-10-14  
**Scope:** Static source review and regression-test additions; this is not a clinical validation.

## Findings from source review

| Area | Current implementation | Audit assessment |
|---|---|---|
| Patient-level splitting | `GroupShuffleSplit` with patient group codes; explicit `assert_disjoint_patient_splits` check | Correctly designed to prevent the same patient entering multiple splits; now regression-tested |
| Feature selection | `observed_training_features` is called on the training fold only | No validation/test-driven feature selection identified |
| Imputation and scaling | `SimpleImputer` and `StandardScaler` are inside a scikit-learn pipeline fitted on training rows only | No validation/test fit identified |
| Threshold choice | Baseline uses a fixed 0.5 reference threshold | No test-set threshold tuning identified; this is not a clinically selected threshold |
| Challenge label timing | The code uses `SepsisLabel` as supplied and documents the six-hour lead convention | No second label shift identified |
| Temporal features | Lag/delta and trailing means are computed within each patient file, preserving file row order | Causal in implementation; assumes each PSV row is one hourly observation and file order is chronological |
| Patient-baseline features | Expanding patient baseline/deviation features are generated within the patient file | Must remain experimental; early history and missingness can make estimates unstable |
| Held-out recalibration | Phase 2 runner fits recalibration using validation labels and reports on test rows | Separation is present in code; do not select methods based on test performance |
| Alert-burden calculation | Uses a fixed threshold and refractory interval; reports alerts outside challenge-positive label windows and coverage of contiguous label runs | Descriptive label-window analysis only, not true clinical false alarms or event-level sensitivity |

## Regression tests added

- `tests/test_validation.py`: confirms disjoint patient splits pass and pairwise overlaps fail.
- `tests/test_evaluation_metrics.py`: checks confusion-matrix-derived sensitivity/specificity/PPV/NPV, alert refractory behavior, challenge-label episode coverage, and invalid refractory periods.
- Existing calibration tests cover probability boundaries, reliability-bin coverage, invalid inputs, and empty missingness summaries.

## Interpretation and remaining risks

1. **Source-order assumption:** alert-burden code assumes test rows remain ordered by patient and time. The baseline runner sorts held-out indices back into the original file concatenation order, and patient files are read in sorted path order. A future data adapter must preserve these guarantees or explicitly sort using a trustworthy time index.
2. **Hourly dependence:** row-level confidence intervals and metrics do not establish patient-level event performance. Challenge-positive runs are not independently observed sepsis episodes.
3. **Operating point:** threshold 0.5 is only a reference. Any clinically motivated threshold must be selected using a prespecified validation protocol, with alert burden and consequences of missed/false alerts reported.
4. **Data and site shift:** this audit does not establish external validity, fairness, calibration transport, prospective performance, or clinical utility.
5. **Strict source identity:** this audit reviews repository source through the GitHub connector; it does not close the separate byte-for-byte local-runner reconciliation exception.

## Decision

The reviewed split/preprocessing design is suitable for continued *exploratory research* with the stated assumptions. It is not evidence that the model is clinically safe or ready for hardware integration or patient-facing use. Run the full test suite and inspect CI before treating these additions as accepted.
