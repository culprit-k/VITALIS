# VITALIS

**VITALIS** is a research-first platform exploring adaptive physiological modeling for early prediction of sepsis-related clinical deterioration from longitudinal observations.

> **Research prototype only.** VITALIS is not a medical device or a clinically validated decision-support system. Do not use it to guide patient care.

## Research goals

- Build a reproducible, auditable cohort pipeline.
- Compare static, causal temporal, and experimental patient-specific baseline-deviation features.
- Prevent patient leakage and label-timing errors.
- Evaluate discrimination, calibration, sensitivity, specificity, and aggregate alert behavior.
- Document uncertainty and limitations before considering any clinical translation.

## Repository layout

```text
docs/                 Research protocol, data dictionary, model card, workflow
src/vitalis/          Reusable temporal-feature and validation code
scripts/              Dataset audit, cohort inventory, training, comparison
configs/              Baseline experiment configuration
tests/                Unit tests
 dashboard/           Optional aggregate-only Streamlit dashboard
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

For the dashboard: `pip install -e ".[dashboard]"` then `streamlit run dashboard/app.py`. Upload aggregate metrics JSON only.

## Data safety and label semantics

**Do not commit raw patient data, derived patient-level records, individual predictions, credentials, or tokens.** Local `data/`, `outputs/`, `artifacts/`, and `.psv` files are ignored by Git.

The challenge `SepsisLabel` already uses a six-hour lead convention. Do not shift it a second time. A positive label should not be described as independently observed clinical onset.

## Research provenance

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
- [VITALIS-PB algorithm specification](docs/VITALIS_PB_ALGORITHM.md) defines the causal patient-baseline deviation features and their limitations.
- [Next steps and research roadmap](docs/NEXT_STEPS.md) lists pipeline fixes, reproducible validation, external validation, and IP safeguards.
- [Full-cohort rerun report](docs/FULL_COHORT_RERUN.md) and [aggregate JSON](results/full_cohort_rerun_2026-10-14.json) record the latest local rerun, with implementation provenance and limitations.
- [Combined A+B cohort evaluation](docs/FULL_AB_COMBINED_RESULTS.md) reports a patient-disjoint three-seed comparison using all 40,336 patients from both official training sets; [aggregate results](results/full_AB_combined_multiseed_2026-10-14.json).
- [Train-A/test-B cross-cohort evaluation](docs/FULL_COHORT_CROSS_COHORT_RESULTS.md) separately tests generalization across the benchmark's two cohorts.

## Development status

This repository contains a research scaffold and reproducible baseline workflows. Model performance has not been asserted as clinically useful or externally validated. No claim of novelty or patentability is made. See [`docs/REPRODUCIBLE_WORKFLOW.md`](docs/REPRODUCIBLE_WORKFLOW.md), [`docs/MODEL_CARD.md`](docs/MODEL_CARD.md), and [`docs/COHORT_PROTOCOL.md`](docs/COHORT_PROTOCOL.md).
