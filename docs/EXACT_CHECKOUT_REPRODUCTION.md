# Exact-checkout cross-cohort reproduction runbook

**Purpose:** close the provenance gap for the cross-cohort validation-only recalibration experiment. This procedure must run on a machine that has authorized local copies of the PhysioNet/CinC Challenge 2019 data. The public repository must contain neither raw patient records nor patient-level caches, group vectors, score archives, or predictions.

## 1. Establish an exact, clean checkout

Run from a terminal on the machine that has the local data:

```bash
git clone https://github.com/culprit-k/VITALIS.git
cd VITALIS
git checkout main
git pull --ff-only origin main

git status --short
git rev-parse HEAD
git rev-parse HEAD:scripts/build_feature_cache.py
git rev-parse HEAD:scripts/evaluate_cross_cohort_recalibration.py
git rev-parse HEAD:tests/test_cross_cohort_recalibration.py

# The tracked source blobs and working-tree files must agree.
git diff --exit-code HEAD -- scripts/build_feature_cache.py scripts/evaluate_cross_cohort_recalibration.py tests/test_cross_cohort_recalibration.py
```

Record the checkout commit SHA and the three blob SHAs with the experiment report. A clean status and successful diff check establish that the source files being run match that checkout; they do not by themselves establish scientific validity.

## 2. Install dependencies and run the repository tests

```bash
python -m venv .venv
# Activate the environment before continuing.
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest
```

Save the test summary and Python/package versions with the local run log. Do not proceed if tests fail; investigate and document any environment-specific differences first.

## 3. Build local feature caches outside the checkout

Set the dataset paths to the directories containing the authorized per-patient `.psv` files. Put caches and outputs outside the repository (for example, under `$HOME/vitalis-local/`):

```bash
export VITALIS_LOCAL="$HOME/vitalis-local"
export SET_A="/absolute/path/to/training_setA"
export SET_B="/absolute/path/to/training_setB"
mkdir -p "$VITALIS_LOCAL"

# Set A has 20,336 patient files: four sequential, non-overlapping chunks.
for RANGE in "0 5084" "5084 10168" "10168 15252" "15252 20336"; do
  read START END <<< "$RANGE"
  python scripts/build_feature_cache.py "$SET_A" \
    --cache-dir "$VITALIS_LOCAL/cache-A" --start "$START" --end "$END"
done

# Set B has 20,000 patient files: four sequential, non-overlapping chunks.
for RANGE in "0 5000" "5000 10000" "10000 15000" "15000 20000"; do
  read START END <<< "$RANGE"
  python scripts/build_feature_cache.py "$SET_B" \
    --cache-dir "$VITALIS_LOCAL/cache-B" --start "$START" --end "$END"
done
```

Run each chunk sequentially. Use fresh cache directories if the input file list changes. Verify that cache metadata reports 20,336 set-A patients and 20,000 set-B patients, and that the evaluator's integrity checks pass. The cache builder's row-level arrays are sensitive research data: never upload or commit them.

## 4. Execute the checked-in recalibration runner

```bash
python scripts/evaluate_cross_cohort_recalibration.py \
  --set-a-cache "$VITALIS_LOCAL/cache-A" \
  --set-b-cache "$VITALIS_LOCAL/cache-B" \
  --seeds 42 123 2026 \
  --output "$VITALIS_LOCAL/cross_cohort_recalibration_exact_checkout.json" \
  | tee "$VITALIS_LOCAL/cross_cohort_recalibration_run.log"
```

The committed runner must report patient-disjoint 60/20/20 splits within set A, fit the Platt recalibrator on set-A validation predictions only, and evaluate the frozen model/recalibrator on set B. Set B must not be used for model fitting, recalibrator fitting, or threshold selection.

## 5. Reconcile with the existing exploratory artifact

Compare the new aggregate output with:

- Historical aggregate: `results/cross_cohort_validation_A_recalibration_test_B_3seed_2026-10-14.json`
- Protocol and limitations: `docs/CROSS_COHORT_RECALIBRATION_PILOT.md`

Compare the same metric definitions for each seed and model: AUROC, average precision, Brier score, log loss, and mean predicted probability for both raw and recalibrated set-B scores. Also compare patient/row counts, split sizes, warning messages, and the set-B prevalence. Do not compare elapsed runtime or JSON formatting as model metrics. Small numerical differences may arise from package versions or numerical libraries; report them explicitly and investigate meaningful discrepancies rather than silently overwriting the historical artifact.

The historical values came from a reconstructed local harness. Numerical agreement with that artifact is a reconciliation check, not proof that the historical result itself was generated from the checked-in source.

## 6. Publish only a safe aggregate report

If results are reconciled, commit only a reviewed, aggregate-only JSON artifact and a report that records:

- checkout commit SHA and relevant source blob SHAs;
- operating system, Python and dependency versions;
- test outcome and exact command used;
- cohort counts, patient-disjoint split counts, and model warnings;
- per-seed metric differences from the historical artifact and the chosen comparison tolerance;
- unresolved differences and limitations.

Before committing, inspect the proposed files and run `git status --short`. Never commit `.psv` files, caches (`X.npy`, `y.npy`, `g.npy`, `meta.json`), patient-group vectors, score archives, individual predictions, credentials, or logs that may contain patient-level information.

## Interpretation boundary

This is retrospective evaluation against hourly challenge labels from two cohorts in the same benchmark. Exact source reproduction improves auditability; it does not constitute external/prospective clinical validation, prove clinical calibration, establish event-level sensitivity or false-alarm rates, or authorize patient-care use. VITALIS remains research-only.
