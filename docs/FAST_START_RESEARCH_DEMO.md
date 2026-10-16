# VITALIS fast-start guide

**Purpose:** run the software research prototype locally and verify the interface before doing any cohort analysis. This guide does not turn VITALIS into a clinically usable predictor.

## 1. Requirements

- Python 3.11 recommended for the locked research workflows.
- Git.
- A terminal.
- For the interactive demos, install the optional Streamlit dashboard dependencies.

## 2. Install and verify

From a local clone of the repository:

```bash
git clone https://github.com/culprit-k/VITALIS.git
cd VITALIS
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`

Install the package, tests, and dashboard:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev,dashboard]"
python scripts/doctor.py
python scripts/doctor.py --dashboard
python -m pytest
```

The doctor command checks the supported Python version, core dependencies, and imports for the twin, timestamped stream, integrated interface, and aggregate-reporting modules. The `--dashboard` option also checks that Streamlit is installed. It does not assess model quality or clinical readiness.

Do not proceed to expensive cohort runs if the environment check or test suite fails. Save the failing output and fix the underlying issue first.

## 3. Start the interactive synthetic twin demo

```bash
streamlit run dashboard/twin_demo.py
```

Open the local URL printed by Streamlit (usually `http://localhost:8501`). Change the random seed to explore generated signals and observe how the heuristic baseline-deviation trajectory changes.

**This demo generates synthetic observations only.** It does not load a trained sepsis predictor, produce a calibrated clinical risk, or provide patient-care recommendations.

To run the command-line synthetic integration demo instead:

```bash
python scripts/demo_integrated_inference.py
```

The supervised probabilities should remain unavailable unless a frozen predictor is explicitly supplied with matching model, calibration, and feature-schema metadata. Do not replace missing probabilities with zero.

## 4. View aggregate experiment reports

Start the reporting dashboard:

```bash
streamlit run dashboard/app.py
```

Upload an **aggregate-only JSON report** produced by a VITALIS evaluation workflow. The dashboard rejects unsupported report schemas and enforces a 10 MiB file limit.

Never upload raw patient records, row-level predictions, patient identifiers, feature caches, or individual score archives. Keep source datasets and generated cohort caches outside the repository.

## 5. Check current project status and release gates

Read [Project Status](PROJECT_STATUS.md) before interpreting results. It records the latest verified main commit, the older full-cohort run's exact source SHA, and the remaining release blockers.

## 6. Run research analysis only after setup passes

Use the documented protocols in:

- [Reproducible workflow](REPRODUCIBLE_WORKFLOW.md)
- [Strict source reproducibility runbook](STRICT_SOURCE_REPRODUCIBILITY_RUNBOOK.md)
- [Calibration and operating-point results](PREVALENCE_AWARE_CALIBRATION_ANALYSIS_2026-10-16.md)
- [Software prototype release gate](SOFTWARE_PROTOTYPE_RELEASE_GATE.md)

For full-cohort runs, use the pinned workflow and verify source/environment manifests, official cohort counts, schema, patient-disjoint partitions, evaluation-only handling, aggregate artifact contents, and checksums. Do not use Set B to tune a model, calibrator, feature set, or threshold.

## Troubleshooting

- **Import error for `vitalis`:** activate the virtual environment and repeat `python -m pip install -e ".[dev,dashboard]"`.
- **Doctor reports a missing dependency:** activate the environment and rerun the install command above.
- **Streamlit command not found:** confirm the environment is active and install the dashboard extra.
- **Tests fail:** do not start the full cohort workflow. Record the failing test and fix it first.
- **No trained supervised model:** this is expected in the synthetic demo. Probabilities are intentionally unavailable; the demo is not a patient risk calculator.
- **Dataset path or cache missing:** follow the cohort workflow documentation and keep data/caches outside Git.

## Safety boundary

VITALIS currently supports research software demonstrations and retrospective benchmark analysis. It is not a medical device or a clinically validated decision-support system. The Challenge endpoint represents entry into a benchmark positive-label window, not independently adjudicated biological sepsis onset. Do not use any output for diagnosis, triage, treatment, or patient-care decisions. External validation, independent review, governance approval, and prospective evaluation remain separate requirements.
