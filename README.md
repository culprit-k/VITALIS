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
- The online twin currently detects within-person deviation patterns. It does **not** yet estimate a calibrated probability of sepsis or forecast a validated 1–3 hour deterioration window.

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

## Development status

VITALIS now has retrospective static/temporal research workflows plus an initial streaming adaptive deviation component. The adaptive component is a software milestone, not a complete digital twin or clinical predictor. Clean-checkout reproducibility, current-head CI, security review, independent statistical/clinical review, and future external/ prospective validation remain separate gates. No claim of novelty or patentability is made. See [release-readiness audit](docs/RELEASE_READINESS_AUDIT.md), [reproducible workflow](docs/REPRODUCIBLE_WORKFLOW.md), [model card](docs/MODEL_CARD.md), and [cohort protocol](docs/COHORT_PROTOCOL.md).
