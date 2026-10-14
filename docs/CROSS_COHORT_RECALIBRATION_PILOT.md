# Cross-cohort recalibration: validation on set A, evaluation on set B

Date: 14 October 2026

## Question

Can recalibration fitted only on patient-disjoint validation data from training set A improve probability quality when applied to set B?

## Protocol

- Three patient-level split seeds: 42, 123, 2026.
- For each seed, set A was divided into 60% model-training patients, 20% calibration-validation patients, and 20% unused patients. These partitions are patient-disjoint.
- Static and temporal logistic-regression models used median imputation, missingness indicators, standard scaling, and balanced class weights.
- A one-dimensional logistic (Platt) recalibrator was fitted on the set A validation predictions only.
- The fitted recalibrator was frozen and applied once to all set B patients. Set B was not used for model fitting, recalibrator fitting, or threshold selection.
- Set B contains 20,000 patients, 761,995 hourly rows, and 10,780 positive hourly challenge-label rows (1.415%).

## Results

Mean ± sample standard deviation across three split seeds. These are not confidence intervals.

| Model / probability stream | AUROC | Average precision | Brier score | Log loss | Mean predicted probability |
|---|---:|---:|---:|---:|---:|
| Static, raw | 0.6750 ± 0.0058 | 0.0455 ± 0.0018 | 0.1659 ± 0.0057 | 0.5223 ± 0.0121 | 36.76% |
| Static, recalibrated | 0.6750 ± 0.0058 | 0.0455 ± 0.0018 | 0.01406 ± 0.00012 | 0.07171 ± 0.00037 | 1.90% |
| Temporal, raw | 0.7319 ± 0.0064 | 0.0581 ± 0.0015 | 0.0972 ± 0.0022 | 0.3526 ± 0.0052 | 26.33% |
| Temporal, recalibrated | 0.7319 ± 0.0064 | 0.0581 ± 0.0015 | 0.01382 ± 0.00003 | 0.06895 ± 0.00036 | 1.34% |

Set A validation positive hourly-label prevalence was about 2.17%; set B prevalence was 1.415%.

## Interpretation

1. Temporal features had better ranking discrimination than static features on set B across all three splits.
2. Validation-only Platt recalibration substantially lowered Brier score and log loss on set B across all three splits while leaving ranking metrics effectively unchanged.
3. This is encouraging for the *recalibration method under this benchmark protocol*, but it is not proof that probabilities are clinically calibrated or will transport to another hospital or future population. The average recalibrated probability remains above set B prevalence, particularly for the static model.
4. Calibration was fit on set A validation labels; the evaluation was on set B, which is held out from recalibration. This separation avoids directly tuning on set B, but does not remove distribution-shift risk.
5. Next: implement this procedure in a checked-in, parameterized runner, test patient isolation and set-B non-use, and execute it from an exact repository checkout. Then assess subgroup and uncertainty robustness without tuning on set B.

## Provenance and limitations

The initial exploratory results used a reconstructed experimental harness; they are retained as historical context in [the three-seed JSON](../results/cross_cohort_validation_A_recalibration_test_B_3seed_2026-10-14.json). A later byte-identical-source run of the checked-in cache builder and recalibration runner is recorded in [the source-verified JSON](../results/cross_cohort_validation_A_recalibration_test_B_source_verified_2026-10-14.json), with metric comparison and limitations in [the reproducibility reconciliation](CROSS_COHORT_REPRODUCIBILITY_RECONCILIATION.md). The historical artifact is not overwritten. No raw patient records, identifiers, or row-level predictions were committed.

Both cohorts are from the PhysioNet/CinC Challenge 2019 benchmark, not prospective clinical validation. Hourly challenge-label metrics are not patient-level event sensitivity, lead time, or real-world clinical false-alarm rates. The threshold 0.5 is not clinically selected.

VITALIS remains research-only and is not validated for diagnosis, triage, treatment, or real patient-care decisions.


## Parameterized runner and regression tests (14 October 2026)

A checked-in runner is now available at [`scripts/evaluate_cross_cohort_recalibration.py`](../scripts/evaluate_cross_cohort_recalibration.py). It builds patient-disjoint 60% training / 20% validation / 20% unused partitions within set A, fits Platt recalibration on validation predictions only, then evaluates frozen raw and recalibrated probabilities on all of set B. Set B is not used for fitting or threshold selection, and the output is aggregate-only.

Example, after building local feature caches outside Git:

```bash
python scripts/evaluate_cross_cohort_recalibration.py \\
  --set-a-cache /path/to/cache-A \\
  --set-b-cache /path/to/cache-B \\
  --seeds 42 123 2026 \\
  --output /secure/local/path/cross_cohort_recalibration.json
```

Regression tests cover deterministic patient-disjoint splitting, the validation-only recalibrator API, invalid calibration inputs, and aggregate-only metric output. The checked-in runner and regression tests passed GitHub Actions on 14 October 2026 (verified run: https://github.com/culprit-k/VITALIS/actions/runs/38583831584). The source files were retrieved from GitHub and their local Git blob hashes matched the recorded source blobs. An additional local rerun reproduced the stored exact-source metrics for seeds 42 and 123 exactly and seed 2026 within floating-point precision (maximum absolute difference below 1.5e-14). The runtime could not complete a full Git checkout because GitHub DNS resolution failed; the claim is byte-identical source execution, not a verified full checkout.


## Exploratory paired patient-cluster uncertainty pilot (14 October 2026)

Set B held-out score archives were regenerated locally for seeds 42, 123, and 2026. For each seed, a paired patient-cluster bootstrap compared temporal against static models using the same 20,000 Set B patients and 761,995 hourly rows. A separate comparison was made for raw scores and for probabilities recalibrated on Set A validation data only.

| Seed | Probability stream | AUROC difference (95% pilot interval) | AUPRC difference (95% pilot interval) | Brier difference (95% pilot interval) |
|---:|---|---:|---:|---:|
| 42 | Raw | +0.0579 (0.0510 to 0.0644) | +0.0132 (0.0106 to 0.0170) | −0.0641 (−0.0647 to −0.0635) |
| 42 | Recalibrated | +0.0568 (0.0504 to 0.0621) | +0.0128 (0.0112 to 0.0150) | −0.000106 (−0.000131 to −0.000078) |
| 123 | Raw | +0.0563 (0.0489 to 0.0614) | +0.0133 (0.0115 to 0.0166) | −0.0670 (−0.0677 to −0.0663) |
| 123 | Recalibrated | +0.0551 (0.0483 to 0.0615) | +0.0131 (0.0111 to 0.0166) | −0.000168 (−0.000256 to −0.000092) |
| 2026 | Raw | +0.0579 (0.0500 to 0.0635) | +0.0120 (0.0100 to 0.0146) | −0.0749 (−0.0755 to −0.0740) |
| 2026 | Recalibrated | +0.0585 (0.0512 to 0.0667) | +0.0123 (0.0103 to 0.0151) | −0.000412 (−0.000550 to −0.000294) |

**Interpret carefully:** this is only 20 bootstrap replicates per seed and probability stream, so intervals are rough pilot estimates—not final inferential results. The temporal model's ranking metrics were consistently higher in these splits, while its recalibrated Brier score was only slightly lower. These results do not establish clinical utility or calibration. Set B was not used for model fitting, recalibrator fitting, or threshold selection.

Aggregate-only artifact: [paired bootstrap JSON](../results/cross_cohort_paired_patient_cluster_bootstrap_20x3_2026-10-14.json). Row-level held-out scores and patient-group vectors remain outside Git.

**Provenance caveat:** the score-generation harness and bootstrap execution were reconstructed local working copies, not verified byte-identical executions of the committed runner. This is an exploratory uncertainty pilot; exact source identity and a higher-replicate run remain open.


## Source-verified rerun and historical comparison (14 October 2026)

The exact-source recalibration runner was rerun against the existing local Set-A/Set-B caches for seeds 42, 123, and 2026. All seven focused regression tests passed. The two rerun outputs for seeds 42 and 123 match the saved source-verified outputs exactly; seed 2026 matches within floating-point precision (maximum absolute metric difference below 1.5e-14). Output hashes and source provenance are recorded in [the reproducibility reconciliation JSON](../results/cross_cohort_reproducibility_reconciliation_2026-10-14.json).

The separate simple cross-cohort evaluator also produced different aggregate metrics from its older reconstructed-harness artifact. The cause cannot be determined from the historical artifact because it lacks enough source and split provenance. The exact-source metrics are retained as canonical for the checked-in evaluator; both records remain available, and the discrepancy is documented in [the reconciliation report](CROSS_COHORT_REPRODUCIBILITY_RECONCILIATION.md). This does not affect the separation of Set-A training/validation and Set-B evaluation, but it does mean the historical simple-evaluator numbers must not be presented as reproduced by the checked-in script.
