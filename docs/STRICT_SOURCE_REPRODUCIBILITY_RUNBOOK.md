# Strict source and full-cohort reproduction gate

**Status:** procedure defined; a fresh clean-checkout, environment-captured full-cohort reproduction has **not** yet been completed. The environment is recorded but not fully locked until a reviewed lock file or immutable container is adopted. Do not mark this gate complete until a reviewer can inspect the command logs and aggregate comparison.

## Goal

Resolve the documented provenance exception: some full-cohort reports were generated from a reconstructed local working copy because a clean checkout could not be verified. This runbook defines a fail-closed procedure for executing the committed source and comparing its aggregate outputs without exposing patient-level data.

VITALIS is research-only. These steps are not authorization for clinical use or prospective data collection.

## 1. Freeze the source revision

Run from a machine authorized to access the official local Challenge data. Replace the example branch below only if the intended review commit differs; record the full 40-character commit SHA in the run log.

```bash
git clone https://github.com/culprit-k/VITALIS.git VITALIS-repro
cd VITALIS-repro
git fetch origin work/strict-reproducibility-gate
git checkout --detach origin/work/strict-reproducibility-gate
git rev-parse HEAD
git status --porcelain
```

The working tree must be clean. Save the commit SHA, UTC run start/end times, operating system, architecture, and Python version in a run log stored **outside** the repository. Do not commit local run logs containing filesystem paths or data-source details.

## 2. Verify checked-out bytes against the selected Git commit

Run the automated manifest command after creating the virtual environment and before installing project dependencies, then again after installation and immediately before model execution. It writes the environment/source manifest outside Git and fails closed if the tree is dirty, a required file is missing, or any checked-out file differs from its Git blob. Any mismatch is a hard stop. The manual Git commands below remain available for independent spot checks.

```bash
set -eu
test -z "$(git status --porcelain)"
for path in \
  pyproject.toml \
  scripts/evaluate_horizon_cross_cohort.py \
  scripts/evaluate_horizon_calibration.py \
  scripts/bootstrap_heldout_scores_fast.py \
  src/vitalis/horizon.py \
  src/vitalis/utility.py
do
  expected="$(git rev-parse "HEAD:$path")"
  actual="$(git hash-object "$path")"
  printf '%s expected=%s actual=%s\n' "$path" "$expected" "$actual"
  test "$expected" = "$actual"
done
```

This checks each listed working-tree file against the blob recorded in the checked-out commit. If a path does not exist at the selected commit, stop and reconcile the runbook with that revision; do not silently skip it. Record the full commit SHA and output outside Git.

## 3. Create and record an isolated Python environment

The existing CI workflow uses Python 3.11 and installs the project with its development and accelerated-bootstrap extras. Match that baseline for the reproduction, and record the exact resolved package versions. Do not claim a fully locked environment until a lock file or immutable container image is reviewed and adopted.

```bash
python3.11 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python scripts/verify_source_manifest.py --output /tmp/vitalis-source-manifest-preinstall.json
python -m pip install -e ".[dev,bootstrap-accelerated]"
python scripts/verify_source_manifest.py --output /tmp/vitalis-source-manifest-installed.json
python --version
python -m pip freeze > /tmp/vitalis-repro-pip-freeze.txt
python -m pip check
python -m compileall -q src scripts dashboard tests
python scripts/check_repository_hygiene.py
python scripts/audit_git_history.py --json-output /tmp/vitalis-repro-history-audit.json
pytest
```

Save both source manifests, package inventory, and test/audit logs outside the repository. CI retains its source manifest and history-audit JSON as a GitHub Actions artifact for 30 days; use the artifact from the exact reviewed commit, not a later run. The manifest records the commit/tree IDs, source blob checks, Python/platform metadata, and resolved package inventory. A successful test suite is necessary but does not by itself prove full-cohort result reproduction.

## 4. Validate local cohort sources and rebuild caches

Use only the authorized official Set A and Set B Challenge 2019 files. Keep the original data, derived feature caches, row-level predictions, patient-group arrays, and intermediate outputs outside the repository. Never upload these files to GitHub.

Use the commands and expected cohort totals in [the full-cohort execution protocol](HORIZON_CROSS_COHORT_EXECUTION.md) to build fresh cache directories from the authorized source files. Do not reuse caches whose source archive, builder commit, feature schema, or provenance is uncertain. Do not run overlapping cache chunks against the same destination.

Before evaluation, verify the official totals:

- Set A: 20,336 patients, 790,215 hourly rows, 17,136 positive hourly labels.
- Set B: 20,000 patients, 761,995 hourly rows, 10,780 positive hourly labels.

The checked-in evaluators must reject mismatched counts or schemas. If validation fails, stop and investigate the source archive, patient ordering, and cache provenance. Never bypass an integrity guard to force a run.

## 5. Run the predeclared evaluations without tuning on Set B

Immediately before the evaluation commands, rerun `python scripts/verify_source_manifest.py --output /tmp/vitalis-source-manifest-pre-run.json`. Use output paths outside the repository. Preserve the existing committed aggregate reports as historical records; do not overwrite them or silently replace them with reconstructed results.

### Static/temporal future-label cross-cohort evaluation

Follow the exact command in [HORIZON_CROSS_COHORT_EXECUTION.md](HORIZON_CROSS_COHORT_EXECUTION.md), using the fresh caches, horizons 1/3/6, seeds 42/123/2026, the documented fixed threshold, and the documented bootstrap count.

### Calibration, paired comparison, and development-only utility analysis

Follow [the calibration protocol](HORIZON_CALIBRATION_OPERATING_POINT_PROTOCOL.md) and [the utility framework](UTILITY_OPERATING_POINT_FRAMEWORK.md). Keep Set B evaluation-only: no fitting, calibration, feature selection, cost selection, or threshold selection may use Set B. Do not choose a threshold after inspecting Set B and then report the same Set B as an unbiased evaluation.

The target is entry into the Challenge SepsisLabel-positive window, not independently observed biological sepsis onset. Keep this distinction in every report.

## 6. Reconcile aggregate outputs

Compare fresh outputs with the committed aggregate reports using a small, reviewable script or notebook kept outside the repository. For each comparison, record:

- Input cohort totals and schema fingerprints.
- Source commit SHA and source-blob checks.
- Python and resolved dependency versions.
- Model/split seeds, horizons, thresholds, calibration method, and bootstrap replicate count.
- Per-metric absolute differences and a predeclared numeric tolerance.
- Captured warnings, failed fits, skipped rows, and any deviations from the protocol.

Do not define a tolerance after seeing the discrepancies. Exact deterministic counts and schemas should match exactly. For floating-point metrics, define the comparison tolerance before execution and explain any differences due to numerical libraries or hardware. If results disagree beyond tolerance, preserve both artifacts, investigate, and report the cause; never silently replace the prior artifact.

Only aggregate, disclosure-reviewed results may be committed. Never commit raw patient data, cache files, row-level predictions, patient identifiers, or private score archives.

## 7. Evidence required to close this gate

- [ ] A clean checkout at a recorded full commit SHA and a clean working tree.
- [ ] Successful source-blob checks for all listed files.
- [ ] Recorded Python/runtime and exact resolved dependency inventory.
- [ ] Successful compilation, repository hygiene/history audits, and full test suite.
- [ ] Fresh caches with official cohort counts/schema verified and provenance recorded privately.
- [ ] Completed predeclared runs for all seeds and horizons, with Set B evaluation-only.
- [ ] Aggregate reconciliation report with predeclared tolerances and all discrepancies explained.
- [ ] Independent reviewer sign-off on the source provenance and statistical comparison.

Until every applicable item is evidenced, the gate remains open and any full-cohort result produced from a reconstructed working copy must remain explicitly provenance-qualified.

## Safety and governance boundary

This procedure addresses software/source reproducibility only. It does not provide independent clinical validation, establish safe operating thresholds, or authorize prospective use. Independent clinical/statistical review, data-governance and ethics determinations, and a genuinely new cohort with independently defined/adjudicated event timing remain separate gates. VITALIS must not be used to guide patient care.
