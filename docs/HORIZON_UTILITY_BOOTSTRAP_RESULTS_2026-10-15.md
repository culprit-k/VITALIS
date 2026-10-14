# Utility operating-point uncertainty and stability results

**Date:** 15 October 2026  
**Status:** exploratory Set-A development analysis completed; no clinical threshold selected.

## What was run

- Cohort: official Set A, 20,336 patients, 790,215 hourly rows, and 17,136 positive hourly Challenge labels.
- Patient-disjoint split: approximately 60% training, 20% Platt calibration, and 20% untouched development holdout; 4,027 holdout patients for each seed.
- Seeds: 42, 123, 2026. Horizons: 1, 3, 6 hours. Models: static and temporal.
- Completed 9 seed × horizon runs, 18 model fits, and 200 whole-patient bootstrap replicates for each model/seed/horizon fit (3,600 replicates total). Summed runtime was 151.741 seconds; no model-fit warnings were captured.
- Set B was not loaded or used in this analysis. No row-level predictions, patient identifiers, or cohort caches were exported.

**Provenance caveat:** this full-cohort analysis used the available reconstructed local working copy because a clean Git checkout could not be verified in the runtime. Results are not claimed as byte-identically verified execution of the checked-in source. Local environment: Python 3.13.5, NumPy 2.3.5, scikit-learn 1.8.0. SHA-256 of the local reconstructed files: `scripts/evaluate_horizon_calibration.py` `784b8cfac0a2e06e5978115b855af82ab379df4a76f78c820301ff2bdb55ad64`; `src/vitalis/utility.py` `5db1f2f6cc2e12baf472b670cbdd4dec002c84d1d640acbf31597a521ace7c4f`; `src/vitalis/horizon.py` `221c9cb49e94acf80f8b55e05e19df356b9b0e9ce78e0d63967f61fa69528126`; `src/vitalis/calibration_uncertainty.py` `b5aa0d69fe3de027fcf3ef10b5202793a29bc844c79686e5dad372b69cc376c6`. Set A cache metadata SHA-256: `67a1ba90a2d89abcb06ae71a08fe4ad63f97a65d6044b0f0a49acc9b4ff4407a`. These are provenance hashes for the local working copy, not claims that the files match GitHub blobs. The committed aggregate artifact records this limitation.

## Operating-point trade-offs

The table summarizes six seed × model runs per horizon. “Interval envelope” means the minimum lower and maximum upper endpoints across those six run-specific 95% patient-cluster bootstrap intervals. These envelopes are descriptive and are **not pooled confidence intervals**.

| Horizon | Threshold | Row sensitivity, mean (envelope) | Row PPV, mean (envelope) | Alerts / at-risk patient-day, mean (envelope) | Forecast-window coverage, mean (envelope) |
|---:|---:|---:|---:|---:|---:|
| 1 h | 0.005 | 25.8% (16.2–39.3%) | 1.38% (1.04–1.90%) | 0.315 (0.172–0.519) | 6.2% (2.4–10.6%) |
| 3 h | 0.005 | 81.3% (71.2–87.7%) | 1.17% (0.88–1.48%) | 2.61 (2.20–3.03) | 46.3% (37.2–54.6%) |
| 3 h | 0.01 | 42.0% (28.8–58.8%) | 3.02% (2.41–3.90%) | 0.633 (0.414–0.862) | 26.2% (18.2–35.5%) |
| 6 h | 0.005 | 98.5% (94.9–99.9%) | 1.45% (1.22–1.70%) | 4.20 (4.07–4.30) | 99.3% (96.6–100%) |
| 6 h | 0.01 | 82.7% (73.7–88.8%) | 2.37% (1.71–2.98%) | 2.68 (2.25–3.16) | 89.7% (82.8–95.6%) |
| 6 h | 0.05 | 14.2% (7.2–24.1%) | 10.9% (7.0–17.5%) | 0.101 (0.046–0.202) | 16.5% (9.0–26.8%) |

Sensitivity and PPV are row-level metrics; coverage is the fraction of contiguous future-positive label windows with at least one qualifying alert. They are different estimands. The pattern shows the expected trade-off: for example, at 6 hours the 0.005 threshold covers nearly all target windows but generates about 4.2 alerts per at-risk patient-day with PPV around 1.45%; 0.05 reduces burden but covers only about 16.5% of windows. None is a clinically acceptable threshold by virtue of these results.

## Sensitivity to assumed costs

The cost proxy is:

\`weighted cost = missed-window cost × missed forecast-positive windows + alert cost × all alerts\`

Missed-window cost is expressed relative to the cost assigned to one alert. The five cost ratios are illustrative engineering scenarios, not costs elicited from clinicians, patients, or health systems.

| Missed-window cost per alert-cost unit | Point-estimate candidate threshold across 18 runs | Mean bootstrap selection fraction |
|---:|---|---|
| 1 | 0.5 in 18/18 runs | 0.5: 98.97% |
| 10 | 0.5 in 12/18; 0.05 in 6/18 | 0.5: 70.31%; 0.05: 29.69% |
| 100 | 0.01 in 16/18; 0.005 in 2/18 | 0.01: 86.17%; 0.005: 10.94% |
| 500 | 0.005 in 11/18; 0.001 in 7/18 | 0.005: 59.81%; 0.001: 37.50% |
| 1,000 | 0.001 in 12/18; 0.005 in 6/18 | 0.001: 68.61%; 0.005: 31.31% |

The candidate changes when the assumed cost ratio changes. This is evidence that an operating point cannot be chosen responsibly without an independently justified cost/utility framework. Bootstrap selection frequency measures resampling stability under those assumptions; it is not the probability that a threshold is clinically optimal.

## Interpretation and limitations

- The outcome is entry into the Challenge SepsisLabel-positive window, not independently observed biological sepsis onset. The Challenge label incorporates a six-hour lead convention.
- Alerts outside a forecast-positive window are not verified clinical false alarms.
- The bootstrap is conditional on the fitted model, split, endpoint, threshold grid, refractory interval, and assumed cost ratio. It does not account for model-selection uncertainty, domain shift, endpoint validity, or uncertainty in the costs.
- Set A is development data. Set B has already been inspected for earlier experiments and must not be reused for threshold selection. A genuinely new independent cohort with independently defined/adjudicated event timing is required for final evaluation.
- The run's reconstructed-source provenance remains a reproducibility limitation. A fresh shallow/filtered clone was retried on 15 October 2026 and failed with `Could not resolve host: github.com`; no partial checkout was left behind. A clean checkout and fresh cache rebuild remain required when network access permits.
- Independent clinical/statistical review, governance/ethics determinations, and any prospective study approvals remain outstanding.

Machine-readable aggregate summary: [utility bootstrap summary](../results/horizon_utility_bootstrap_summary_2026-10-15.json).

## Software validation checkpoint

- The available reconstructed local suite passed 28 tests with `PYTHONPATH=src`; `compileall` passed for the available `src`, `scripts`, and `tests` trees.
- GitHub Actions passed on code-bearing PR head `86776762479dd450e20821da8e6f0b50c482e21d` (run [38639673606](https://github.com/culprit-k/VITALIS/actions/runs/38639673606)): 170 tests passed, compile and synthetic stream smoke tests passed, repository-artifact hygiene passed, and the reachable-history audit reported zero configured-pattern findings in 563 commits / 544 unique blobs among fetched refs.
- These checks validate software behavior and configured preventive gates; they do not close the clean local checkout/fresh-cache reproduction or independent clinical/statistical/governance gates.

**Research-only:** VITALIS is not clinically validated and must not guide patient care.
