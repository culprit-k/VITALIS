# VITALIS research prototype handover — 16 October 2026

**Repository:** https://github.com/culprit-k/VITALIS  
**Default branch:** `main`  
**Main integration commit:** `e4dd10bff7159a7bf419ed2ccae690edd0dcb479`  
**Reproducibility changes PR:** https://github.com/culprit-k/VITALIS/pull/2 (merged)  
**Disposition:** reproducible research prototype; not a clinical release.

## Current execution evidence

The following evidence was verified across the reproducibility branch and subsequent `main` integration on 16 October 2026. The current `main` commit has a passing standard test workflow; the full-cohort acceptance evidence below is from the pinned Python 3.11 clean-checkout workflow on the documented reproducibility commit, not a new full-cohort run on `main`:

- Standard CI, including compileall, source manifest, repository hygiene, reachable-history audit, synthetic twin stream demo, integrated-inference demo, and pytest: https://github.com/culprit-k/VITALIS/actions/runs/38880081362 — passed on the reproducibility branch.
- Reporting/dashboard tests: https://github.com/culprit-k/VITALIS/actions/runs/38880081293 — passed on the reproducibility branch.
- Pinned Python 3.11 clean-checkout full-cohort workflow: https://github.com/culprit-k/VITALIS/actions/runs/38880081272 — passed on the reproducibility branch.
- Full-cohort pytest: 218 passed.
- Pinned Python 3.11 reconciliation: 42/42 mean/sample-standard-deviation pairs and 84/84 scalar values matched the preserved aggregate under the existing six-decimal rule; zero mismatches. The workflow retained an aggregate-only artifact with provenance. Artifact: https://github.com/culprit-k/VITALIS/actions/runs/38880081272/artifacts/12037367815
- Python 3.13 diagnostic: https://github.com/culprit-k/VITALIS/actions/runs/38880082111 — failed at the baseline-compatible CPU preflight because the runner did not expose required AVX-512F. It stopped before Python setup, dataset download, or evaluation. This is a runner-compatibility diagnostic, not evidence of model failure, and Python 3.13 is not the acceptance environment.

The official Challenge 2019 cohort counts recorded by the source audit are:

| Cohort | Patients | Hourly rows | Positive hourly labels |
|---|---:|---:|---:|
| Set A | 20,336 | 790,215 | 17,136 |
| Set B | 20,000 | 761,995 | 10,780 |

Set B is held out for retrospective evaluation within the same challenge benchmark; it is not independent prospective clinical validation.

## Run the software locally

Use Python 3.11 for the pinned reproduction workflow. Keep downloaded cohort files, caches, row-level predictions, and outputs outside the Git repository.

### Install and test

```bash
python -m venv .venv
# Activate .venv using your operating system's activation command
python -m pip install -e ".[dev,bootstrap-accelerated]"
python -m compileall -q src scripts dashboard tests
python scripts/verify_source_manifest.py --output /tmp/vitalis-source-manifest.json
python scripts/check_repository_hygiene.py
python scripts/audit_git_history.py --json-output /tmp/vitalis-history-audit.json
pytest
```

### Run synthetic demos

```bash
python scripts/demo_adaptive_twin.py --seed 2026
python scripts/demo_integrated_inference.py
```

These use synthetic inputs. They demonstrate software behavior and output contracts, not clinical prediction accuracy.

### Run the dashboards

```bash
python -m pip install -e ".[dashboard]"
streamlit run dashboard/app.py
```

For the synthetic twin sandbox, use a second terminal:

```bash
streamlit run dashboard/twin_demo.py
```

The evaluation dashboard accepts aggregate metrics only. Do not upload patient-level predictions or identifiers.

### Reproduce the full-cohort experiment

Obtain the PhysioNet/CinC Challenge 2019 dataset under its access terms, then run the committed clean-checkout workflow or follow `docs/EXACT_CHECKOUT_REPRODUCTION.md` and `docs/HORIZON_CROSS_COHORT_EXECUTION.md`. The automated workflow downloads both official cohorts to ephemeral runner storage, rebuilds fresh caches, checks source and cache integrity, evaluates predeclared 1/3/6-hour horizons over three seeds, reconciles aggregate outputs, and retains aggregate-only artifacts. Do not commit raw data, caches, row-level predictions, or credentials.

## Remaining release blockers

1. **Independent review:** Issue #4 tracks the required independent statistical/methods and provenance review. No independent reviewer sign-off is present. Automated checks are not a substitute.
2. **Model behavior:** physiology features improved some discrimination metrics but worsened Brier score. No model is promoted as a probability-quality winner.
3. **Calibration/operating point:** the Set-A Platt experiment has near-zero sensitivity at the fixed 0.5 reference threshold. The threshold is experimental, not clinically selected; alert burden/PPV remains a major limitation.
4. **Twin integration:** the adaptive twin produces a unitless heuristic deviation/trajectory score, not a sepsis probability. A frozen supervised model artifact is not wired into the demo, so trained-model inference is not available through that demo.
5. **Clinical evidence:** no prospective silent-mode study, independent external clinical validation, clinical utility study, or patient-benefit evidence exists. No claim of patentability, regulatory clearance, or clinical readiness is made here.
6. **Repository integration:** PR #2 is merged and the reproducibility work is present on `main`. That merge is a code/documentation integration milestone, not clinical release approval. A new full-cohort run on `main` and independent human review remain separate gates.

## Hardware and deployment boundary

No patient-connected sensor hardware, embedded firmware, clinical monitor integration, or bedside deployment has been built or validated in this repository. Any hardware phase must start with a non-patient bench prototype and a documented interface/safety plan; it must not be connected to patients or used for treatment decisions. Sensor accuracy, synchronization, missing-data behavior, electrical safety, cybersecurity, and device/regulatory requirements need separate engineering and expert review.

## Scientific interpretation guardrails

- The target is entry into the Challenge `SepsisLabel`-positive window, not independently adjudicated biological sepsis onset. The Challenge label already incorporates a six-hour lead convention; do not shift it again.
- Set B is evaluation-only and must not be used to choose features, calibrators, thresholds, or models.
- AUROC/AUPRC measure ranking, not calibration or clinical utility. Report Brier/log loss, sensitivity, PPV, and alert burden alongside ranking metrics.
- VITALIS is a research prototype, not a medical device or validated clinical decision-support system. Never use its output to make patient-care decisions.


## Verified main-branch reproduction update — 16 October 2026

The current `main` commit `426ac5dd2a8076fb192bcebd0b1c8f838bf72906` completed the clean-checkout full-cohort workflow successfully: [GitHub Actions run 38889950689](https://github.com/culprit-k/VITALIS/actions/runs/38889950689). All preflight, source provenance, Python 3.11, numerical backend, unit-test, official cohort download, source audit, fresh cache, 1/3/6-hour evaluation, physiology ablation, patient-disjoint Set A calibration, aggregate-output, and baseline reconciliation steps passed.

- Reconciliation remained unchanged: 42/42 metric mean/sample-SD pairs and 84/84 scalar values matched at the predeclared six-decimal rule; zero mismatches.
- The aggregate-only artifact is available at [artifact 12042469450](https://github.com/culprit-k/VITALIS/actions/runs/38889950689/artifacts/12042469450).
- The full report, including exact metrics and interpretation, is in [MAIN_BRANCH_FULL_COHORT_REPRODUCTION_2026-10-16.md](MAIN_BRANCH_FULL_COHORT_REPRODUCTION_2026-10-16.md).
- Main finding: the baseline reproduces, but there is no clear overall model winner. Patient-relative physiology improves AUROC over the temporal baseline but worsens Brier at all horizons. Platt calibration sharply reduces Brier for class-balanced models but leaves effectively zero sensitivity at the fixed 0.5 threshold.
- Set B remained evaluation-only. It must not be used to select a threshold or calibrator.
- The workflow passing is a reproducibility milestone, not clinical validation. Independent statistical/methods review, an independent clinical cohort, prospective/governance evidence, and the human release decision remain open. Do not begin patient-connected hardware or clinical deployment based on these results.
