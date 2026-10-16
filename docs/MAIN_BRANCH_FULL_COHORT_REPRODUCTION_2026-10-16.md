# Main-branch clean-checkout full-cohort reproduction — 16 October 2026

## Execution record

- **Workflow:** [full-cohort reproduction run 160](https://github.com/culprit-k/VITALIS/actions/runs/38889950689)
- **Result:** success; all workflow steps completed.
- **Source commit:** `426ac5dd2a8076fb192bcebd0b1c8f838bf72906` on `main`.
- **Environment:** GitHub-hosted Ubuntu runner, Python 3.11.17, baseline-compatible OpenBLAS numerical kernel.
- **Data:** official PhysioNet/CinC Challenge 2019 Set A and Set B, downloaded during the workflow to ephemeral runner storage.
- **Protocol:** horizons 1/3/6 hours; seeds 42, 123, 2026; static and temporal logistic regression; fixed reference threshold 0.5; six-hour alert refractory interval; 200 patient-cluster bootstrap replicates.
- **Artifact:** [aggregate-only workflow artifact](https://github.com/culprit-k/VITALIS/actions/runs/38889950689/artifacts/12042469450). The artifact contains aggregate metrics and provenance only; no raw cohort files, feature caches, patient identifiers, or patient-level predictions.
- **Baseline reconciliation:** PASS — 42/42 mean/sample-SD pairs and 84/84 scalar values matched under the previously frozen six-decimal rule; zero mismatches.

This is the first recorded successful full-cohort clean-checkout run on the integrated `main` commit above. It supersedes the earlier status that this exact run was pending; it does not replace or rewrite older historical artifacts.

## Cohort integrity

| Cohort | Patient files | Hourly rows | Positive source labels | Source columns | Malformed rows | Nonbinary labels | Label reversions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 | 41 | 0 | 0 | 0 |
| Set B | 20,000 | 761,995 | 10,780 | 41 | 0 | 0 | 0 |

Fresh Set A and Set B feature caches were built in disjoint chunks and passed source/cache fingerprint and patient-row ordering audits. Set A was split by patient into model-fit and unused held-out partitions. Set B remained evaluation-only: no fitting, feature selection, calibration fitting, or threshold selection used Set B.

## Primary cross-cohort results

The table reports mean ± sample standard deviation across seeds 42, 123, and 2026. The endpoint is entry into the Challenge `SepsisLabel`-positive window over the stated future horizon, excluding current-positive rows and incomplete patient tails.

| Horizon | Model | AUROC mean ± SD | AUPRC mean ± SD | Brier mean ± SD | Sensitivity at 0.5 | PPV at 0.5 | Alerts / at-risk patient-day mean ± SD | Positive-window coverage mean ± SD |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 h | Static | 0.663385 ± 0.002217 | 0.003793 ± 0.000219 | 0.193701 ± 0.005846 | 0.528473 | 0.002476 | 1.792175 ± 0.142768 | 0.120058 ± 0.003821 |
| 1 h | Temporal | 0.656890 ± 0.010999 | 0.003170 ± 0.000148 | 0.131964 ± 0.008834 | 0.400798 | 0.003191 | 1.461593 ± 0.113243 | 0.117156 ± 0.012230 |
| 3 h | Static | 0.681317 ± 0.004288 | 0.013583 ± 0.000165 | 0.180597 ± 0.005457 | 0.521326 | 0.008421 | 1.506671 ± 0.038862 | 0.328618 ± 0.007135 |
| 3 h | Temporal | 0.680004 ± 0.014513 | 0.012639 ± 0.000478 | 0.131344 ± 0.003472 | 0.415134 | 0.010771 | 1.276286 ± 0.080706 | 0.293435 ± 0.014854 |
| 6 h | Static | 0.686763 ± 0.004962 | 0.028594 ± 0.000336 | 0.174550 ± 0.006209 | 0.514710 | 0.019026 | 1.399416 ± 0.051793 | 0.601741 ± 0.017410 |
| 6 h | Temporal | 0.686375 ± 0.013809 | 0.026433 ± 0.001021 | 0.142186 ± 0.005156 | 0.445697 | 0.022373 | 1.256563 ± 0.105401 | 0.568009 ± 0.020328 |

### Primary interpretation

- Temporal features lower Brier scores and reduce alert burden relative to the static model, but also have lower sensitivity and lower positive-window coverage at the fixed 0.5 threshold.
- Static AUPRC is higher than temporal AUPRC at all three horizons. AUROC differences are small and not a consistent temporal win.
- PPV remains very low (about 0.25%–2.24% across these rows), reflecting the severe class imbalance and fixed reference operating point. Alerts outside a Challenge-positive future window are not verified clinical false alarms.
- The threshold 0.5 and six-hour refractory interval are research defaults, not clinically selected operating settings.

## Predeclared patient-relative physiology ablation

The causal patient-relative feature candidate used prior rows only, required at least five observations, and added relative physiology features for HR, O2 saturation, temperature, SBP, MAP, DBP, and respiratory rate. Set B remained evaluation-only.

| Horizon | Model | Mean AUROC | Mean AUPRC | Mean Brier |
|---:|---|---:|---:|---:|
| 1 h | Static baseline | 0.663385 | 0.003793 | 0.193701 |
| 1 h | Temporal baseline | 0.656890 | 0.003170 | 0.131964 |
| 1 h | Temporal + patient-relative physiology | 0.666296 | 0.003478 | 0.138101 |
| 3 h | Static baseline | 0.681317 | 0.013583 | 0.180597 |
| 3 h | Temporal baseline | 0.680004 | 0.012639 | 0.131344 |
| 3 h | Temporal + patient-relative physiology | 0.689820 | 0.013419 | 0.135656 |
| 6 h | Static baseline | 0.686763 | 0.028594 | 0.174550 |
| 6 h | Temporal baseline | 0.686375 | 0.026433 | 0.142186 |
| 6 h | Temporal + patient-relative physiology | 0.695591 | 0.027696 | 0.145115 |

The patient-relative candidate improves AUROC over the temporal baseline at each horizon and improves AUPRC over the temporal baseline, but **worsens Brier score at every horizon**. Static AUPRC remains slightly higher than the patient-relative candidate at all horizons. The paired patient-cluster bootstrap for candidate-minus-temporal Brier was positive at each horizon (mean differences: +0.005086 at 1 h, +0.003195 at 3 h, +0.003153 at 6 h; each 95% percentile interval was above zero). This is a discrimination-versus-probability-quality tradeoff, not grounds to promote the candidate as a winner.

## Patient-disjoint Set A Platt calibration experiment

Platt calibration was fit using a patient-disjoint Set A calibration partition. The table shows means over the three seeds for the class-balanced models, before and after Platt scaling.

| Horizon | Model | Raw Brier | Platt Brier | Raw AUROC | Platt AUROC | Mean sensitivity after Platt at 0.5 |
|---:|---|---:|---:|---:|---:|---:|
| 1 h | Temporal baseline | 0.112765 | 0.001270 | 0.659459 | 0.659459 | 0.000000 |
| 1 h | Temporal + patient-relative physiology | 0.119062 | 0.001268 | 0.668269 | 0.668269 | 0.000000 |
| 3 h | Temporal baseline | 0.115349 | 0.003852 | 0.681265 | 0.681265 | 0.000125 |
| 3 h | Temporal + patient-relative physiology | 0.119650 | 0.003868 | 0.691350 | 0.691350 | 0.000000 |
| 6 h | Temporal baseline | 0.133599 | 0.008124 | 0.683405 | 0.683405 | 0.000713 |
| 6 h | Temporal + patient-relative physiology | 0.136159 | 0.008176 | 0.693398 | 0.693398 | 0.001490 |

Although Platt scaling sharply reduces Brier score for the class-balanced models, the fixed 0.5 threshold then yields essentially zero sensitivity. AUROC is unchanged, as expected for a monotonic score transformation. Under this low-prevalence target, Brier score can look excellent when predicted probabilities are compressed near zero; that does not establish useful alerting or adequate calibration. Do not choose a replacement threshold on Set B. Any operating-point selection must occur on Set A development data and then be frozen before a new evaluation.

## Limitations and release disposition

- The Challenge `SepsisLabel` already incorporates a six-hour lead convention. This experiment predicts entry into its positive window, not independently adjudicated biological sepsis onset.
- Set B is another cohort from the same Challenge benchmark, not an independent prospective clinical cohort.
- No prospective silent-mode study, independent external clinical validation, clinical utility study, or patient-benefit evidence has been completed.
- The adaptive twin's unitless heuristic trajectory score is not a sepsis probability; a frozen supervised model artifact is not wired into the twin demo.
- Independent statistical/methods review and the final human release decision remain outstanding.

**Disposition:** the main-branch full-cohort software reproduction and frozen baseline reconciliation passed. VITALIS remains a research prototype only; these results do not support clinical use, regulatory clearance, patentability, or clinical-readiness claims.
