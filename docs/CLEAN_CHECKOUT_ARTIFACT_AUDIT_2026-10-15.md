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
