# Patient-cluster uncertainty for horizon calibration metrics

**Run date:** 15 October 2026  
**Status:** completed all nine predeclared horizon × seed combinations; 200 patient-cluster bootstrap replicates per model/run.  
**Scope:** conditional retrospective uncertainty on Set B; not prospective or clinical validation.

## Method and integrity

- Set A and Set B caches passed the evaluator’s official cohort count/schema checks. Set B target prevalence was approximately 0.1255% (1 h), 0.3837% (3 h), and 0.8062% (6 h).
- For each seed/horizon, models were trained on Set A training patients and Platt recalibration was fitted on disjoint Set A calibration patients. All bootstrap calculations were performed on Set B only after predictions were frozen.
- Whole patients were resampled with replacement. Per-patient sufficient statistics were used to calculate percentile intervals for calibrated Brier score, log loss, mean predicted probability, fixed-bin ECE, Brier score minus a prevalence-reference score, and paired calibrated-minus-raw Brier difference.
- 200 replicates × 18 model/horizon/seed combinations; summed runtime 235.5 seconds. Captured model-fit warnings: 0.
- Results contain aggregate metrics only. Raw records, feature caches, patient IDs, and individual scores remain local.

## Key results

The table reports the mean point estimate ± sample SD across the three seeds. The bracketed range is the minimum lower to maximum upper endpoint among the three separate seed-specific 95% patient-cluster bootstrap intervals. This **envelope is not a pooled confidence interval**.

| Horizon | Model | Calibrated Brier minus prevalence reference | Paired calibrated minus raw Brier | Fixed-bin ECE |
|---:|---|---:|---:|---:|
| 1 h | Static | 1.52757e-05 ± 1.2e-05 [2.74683e-06, 5.02364e-05] | -0.178258 ± 0.0055 [-0.187872, -0.170811] | 0.000958865 ± 0.00025 [0.000635109, 0.00133325] |
| 1 h | Temporal | 1.38428e-05 ± 1.2e-05 [-9.09856e-08, 4.68486e-05] | -0.111865 ± 0.0044 [-0.118331, -0.1038] | 0.000510198 ± 0.00012 [0.00028663, 0.000719086] |
| 3 h | Static | 4.15861e-05 ± 4.8e-05 [-4.97146e-06, 0.000162168] | -0.164243 ± 0.0028 [-0.170945, -0.158691] | 0.00237687 ± 0.00026 [0.00182328, 0.00297108] |
| 3 h | Temporal | 1.18642e-05 ± 1.7e-05 [-1.36512e-05, 6.55701e-05] | -0.10979 ± 0.0067 [-0.120664, -0.101935] | 0.00121073 ± 0.00016 [0.000718875, 0.00161489] |
| 6 h | Static | 9.2972e-05 ± 0.00012 [-4.02653e-05, 0.000409899] | -0.160562 ± 0.0065 [-0.171776, -0.15271] | 0.00452654 ± 0.00062 [0.00335067, 0.00577655] |
| 6 h | Temporal | 3.35222e-05 ± 7.9e-05 [-6.00674e-05, 0.000247561] | -0.115306 ± 0.0078 [-0.125397, -0.103347] | 0.00254608 ± 0.00026 [0.00190322, 0.00345831] |

## Interpretation

- **Calibration consistently improved Brier score versus raw class-weighted scores.** The paired calibrated-minus-raw Brier interval was below zero for every seed/model/horizon run. This is evidence that recalibration corrects the extreme raw probability scale in this benchmark; it is not evidence of clinical calibration.
- **Evidence against the constant-prevalence reference is less uniform.** The point estimates for calibrated Brier minus the observed-prevalence reference were usually positive, but many seed-specific bootstrap intervals crossed zero. At 1 hour, the static model’s intervals were above zero across all seeds; most 3-hour and 6-hour intervals overlapped zero. These comparisons use a reference computed from the evaluated cohort’s prevalence and are descriptive, not a deployable baseline fit independently of the test data.
- **Fixed-bin ECE remains small in absolute terms but increases with horizon and varies by model/seed.** ECE depends on the predefined bins and should not be interpreted alone. Mean predicted probabilities remain above observed prevalence in the aggregate results.
- The 200-replicate percentile intervals quantify patient-sampling uncertainty conditional on the fixed Set B cohort and the fitted models. They do not include uncertainty from model development, seed selection, dataset shift, label error, or prospective deployment. The three seeds are not independent cohorts.

## Next step

Define a utility-based operating-point framework before selecting any alert threshold. It should state the relative costs of missed forecast windows and alerts, report sensitivity/PPV/alerts per patient-day/window coverage together, and use a development-only patient-disjoint partition. No threshold may be selected on Set B; any chosen policy would require a new independent evaluation cohort.

## Limitations

- The target forecasts entry into the Challenge SepsisLabel-positive window, not independently observed biological onset; the Challenge label already incorporates a six-hour lead convention.
- Alerts outside forecast-positive windows are not verified clinical false alarms.
- Set B is a second Challenge training cohort, not prospective external clinical validation.
- No clinical safety, utility, or patient benefit is established.

**Research-only:** VITALIS is not a medical device or clinically validated decision-support system. Do not use its outputs to guide patient care.
