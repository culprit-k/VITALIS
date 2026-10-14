# Full-cohort paired patient-cluster bootstrap — 200 replicates

## Results

Each interval is a paired, patient-cluster percentile bootstrap of the temporal-minus-static metric difference within that seed's held-out test split. Patients are sampled with replacement; all hourly rows belonging to a sampled patient receive the corresponding multiplicity weight.

| Split seed | Metric | Mean bootstrap difference | 95% percentile interval |
|---:|---|---:|---:|
| 42 | AUROC | +0.0253 | +0.0149 to +0.0359 |
| 42 | AUPRC | +0.0071 | +0.0024 to +0.0151 |
| 42 | Brier score | −0.0088 | −0.0103 to −0.0069 |
| 123 | AUROC | +0.0268 | +0.0169 to +0.0369 |
| 123 | AUPRC | +0.0013 | −0.0036 to +0.0070 |
| 123 | Brier score | −0.0066 | −0.0086 to −0.0048 |
| 2026 | AUROC | +0.0253 | +0.0140 to +0.0368 |
| 2026 | AUPRC | +0.0043 | +0.0004 to +0.0088 |
| 2026 | Brier score | −0.0080 | −0.0099 to −0.0059 |

All three seeds completed 200 valid replicates each. The positive AUROC difference and negative Brier difference are consistent across seeds. AUPRC is less consistent: its interval crosses zero for seed 123.

## Interpretation and limits

These are conditional uncertainty intervals for retrospective hourly challenge-label metrics, not external validation. The 0.5 threshold was not clinically selected. Hourly label performance does not establish patient-level event sensitivity, lead time, or clinical false-alarm rates. No clinical-use claim is justified.

**Reproducibility caveat:** the local working copy used for this execution was reconstructed from checked-in evaluator logic and is not byte-identical to the GitHub blob. The checked-in evaluator now includes the intended patient-cluster bootstrap implementation, but strict byte-identity of this run remains unverified.

Dataset integrity totals: 20,336 patients, 790,215 rows, 17,136 positive hourly challenge labels. No raw patient data, patient identifiers, or row-level predictions are included.

Machine-readable results: [aggregate JSON](../results/full_cohort_paired_patient_cluster_bootstrap_2026-10-14.json).
