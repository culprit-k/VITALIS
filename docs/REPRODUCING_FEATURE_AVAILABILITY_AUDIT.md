# Reproducing the cross-cohort feature-availability audit

The script `scripts/audit_feature_availability.py` recreates a descriptive availability comparison from the local memory-mapped caches produced by `scripts/build_feature_cache.py`. It writes aggregate counts and rates only.

## Run

Build the Set A and Set B caches outside the repository, then run:

```bash
python scripts/audit_feature_availability.py \
  --set-a-cache /path/to/set-a-cache \
  --set-b-cache /path/to/set-b-cache \
  --threshold 0.05 \
  --chunk-rows 50000 \
  --output /path/outside/repo/feature_availability_audit.json
```

The output includes row counts, finite counts/rates for each feature, features entirely missing in one cohort, and features whose absolute finite-rate difference meets the selected threshold. Processing is chunked to bound temporary memory. The input caches and output should remain outside Git if they contain data derived from local patient records; only reviewed aggregate artifacts should be checked in.

## Interpretation and limits

- The default 0.05 threshold is a descriptive reporting cutoff, not a clinically justified decision rule.
- Hourly rows within a patient are correlated; rates are descriptive and are not patient-level inferential estimates.
- Set B is evaluation-cohort characterization only. This audit does not fit a model and must not be used to select features, tune thresholds, or otherwise optimize the model against Set B.
- Availability alone does not establish comparable units, measurement practices, missingness mechanisms, predictive value, transportability, or clinical utility.
- VITALIS remains a research project, not a validated clinical decision tool.
