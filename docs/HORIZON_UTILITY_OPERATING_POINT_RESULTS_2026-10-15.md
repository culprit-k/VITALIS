# Utility-based horizon operating-point results (15 October 2026)

**Status:** exploratory Set-A development analysis completed across the nine predeclared seed × horizon combinations. These results do not select a clinical threshold.

## Execution and protocol

- Cohorts: Set A 20,336 patients / 790,215 rows / 17,136 positive hourly labels; Set B 20,000 patients / 761,995 rows / 10,780 positive hourly labels.
- Seeds: 42, 123, 2026; horizons: 1, 3, 6 hours; static and temporal models.
- For each seed/horizon, patients were split within Set A into approximately 60% training, 20% Platt calibration, and 20% untouched operating-point holdout. Recalibration used Set-A calibration patients only.
- Threshold grid: 0.001, 0.005, 0.01, 0.05, 0.5; six-hour alert refractory interval.
- Cost sensitivity scenarios: missed-window cost of 1, 10, 100, 500, or 1,000 units relative to alert cost 1. These are deliberately broad **illustrative assumptions**, not clinician-elicited costs.
- All nine runs completed, 18 base-model fits, 249.7 seconds summed runtime, and zero captured model-fit warnings. Twenty bootstrap replicates were used in these utility-focused reruns for ancillary uncertainty summaries; those intervals are preliminary and are not used by the deterministic cost ranking.
- Aggregate-only output: [utility operating-point JSON](../results/horizon_utility_operating_point_aggregate_2026-10-15.json).

## Main findings

Means below are across the three Set-A patient-split seeds. Sensitivity and PPV are row-level future-label metrics; window coverage and alert burden are patient-level metrics.

| Horizon | Model | Threshold | Sensitivity | PPV | Alerts / at-risk patient-day | Window coverage |
|---|---|---:|---:|---:|---:|---:|
| 1 h | Static | 0.001 | 96.2% | 0.24% | 4.04 | 19.0% |
| 1 h | Static | 0.005 | 24.0% | 1.43% | 0.29 | 5.8% |
| 1 h | Temporal | 0.001 | 96.2% | 0.26% | 3.91 | 18.6% |
| 1 h | Temporal | 0.005 | 27.7% | 1.34% | 0.34 | 6.6% |
| 3 h | Static | 0.001 | 100.0% | 0.66% | 4.28 | 50.9% |
| 3 h | Static | 0.005 | 80.8% | 1.10% | 2.74 | 47.4% |
| 3 h | Temporal | 0.001 | 100.0% | 0.67% | 4.28 | 50.6% |
| 3 h | Temporal | 0.005 | 81.8% | 1.25% | 2.47 | 45.1% |
| 6 h | Static | 0.005 | 98.6% | 1.43% | 4.23 | 99.2% |
| 6 h | Static | 0.01 | 82.4% | 2.22% | 2.82 | 88.7% |
| 6 h | Temporal | 0.005 | 98.4% | 1.47% | 4.16 | 99.3% |
| 6 h | Temporal | 0.01 | 83.1% | 2.52% | 2.53 | 90.7% |

### Trade-off interpretation

- **1-hour target:** the lowest tested threshold produced roughly 3.9–4.0 alerts per at-risk patient-day but covered only about 19% of future-positive windows. Raising the threshold sharply reduced burden but also reduced coverage. This is not a satisfactory established operating point.
- **3-hour target:** at threshold 0.005, coverage was about 45–47% with 2.5–2.7 alerts per at-risk patient-day. At 0.01, burden fell to about 0.62–0.65 per day, but coverage fell to roughly 25–27%.
- **6-hour target:** threshold 0.005 covered about 99% of windows but generated about 4.2 alerts per at-risk patient-day and had PPV near 1.4%. Threshold 0.01 reduced burden to about 2.5–2.8 alerts per day, with coverage around 89–91%. At threshold 0.05, alert burden was about 0.10 per day, but coverage fell to around 16–17%.
- At missed-window cost ratio 1, the mathematical minimum was generally the near-zero-alert threshold 0.5. At ratio 100, threshold 0.01 was the lowest-cost development candidate across seeds for most model/horizon combinations. At ratios 500–1,000, lower thresholds more often won, but several combinations disagreed across seeds. This demonstrates that the result depends strongly on the assumed costs; it does not identify an objectively correct ratio or a clinically appropriate threshold.

## Provenance and limitations

**Provenance caveat:** these full-cohort utility runs used the available reconstructed local working copy and local cohort caches because a clean checkout could not be verified. They are not claimed as byte-identically verified executions of the checked-in source. The checked-in utility framework and evaluator integration separately passed GitHub Actions; the final checked-in code-bearing commit is linked from the pull request.

Set B remained evaluation-only for this analysis: no fitting, recalibration, threshold ranking, or utility selection used it. No raw patient records, caches, patient identifiers, or row-level predictions were committed.

The Challenge target forecasts entry into the SepsisLabel-positive window, not independently observed biological sepsis onset. Alerts outside target-positive windows are not verified clinical false alarms. Cost ratios are not clinically or economically validated and omit alarm fatigue, staffing, treatment harms, delayed treatment, patient preferences, and competing outcomes. A frozen development policy would need a new independent cohort and clinical/statistical governance review. VITALIS remains research-only and is not clinically validated.
