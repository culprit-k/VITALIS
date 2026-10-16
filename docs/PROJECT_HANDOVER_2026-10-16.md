# VITALIS research prototype handover — 16 October 2026

**Repository:** https://github.com/culprit-k/VITALIS  
**Branch:** `work/strict-reproducibility-gate`  
**Verified source commit:** `49d13fc769d8596cae76fddd2974962563a074d5`  
**Pull request:** https://github.com/culprit-k/VITALIS/pull/2  
**Disposition:** reproducible research prototype; not a clinical release.

## Current execution evidence

All checks below were observed on the exact verified branch head above:

- Standard CI, including compileall, source manifest, repository hygiene, reachable-history audit, synthetic twin stream demo, integrated-inference demo, and pytest: https://github.com/culprit-k/VITALIS/actions/runs/38876716745 — passed.
- Reporting/dashboard tests: https://github.com/culprit-k/VITALIS/actions/runs/38876716839 — passed.
- Pinned Python 3.11 clean-checkout full-cohort workflow: https://github.com/culprit-k/VITALIS/actions/runs/38876716891 — passed.
- Python 3.13 full-cohort diagnostic: https://github.com/culprit-k/VITALIS/actions/runs/38876716750 — passed as a diagnostic, not the acceptance environment.
- Pinned Python 3.11 reconciliation: 42/42 mean/sample-standard-deviation pairs and 84/84 scalar values matched the preserved aggregate under the existing six-decimal rule; zero mismatches. The workflow retained an aggregate-only artifact with provenance. Artifact: https://github.com/culprit-k/VITALIS/actions/runs/38876716891/artifacts/12037026308
- The latest pinned full-cohort job reports 218 tests passed. The standard workflow additionally runs the two synthetic demos and the reachable Git history/privacy heuristic scan.

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
6. **Release decision:** PR #2 remains draft and unmerged until the independent review and final human release decision are recorded.

## Scientific interpretation guardrails

- The target is entry into the Challenge `SepsisLabel`-positive window, not independently adjudicated biological sepsis onset. The Challenge label already incorporates a six-hour lead convention; do not shift it again.
- Set B is evaluation-only and must not be used to choose features, calibrators, thresholds, or models.
- AUROC/AUPRC measure ranking, not calibration or clinical utility. Report Brier/log loss, sensitivity, PPV, and alert burden alongside ranking metrics.
- VITALIS is a research prototype, not a medical device or validated clinical decision-support system. Never use its output to make patient-care decisions.
