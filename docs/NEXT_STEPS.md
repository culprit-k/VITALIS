# VITALIS next steps and current status

## Current verified state

- The public repository contains the research scaffold, automated tests, dataset inventory, historical experiment register, and multi-seed runner.
- An earlier local rerun on a deterministic 1,500-patient sample is recorded in [current_subset_rerun.json](../results/current_subset_rerun.json).
- [x] Completed a fresh three-seed comparison on the same deterministic 1,500-patient sample; see [multi-seed report](MULTISEED_SUBSET_EXPERIMENT.md) and [aggregate results](../results/multiseed_subset_summary.json).
- The rerun used 960 train, 240 validation, and 300 test patients with no patient overlap. The model fit emitted warnings because EtCO2 had no observed values and was dropped by the imputer.
- On this one held-out sample, temporal features increased AUROC by about 0.0119 and lowered Brier score by about 0.0186, but average precision decreased by about 0.0092. This mixed result does not establish that temporal features are better overall.
- The run was executed locally against the current intended protocol, but it is not an execution from GitHub Actions and not a full-cohort evaluation.

- [x] Implemented the first VITALIS-PB patient-baseline deviation feature generator and integrated a third model into the matched comparison. See [algorithm specification](VITALIS_PB_ALGORITHM.md). CI and data-backed model evaluation are still required before interpreting performance.

## Prioritized plan

### 1. Fix and test data/model pipeline details
- [x] Exclude predictors entirely missing in the training fold and record dropped columns in the report.
- [x] Add a deterministic subset runner and tests for sample-size validation and repeatable patient-file sampling.
- Confirm that file ordering is chronological and that temporal features are calculated within patient only.
- Ensure a single shared sampled cohort and identical patient splits for all model variants.
- [x] Add regression tests for training-fold all-missing feature exclusion and deterministic subset sampling.
- [ ] Add further explicit tests for feature alignment and chronological ordering.

### 2. Rerun the baseline experiment reproducibly
- [x] Add `scripts/run_subset_experiment.py` for a deterministic patient-level subset comparison; run it locally and keep aggregate-only outputs.
- [x] Run static-versus-temporal comparisons on split seeds 42, 123, and 2026; the checked-in multi-seed report records results and limitations.
- [x] Review and publish aggregate-only metrics after checking counts, split overlap, and model warnings.
- [x] Inspect cohort counts, positive-label prevalence, convergence warnings, and patient-level split separation.
- Keep patient-level predictions and raw files local; only publish aggregate metrics after review.

### 3. Improve evaluation before claiming model benefit
- Treat AUROC, average precision, Brier score, calibration, sensitivity, and alert burden as complementary metrics.
- Select any operational threshold on validation data only, then freeze it before test evaluation.
- Add patient-level event/episode evaluation only when a defensible episode definition and timing target are prespecified.
- Use patient-cluster uncertainty estimates; do not treat hourly rows as independent observations.
- Keep full-cohort evaluation provisional until models converge and the results reproduce.

### 4. External validation and clinical research
- Identify a distinct suitable cohort and document its permissions, population, label definition, and preprocessing differences.
- Freeze model and threshold before external evaluation.
- Seek clinical/statistical supervision and an appropriate ethics/data-governance review before any prospective or patient-facing study.

### 5. Innovation and IP
- [x] Define and implement a first mathematical patient-baseline deviation hypothesis as an experimental feature generator.
- [ ] Evaluate whether it adds value over static and temporal baselines on identical splits with paired patient-cluster uncertainty.
- Keep the patient-specific baseline concept as a hypothesis until prior-art review and technical differentiation are documented.
- Do not make novelty, patentability, regulatory approval, or clinical efficacy claims based on these internal experiments.

## Safety boundary

VITALIS is a research prototype. It is not validated for diagnosis, triage, treatment, or any real patient-care decision. No patient-level records or predictions belong in this public repository.
