# Full-cohort paired patient-cluster bootstrap (14 October 2026)

## Status and caveat

A preliminary paired patient-cluster bootstrap was run separately on the held-out patients for split seeds 42, 123, and 2026. Only **20 bootstrap replicates per seed** completed within the available execution window. These percentile intervals are coarse pilot diagnostics, **not final inferential evidence**; repeat with at least 200–1,000 replicates after further runtime optimization.

The local evaluator used for this run was reconstructed from checked-in logic and is not byte-identical to the GitHub source. The current checked-in evaluator uses the same intended multiplicity-weighted cluster bootstrap method, but this artifact must not be represented as a byte-identical execution of that exact source.

## Paired temporal-minus-static differences

Positive AUROC/AUPRC differences favor temporal features. Negative Brier differences favor temporal features. Intervals are conditional on each held-out split and do not estimate external-validation uncertainty.

| Split seed | Metric | Difference | Preliminary 95% percentile interval |
|---:|---|---:|---:|
| 42 | AUROC | +0.0242 | +0.0153 to +0.0351 |
| 42 | AUPRC | +0.0077 | +0.0037 to +0.0172 |
| 42 | Brier | −0.0088 | −0.0104 to −0.0071 |
| 123 | AUROC | +0.0268 | +0.0190 to +0.0375 |
| 123 | AUPRC | +0.0012 | −0.0027 to +0.0065 |
| 123 | Brier | −0.0067 | −0.0083 to −0.0049 |
| 2026 | AUROC | +0.0255 | +0.0175 to +0.0326 |
| 2026 | AUPRC | +0.0039 | +0.0002 to +0.0075 |
| 2026 | Brier | −0.0081 | −0.0094 to −0.0060 |

## Interpretation

Across these three splits, temporal features had higher AUROC and lower Brier score. The AUPRC difference was less consistent; its preliminary interval crossed zero for seed 123. With only 20 bootstrap replicates, interval endpoints are especially coarse. This supports further evaluation, not a claim of clinical benefit or model readiness.

## Dataset and safeguards

- Full training_setA integrity totals: 20,336 patients, 790,215 hourly rows, 17,136 positive challenge-label rows.
- Patient-disjoint train/validation/test partitions; bootstrap resamples patient groups, retaining all hourly rows for each selected patient.
- No raw patient records or row-level predictions are included in this report or aggregate JSON.
- The fixed threshold of 0.5 is not a clinically selected operating point.
- Hourly challenge-label metrics are not patient-level event sensitivity, time-to-detection, or clinical false-alarm rates.
- No external/prospective validation; not for diagnosis, triage, or treatment.

Machine-readable aggregate artifact: [JSON](../results/full_cohort_paired_patient_cluster_bootstrap_2026-10-14.json).
