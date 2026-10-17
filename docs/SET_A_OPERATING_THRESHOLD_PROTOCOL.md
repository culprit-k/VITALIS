# VITALIS development-only operating-threshold protocol

**Status:** protocol proposal; research-only. No thresholds in this document are clinically approved.

## Motivation

The existing cross-cohort experiment uses a fixed probability threshold of 0.5 for descriptive reporting. The prevalence-aware calibration analysis shows that this fixed threshold can yield almost no sensitivity after calibration, while class-weighted scores can be badly overconfident before calibration. A threshold of 0.5 must therefore not be interpreted as a suitable clinical alert policy.

## Data boundary

- Use Set A only to choose operating thresholds.
- Keep patient groups disjoint between model fitting, probability calibration, and threshold selection.
- Threshold selection must use a dedicated Set A development partition that is not used to fit the base model or calibrator.
- Set B remains evaluation-only. Do not use Set B to select a threshold, alert budget, feature, model, calibration map, or stopping rule.
- Do not export patient IDs, row-level predictions, or feature caches. Retain aggregate metrics only.

## Predeclared evaluation grid

Evaluate each predeclared horizon (1, 3, and 6 hours) and each frozen model/calibration configuration separately. For the Set A threshold-selection partition, report a threshold sweep over a fixed grid (0.01 increments from 0.01 through 0.99, plus exact operating points 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.10, and 0.50). The grid is descriptive; the selected threshold must be chosen without looking at Set B.

For every threshold, report:
- sensitivity/recall and specificity;
- positive predictive value (PPV) and negative predictive value (NPV);
- precision-recall AUPRC and AUROC for the underlying scores (threshold-independent);
- confusion counts as aggregate totals only;
- alert episodes per patient-day, using the already specified six-hour refractory period and a consistent episode definition;
- patient-cluster bootstrap uncertainty intervals for sensitivity and PPV at four predeclared reference thresholds (0.01, 0.05, 0.10, 0.50), plus alert-burden point estimates and patient-cluster intervals at those same reference thresholds. Other grid points receive aggregate point estimates only.

Document positive-window prevalence and compare Brier score to the constant-prevalence reference. Calibration quality and discrimination are different properties and must not be conflated.

## Selection rule

Before running the sweep, choose an explicit development objective and alert-budget constraint with the clinical/research supervisor. Do not silently optimize a threshold on Set B or choose a threshold after seeing the preferred result. If no defensible alert budget has been specified, publish the full Set A trade-off table and do not nominate a single operating threshold.

Any chosen threshold and its rationale must be frozen and recorded before the final Set B evaluation. Set B results should be presented once for the frozen threshold alongside threshold-independent metrics and uncertainty intervals. Do not retune after viewing Set B.

## Acceptance and interpretation

- Verify model-fit, calibration, and threshold-selection patients are disjoint for every horizon and seed.
- Verify deterministic seeds, source-manifest integrity, cache fingerprints, and aggregate-only outputs.
- Include a constant-prevalence reference and patient-cluster bootstrap intervals.
- Report all attempted predeclared configurations, including unsuccessful or degenerate operating points.
- Treat Challenge 2019 labels as the future Challenge-label-window target, not independently adjudicated sepsis onset.
- Results are research evidence only, not clinical validation or a patient-care recommendation.

## Current blocker

This protocol is implemented by `scripts/evaluate_set_a_threshold_sweep.py` and wired into the optional extended full-cohort workflow. Automated tests and a pinned full-cohort execution are still required before treating the implementation or output as verified. Uncertainty intervals are limited to the four reference thresholds listed above; the full grid receives aggregate point estimates. No threshold has been selected, and no Set B result should be inferred from this document.
