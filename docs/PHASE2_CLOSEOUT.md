# VITALIS Phase 2 Closeout

**Status: Exploratory analysis and aggregate-metric reconciliation complete; strict byte-for-byte source identity remains an explicit reproducibility exception.**

## Scope completed

- Implemented aggregate calibration and feature-missingness helpers with unit tests.
- Added a held-out calibration/missingness runner with patient-disjoint train, validation, and test splits.
- Evaluated static, temporal, and experimental personalized feature sets on a deterministic 500-patient sample across three split seeds.
- Evaluated validation-only Platt/logistic and isotonic recalibration; test outcomes were not used to fit the recalibration mapping.
- Compared median imputation with and without missingness indicators.
- Ran exploratory age/gender subgroup and missingness-stratified audits with small-cell suppression.
- Repeated local aggregate runs and recorded their hashes.
- Kept raw patient rows and patient-level prediction outputs out of the repository.
- Updated the roadmap and results artifacts; GitHub Actions passed for the latest checked commits before this closeout document.

## Key findings

1. Static features had the strongest mean discrimination in the initial Phase 1 comparison. Temporal and personalized features did not establish an improvement over static features.
2. Recalibration reduced row-level Brier score/log loss in the exploratory sample, but AUROC did not improve with Platt scaling. The apparent score improvement may largely reflect probability compression toward low row-level prevalence; it is not proof of clinical calibration.
3. Isotonic calibration varied across splits and may overfit a small validation cohort.
4. Missingness indicators showed modest and inconsistent effects. No imputation strategy has been established as generally superior.
5. Subgroup estimates were unstable or unavailable for some small strata. No fairness, subgroup safety, or transportability claim is supported.

## Reproducibility exception

The checked-in runner logic was mirrored from GitHub and executed against the local dataset. Aggregate split counts, row counts, positive-label counts, and feature counts match the prior local equivalent; metric differences are small and recorded below. However, the mirrored files were not verified byte-for-byte against the repository blobs in the execution runtime, so this is aggregate-metric reconciliation, not strict source-identical execution.

**Remaining closure gate:** verify exact source/blob identity in the execution runtime (or run the canonical entry point in an environment with the repository checkout and dataset together). Do not claim byte-for-byte canonical execution until this is completed.

## Phase 2 acceptance decision

- **Exploratory analysis and documentation:** complete.
- **Unit tests and CI for checked-in code:** passed on the latest verified checks before this closeout document.
- **Exact canonical-runner reconciliation:** pending.
- **Clinical validation / prospective use:** out of scope; not performed.
- **Full-cohort or external validation:** out of scope; not performed.
- **Hardware prototyping:** not justified by these results alone.

## Safety and claims

VITALIS remains a research prototype. The dataset's hourly `SepsisLabel` was used as supplied and not shifted again. Hourly challenge-label metrics are not event-level clinical outcomes. These results do not support diagnosis, triage, treatment, clinical benefit, patentability, or patient-facing deployment.

## Runner reconciliation follow-up (2026-10-14)

The checked-in runner logic was mirrored into the local runtime from source retrieved through the GitHub connector and executed against the local dataset using the recorded sample and split seeds. The resulting aggregate artifact is [`phase2_canonical_runner_reconciliation.json`](../results/phase2_canonical_runner_reconciliation.json).

- The three splits match the prior local equivalent exactly on patient counts, hourly-row counts, positive-label-row counts, and feature counts.
- Across 135 shared calibration metric comparisons, maximum absolute differences were: Brier score 0.000084; log loss 0.000704; calibration intercept 0.00983; calibration slope 0.00238.
- Reliability-bin counts are not identical. The previous local equivalent clipped probabilities before assigning bins, while the repository helper assigns bins from original probabilities. The repository helper's binning behavior is authoritative; do not use the prior local equivalent's reliability bins as canonical.
- Canonical-style aggregate output SHA-256: `c9b3117cd7a32e825b0d859da37480b2c0102e751656e3af733bd82be4078a86`.

**Remaining integrity caveat:** because the local container cannot resolve GitHub hosts, exact byte-for-byte checkout/blob-hash verification of every mirrored source/dependency file could not be performed in the same runtime. Therefore the empirical protocol/results reconciliation is complete to the aggregate-metric level, but strict source-byte identity is not claimed. The source-hash caveat remains documented rather than silently waived.
