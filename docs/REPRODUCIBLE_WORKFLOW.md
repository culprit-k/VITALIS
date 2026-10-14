# Reproducible Local Workflow

## 1. Install

```bash
python -m venv .venv
# Activate the environment
pip install -e ".[dev]"
pytest
```

## 2. Keep the dataset outside Git

Obtain the PhysioNet/CinC Challenge 2019 data from the official source and comply with its access and use terms: https://physionet.org/content/challenge-2019/1.0.0/

Place the extracted per-patient `.psv` files in a local directory. Do not place raw or patient-level data in the repository.

## 3. Audit cohort integrity

```bash
python scripts/audit_dataset.py /path/to/psv_files --output outputs/audit.json
python scripts/build_cohort.py /path/to/psv_files --output outputs/cohort_inventory.json
```

Review row counts, patient counts, label prevalence, schema variation, and missingness before modeling. Outputs should remain local and aggregate-only.

## 4. Train a static baseline

```bash
python scripts/train_baseline.py /path/to/psv_files --seed 42 --output outputs/static_metrics.json
```

## 5. Train the temporal feature comparison

```bash
python scripts/train_baseline.py /path/to/psv_files --temporal --seed 42 --output outputs/temporal_metrics.json
```

The script uses patient-level group splits, training-only preprocessing, and a fixed 0.5 reference threshold. The validation split is reserved for later threshold selection; the current script deliberately does not tune the test threshold. Temporal features use current and prior observations only.

## 6. Run a matched static-versus-temporal comparison

```bash
python scripts/compare_models.py /path/to/psv_files --seed 42 --output outputs/model_comparison.json
```

The comparison runs both variants with the same deterministic patient split strategy and reports temporal-minus-static metric deltas. Deltas are descriptive; they do not establish clinical benefit.

The training report includes 95% patient-cluster bootstrap intervals for held-out row-level metrics (200 patient-resampling replicates by default). Intervals express between-patient sampling uncertainty; they do not make row-level results event-level metrics.

The training report also includes a refractory-period alert-burden summary and coverage of contiguous challenge-positive label episodes. These are label-window analyses, not true clinical event sensitivity or false-alarm rates, because the challenge label is not independently observed onset.

## 7. View aggregate results

Install the optional dashboard dependency and launch:

```bash
pip install -e ".[dashboard]"
streamlit run dashboard/app.py
```

Upload only aggregate metrics JSON. Do not upload patient-level records or predictions.

## Important interpretation notes

- The challenge `SepsisLabel` already uses a six-hour lead convention. Do not shift it again.
- The first positive challenge label is not independently observed clinical onset.
- Row-level AUROC/AUPRC and a fixed threshold do not establish event-level performance or clinical utility.
- The cohort must be externally validated before any clinical translation is considered.
