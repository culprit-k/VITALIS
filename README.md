# VITALIS

**VITALIS** is a research-first platform exploring adaptive physiological modeling for early prediction of sepsis-related clinical deterioration from longitudinal observations.

> **Research prototype only.** VITALIS is not a medical device or a clinically validated decision-support system. Do not use it to guide patient care.

## Research goals

- Build a reproducible, auditable cohort pipeline.
- Compare static, causal temporal, and experimental patient-specific baseline-deviation features.
- Implement an online adaptive physiological deviation layer while keeping deviation detection separate from supervised clinical-outcome prediction.
- Prevent patient leakage and label-timing errors.
- Evaluate discrimination, calibration, sensitivity, specificity, and aggregate alert behavior.
- Document uncertainty and limitations before considering any clinical translation.

## Repository layout

```text
docs/                 Research protocol, algorithm specs, model card, workflow
src/vitalis/          Reusable temporal features, validation, adaptive twin
scripts/              Dataset audit, training, comparisons, synthetic twin demo
configs/              Baseline experiment configuration
tests/                Unit and regression tests
dashboard/            Aggregate-only Streamlit evaluation dashboard
.github/workflows/    Automated tests
```

## Local workflow

Install and test:

```bash
python -m venv .venv
# Activate the environment, then:
pip install -e ".[dev]"
pytest
```

Keep the PhysioNet/CinC Challenge 2019 data outside Git and follow its access terms. Run the aggregate cohort inventory:

```bash
python scripts/build_cohort.py /path/to/psv_files --output outputs/cohort_inventory.json
```

Train the static baseline, temporal variant, matched comparison, or a deterministic subset experiment:

```bash
python scripts/train_baseline.py /path/to/psv_files --output outputs/static_metrics.json
python scripts/train_baseline.py /path/to/psv_files --temporal --output outputs/temporal_metrics.json
python scripts/train_baseline.py /path/to/psv_files --temporal --personalized --output outputs/personalized_metrics.json
python scripts/compare_models.py /path/to/psv_files --output outputs/model_comparison.json
python scripts/run_subset_experiment.py /path/to/psv_files --sample-size 1500 --sampling-seed 2026 --split-seed 42 --output outputs/subset_comparison.json
python scripts/train_horizon_model.py /path/to/psv_files --horizons 1 3 6 --seed 42 --threshold 0.5 --refractory-hours 6 --bootstrap-replicates 200 --output outputs/horizon_forecast_summary.json
python scripts/evaluate_horizon_cross_cohort.py --set-a-cache /path/outside/repo/cache_set_a --set-b-cache /path/outside/repo/cache_set_b --horizons 1 3 6 --seeds 42 123 2026 --threshold 0.5 --refractory-hours 6 --bootstrap-replicates 200 --output /path/outside/repo/horizon_cross_cohort.json
```

Run the synthetic streaming demonstration of the adaptive physiological twin:

```bash
python scripts/demo_adaptive_twin.py
```

This script uses generated values only. It illustrates baseline warm-up, deviation scoring, multisystem aggregation, and trajectory direction; it is not clinical evidence.

For the evaluation dashboard: `pip install -e ".[dashboard]"` then `streamlit run dashboard/app.py`. Upload aggregate metrics JSON only.\n\nFor the synthetic adaptive-twin sandbox: `streamlit run dashboard/twin_demo.py`. It uses generated signals only and shows heuristic trajectory behavior, not clinical predictions.

## Adaptive twin component

- [Algorithm and validation contract](docs/ADAPTIVE_TWIN_IMPLEMENTATION.md) defines the robust baseline, normalized deviation, multisystem aggregation, trajectory smoothing, output semantics, and next validation gates.\n- `src/vitalis/stream.py` adds a timestamped input contract with unit checks, freshness handling, quality flags, out-of-order rejection, and session reset; device-specific acquisition is still future work.
- [VITALIS-PB research specification](docs/VITALIS_PB_ALGORITHM.md) defines the separate retrospective patient-baseline feature experiment.
- The online twin combines a rolling robust baseline with a frozen initial reference and two-sided CUSUM to help expose gradual shifts, alongside multisystem aggregation and trajectory smoothing. It does **not** itself estimate a calibrated clinical risk.\n- `scripts/train_horizon_model.py` adds separate 1-, 3-, and 6-hour future-Challenge-label forecasting experiments with patient-disjoint splits and patient-level warning-burden metrics. `scripts/evaluate_horizon_cross_cohort.py` trains on a patient-disjoint Set A subset and evaluates all eligible Set B patients, with Set B used only for final evaluation. These horizons refer to entry into the challenge-positive label window, not independently observed sepsis onset. See [Horizon forecasting protocol](docs/HORIZON_FORECASTING.md) and [cross-cohort execution checklist](docs/HORIZON_CROSS_COHORT_EXECUTION.md).\n- [Full-cohort horizon results](docs/FULL_COHORT_HORIZON_CROSS_COHORT_RESULTS.md) records the completed 1/3/6-hour Set A→Set B evaluation across three seeds, including patient-level warning burden and limitations. The results do not support clinical use; raw caches and individual predictions remain local-only.

## Data safety and label semantics

**Do not commit raw patient data, derived patient-level records, individual predictions, credentials, or tokens.** Local `data/`, `outputs/`, `artifacts/`, and `.psv` files are ignored by Git.

The challenge `SepsisLabel` already uses a six-hour lead convention. Do not shift it a second time. A positive label should not be described as independently observed clinical onset.

## Research provenance

- [Plain-language project status](docs/PROJECT_STATUS.md) summarizes the current stage, findings, limitations, remaining release gates, and next steps.
- [Local experiment history](docs/LOCAL_EXPERIMENTS.md) records prior exploratory runs and their limitations.
- [Aggregate dataset inventory](results/dataset_inventory.json) records the verified local archive counts for training sets A and B; no raw or patient-level data are stored here.
- [Multi-seed experiment runner](scripts/run_experiment_suite.py) supports reproducible static-versus-temporal comparisons across patient-level split seeds.
- [Subset experiment runner](scripts/run_subset_experiment.py) deterministically samples patient files and writes aggregate-only matched comparison results.
- [Exact-source cross-cohort results](docs/FULL_COHORT_CROSS_COHORT_RESULTS.md) documents the Set-A-to-Set-B benchmark comparison and its limitations.
- [1,000-replicate patient-cluster uncertainty analysis](docs/CROSS_COHORT_BOOTSTRAP_RAW_AND_RECALIBRATED_1000.md) records raw and Set-A-validation-Platt-recalibrated comparisons across seeds 42, 123, and 2026. Row-level score archives remain local-only.
- For the accelerated uncertainty runner, install the optional extra with `pip install -e ".[bootstrap-accelerated]"`; use only local score archives stored outside the repository.
- [Structured historical results](results/local_experiment_summary.json) is an aggregate-only record of earlier experiments. These historical metrics are not automatically reproduced by the current workflow.
- [Fresh subset rerun](results/current_subset_rerun.json) records an earlier 1,500-patient experiment; its results are mixed and exploratory.
- [Three-seed subset experiment report](docs/MULTISEED_SUBSET_EXPERIMENT.md) and [aggregate metrics](results/multiseed_subset_summary.json) document a fresh comparison on the same deterministic 1,500-patient sample across split seeds 42, 123, and 2026.
- [Next steps and research roadmap](docs/NEXT_STEPS.md) lists pipeline fixes, reproducible validation, external validation, and IP safeguards.
- [Full-cohort rerun report](docs/FULL_COHORT_RERUN.md) and [aggregate JSON](results/full_cohort_rerun_2026-10-14.json) record the latest local rerun, with implementation provenance and limitations.
- [Combined A+B cohort evaluation](docs/FULL_AB_COMBINED_RESULTS.md) reports a patient-disjoint three-seed comparison using all 40,336 patients from both official training sets; [aggregate results](results/full_AB_combined_multiseed_2026-10-14.json).
- [Train-A/test-B cross-cohort evaluation](docs/FULL_COHORT_CROSS_COHORT_RESULTS.md) separately tests generalization across the benchmark's two cohorts.
- [Full-cohort future-label horizon results](docs/FULL_COHORT_HORIZON_CROSS_COHORT_RESULTS.md) records the Set A→Set B 1/3/6-hour run; [aggregate-only metrics and provenance](results/horizon_cross_cohort_2026-10-14.json).
- [Horizon calibration and operating-point protocol](docs/HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md) defines patient-disjoint Set-A-only Platt recalibration, a predeclared threshold grid, and evaluation-only Set B handling. Completed results: [interpretation report](docs/HORIZON_CALIBRATION_RESULTS_2026-10-15.md) and [aggregate-only JSON](results/horizon_calibration_summary_2026-10-15.json). Patient-cluster uncertainty intervals are summarized in [the uncertainty report](docs/HORIZON_CALIBRATION_UNCERTAINTY_RESULTS_2026-10-15.md) and [aggregate JSON](results/horizon_calibration_uncertainty_summary_2026-10-15.json).
- [Patient-cluster calibration uncertainty analysis](docs/HORIZON_CALIBRATION_UNCERTAINTY_RESULTS_2026-10-15.md) reports 200-replicate per-patient bootstrap intervals across the nine predeclared seed × horizon runs; [aggregate-only JSON](results/horizon_calibration_uncertainty_summary_2026-10-15.json).
- [Paired static-versus-temporal comparison](docs/HORIZON_PAIRED_MODEL_COMPARISON_RESULTS_2026-10-15.md) reports paired patient-cluster differences in AUROC, AUPRC, Brier score, and log loss; [aggregate-only JSON](results/horizon_paired_model_comparison_aggregate_2026-10-15.json).

## Development status

VITALIS now has retrospective static/temporal research workflows plus an initial streaming adaptive deviation component. The adaptive component is a software milestone, not a complete digital twin or clinical predictor. Clean-checkout reproducibility, current-head CI, security review, independent statistical/clinical review, and future external/ prospective validation remain separate gates. No claim of novelty or patentability is made. See [release-readiness audit](docs/RELEASE_READINESS_AUDIT.md), [reproducible workflow](docs/REPRODUCIBLE_WORKFLOW.md), [model card](docs/MODEL_CARD.md), and [cohort protocol](docs/COHORT_PROTOCOL.md).


### Utility-based operating-point analysis

The Set-A-only cost-sensitivity framework is documented in [Utility operating-point framework](docs/UTILITY_OPERATING_POINT_FRAMEWORK.md) and [the calibration/operating-point protocol](docs/HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md). The evaluator now adds patient-cluster uncertainty intervals and threshold-selection stability summaries on the untouched Set-A holdout (default 200 replicates; `--utility-bootstrap-replicates`); these quantify conditional development-sample variability, not clinical optimality. Exploratory nine-run point estimates and the source-provenance caveat are in [the utility results report](docs/HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md) and [aggregate-only JSON](results/horizon_utility_operating_point_aggregate_2026-10-15.json). The completed 200-replicate-per-fit Set-A-only uncertainty/stability analysis is in [the utility bootstrap report](docs/HORIZON_UTILITY_BOOTSTRAP_RESULTS_2026-10-15.md) and [aggregate-only summary](results/horizon_utility_bootstrap_summary_2026-10-15.json). Cost ratios are illustrative, not clinical recommendations. Set B remains evaluation-only.


### Independent evaluation gate

The next external evidence stage is specified in the [independent-cohort evaluation protocol](docs/INDEPENDENT_EVALUATION_PROTOCOL.md). It requires a frozen model/policy, a genuinely new cohort, an independently defined event time, and clinical/statistical and governance sign-off. This is a planning protocol only; no external or prospective validation has occurred. The [utility cost review checklist](docs/UTILITY_COST_REVIEW_CHECKLIST.md) is available for independent review.


### Independent evaluation freeze gate

The independent-evaluation protocol now has a machine-checkable scaffold: `configs/independent_evaluation_lockfile.template.json`, validated by `scripts/validate_evaluation_lockfile.py`. It refuses draft/unfrozen policies, Set B reuse, proxy-label/clinical-onset mismatches, and missing reviewer/governance sign-offs. The template is intentionally invalid until independently completed. Keep the completed lockfile and any cohort-identifying information in an approved private workspace; this validator is not an ethics approval or clinical-validity check. The lockfile now also requires explicit utility-cost scenarios, the primary scenario, a Set-A-only candidate-selection rule, and a clinical/statistical rationale or an explicit exploratory-only statement; the validator rejects Set B as the threshold-selection cohort.


- [Utility-based operating-point framework](docs/UTILITY_OPERATING_POINT_FRAMEWORK.md) documents the cost-sensitivity method for missed forecast windows versus alert burden. The exploratory nine-run aggregate analysis is complete: [results report](docs/HORIZON_UTILITY_OPERATING_POINT_RESULTS_2026-10-15.md) and [aggregate JSON](results/horizon_utility_operating_point_aggregate_2026-10-15.json). Cost ratios are illustrative, the run used a reconstructed working copy, and no threshold is selected from Set B. Independent cost review and a new evaluation cohort remain required.


### Repository data-artifact hygiene

CI runs \`scripts/check_repository_hygiene.py\` to reject common row-level data/cache/model-artifact file extensions and files larger than 5 MiB in the current working tree. This is a preventive current-tree check only; it does not scan Git history or replace secret scanning, data-governance review, or a manual privacy audit.


### Historical repository privacy audit

The current-tree guard is complemented by a full-history scanner: see [Git-history privacy audit](docs/GIT_HISTORY_PRIVACY_AUDIT.md) and run python scripts/audit_git_history.py from a complete clone with all relevant refs fetched. It reports artifact paths, oversized blobs, and high-confidence credential-pattern matches without printing credential values. Findings require human triage; a clean scan is not proof of no prior exposure.


## Clinical translation and regulatory readiness

The [clinical translation and regulatory roadmap](docs/CLINICAL_TRANSLATION_AND_REGULATORY_ROADMAP.md) defines the gates for moving from retrospective research toward a possible medical-device programme: intended-use definition, target-market classification, quality/design controls, risk management, independent clinical validation, prospective studies, regulatory authorization, and post-market monitoring. It is a planning document, not proof of compliance or clinical validation. VITALIS remains research-only; do not use it to guide patient care.


## Uzbekistan research-readiness gate

- [Uzbekistan research-readiness dossier](docs/UZBEKISTAN_RESEARCH_READINESS.md) records the proposed offline retrospective research boundary, current legal/regulatory source checks, data-protection and ethics questions, and stop conditions.
- [Machine-readable Uzbekistan readiness register](configs/regulatory/uzbekistan_research_readiness.json) tracks the evidence gates without implying approvals.
- Initial market: **Uzbekistan**. Initial intended deployment: **research only**, beginning with offline retrospective analysis of authorized, de-identified data.
- No live hospital feed, prospective patient monitoring, clinician-facing score, patient-care influence, or clinical marketing is authorized by this project status. The pathway for software-specific registration and study governance requires written confirmation from the competent Uzbekistan authorities and host institution.
- This documentation is a planning aid, not legal advice, medical-device classification, ethics approval, data-processing permission, regulatory authorization, or clinical validation.
