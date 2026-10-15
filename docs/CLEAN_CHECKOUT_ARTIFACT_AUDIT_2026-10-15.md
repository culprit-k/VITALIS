# Clean-checkout artifact audit — 15 October 2026

## Status

**The first clean-checkout evaluation job completed, but its result is not accepted as the reproducibility gate.** The artifact came from run [38677774161](https://github.com/culprit-k/VITALIS/actions/runs/38677774161), commit `bfa78a9cfc6a045feb2edff57c0dc6d2b82e4641`. That run's executed step list did not include the fail-closed baseline reconciliation step present in the newer workflow.

## What passed in that run

- Exact checkout and source-manifest verification reported a clean tree and matching tracked source blobs.
- The official Set A and Set B source audits passed: Set A 20,336 patients / 790,215 rows / 17,136 positive labels; Set B 20,000 patients / 761,995 rows / 10,780 positive labels.
- Fresh caches for both cohorts completed; all nine horizon × seed runs (18 static/temporal fits) completed.
- Aggregate-only artifact was retained. It contains no raw cohort files, caches, patient IDs, or row-level predictions.
- Source history heuristic reported zero findings (not proof that sensitive information was never exposed).

## Blocking issue: runtime and baseline mismatch

The artifact's `pip freeze` recorded NumPy 2.4.6, pandas 3.0.6, scikit-learn 1.9.1 and SciPy 1.17.1. These do **not** match the repository's intended reproduction constraints: NumPy 2.3.5, pandas 2.2.3, scikit-learn 1.8.0 and SciPy 1.17.0. Therefore this run does not verify the pinned environment.

I independently recomputed the seven predeclared aggregate metrics for each of two models at each of three horizons (42 mean/SD pairs) from the artifact and compared them with `results/horizon_cross_cohort_2026-10-14.json`, rounding both means and sample SDs to six decimal places:

- Full pairs matching both mean and SD: **1 / 42**.
- Scalar mean/SD values matching: **3 / 84**.
- Scalar mean/SD values differing: **81 / 84**.

This contradicts the earlier claim that all 42 pairs matched for this clean-checkout run. The mismatch does not by itself establish which historical result is correct. Do not weaken the predeclared tolerance or overwrite the baseline to force agreement. Re-run the current pinned workflow with its reconciliation step, preserve both outputs, and investigate any remaining differences in split definitions, metric calculations, dependency versions and baseline provenance.

## Current decision

- **Clean data access/cache/evaluation execution:** passed for the run cited above.
- **Pinned-environment reproduction:** not verified by that run.
- **Historical aggregate reconciliation:** failed for that run.
- **Independent review:** still required.
- **Clinical validation:** not performed; research-only.

A newer workflow revision with an isolated Python environment and fail-closed reconciliation is present in the branch. A manual workflow-dispatch trigger has been enabled in commit `30d34924587121cec364c2334d111e686fd0b5ca`. This audit records the earlier artifact honestly; it is not a release approval.

## Follow-up control added after this audit

Commit [c20ed448ab3fbcfc6e6e35c73dd8b28a26950184](https://github.com/culprit-k/VITALIS/commit/c20ed448ab3fbcfc6e6e35c73dd8b28a26950184) adds explicit runtime assertions for the pinned scientific stack and key test/runtime dependencies immediately after installation. A version mismatch now stops the reproduction before cohort download and model evaluation. This prevents a future artifact from being treated as a pinned run merely because `pip freeze` was captured.

The connected GitHub integration currently exposes a PR-triggered standard test run but not discovery of push-triggered full-cohort runs. The current full-cohort run and its artifact are therefore **not yet verified** in this audit. The dependency-version gate is a control added to the workflow, not evidence that the new run passed.

## Baseline provenance disposition

The preserved baseline at `results/horizon_cross_cohort_2026-10-14.json` records that the historical execution used a reconstruction of the checked-in evaluator because a full Git clone was unavailable. Its source-blob fields establish which files were referenced, but do not establish that the checked-in evaluator was executed end-to-end from a clean checkout. Therefore the baseline remains a valuable immutable historical comparator, but it is **not yet an approved authoritative reference** for a release-grade reproducibility claim.

The two problems must be treated separately:

1. **Environment defect in the older CI artifact:** the run did not use the intended dependency pins.
2. **Reference provenance defect:** the historical baseline itself was produced using a reconstructed execution path.

The pinned clean-checkout run at [#38679761894](https://github.com/culprit-k/VITALIS/actions/runs/38679761894) passed installation and the explicit version-verification step before proceeding to source download. Its final execution, artifact, and reconciliation are still pending at the time of this update.

If that run completes but fails numerical reconciliation, do not change the six-decimal rule or replace the 14 October file. Preserve its output as a candidate clean-checkout reference, document per-seed and per-metric differences, and require an independent reviewer to approve a separately versioned baseline before changing what future runs compare against. Numerical agreement alone cannot cure the baseline's provenance gap.
