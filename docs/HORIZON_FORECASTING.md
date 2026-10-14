# Future-label forecasting and patient-level warning evaluation

**Implementation:** `scripts/train_horizon_model.py`, `src/vitalis/horizon.py`  
**Status:** initial retrospective research implementation; not clinically validated.

## Why a separate horizon target?

The existing VITALIS models classify the current hourly Challenge 2019 SepsisLabel. This experiment asks a different question: while the current label is zero, will any of the next H hourly challenge labels be positive? It runs H = 1, 3, and 6 hours by default.

For patient i and hourly row t:

\[
Y^{(H)}_{i,t} = \\mathbb{1}\\left[Y_{i,t}=0 \\land \\max_{k=1,\\ldots,H}Y_{i,t+k}=1\\right].
\]

Rows with a current positive label are excluded because this is a forecast/warning task, not detection after the positive window has already started. The last H rows of each patient are excluded because their complete future window is unavailable. The target is never shifted across patient boundaries.

**Important label semantics:** Challenge 2019 SepsisLabel already incorporates a six-hour lead convention. These models forecast entry into the challenge-positive label window; they do not forecast an independently observed biological onset. An H-hour target here means "challenge label becomes positive within H hourly rows," not "sepsis onset within H hours."

## Training and split protocol

- Input is the local, authorized per-patient PSV archive. Raw data stay outside Git.
- Static baseline features plus causal lag, one-step delta, and trailing-six-row features are used.
- Patients are split into train/validation/test groups (64%/16%/20% by the two-stage group split). No patient crosses partitions.
- Imputation, missingness indicators, scaling, and logistic-regression fitting are learned from training rows only.
- The threshold defaults to a fixed 0.5 reference. No threshold or model choice is tuned on test results.
- Aggregate-only JSON is written to the requested output path. No fitted model, row-level score, patient ID, or raw record is exported.

Example:

```bash
python scripts/train_horizon_model.py /path/to/psv_files \
  --horizons 1 3 6 --seed 42 --threshold 0.5 \
  --refractory-hours 6 --bootstrap-replicates 200 \
  --output outputs/horizon_forecast_summary.json
```

The model is trained independently for each horizon. Reported AUROC, AUPRC, Brier score, and threshold metrics are row-level and can be affected by within-patient correlation.

## Patient-level warning metrics

The evaluation reports:

- Forecast-positive windows covered by at least one alert.
- Total alerts and alerts outside future-positive forecast windows per at-risk patient-day.
- Fraction of patients with at least one alert.
- Time from the earliest alert inside a forecast-positive window to the next challenge-positive label row.
- Patient-cluster percentile intervals for alert rates, forecast-window coverage, patient alert prevalence, and mean label-relative warning time.

Alerts use a fixed refractory interval measured in source hourly row indices. Patient-days use eligible at-risk hours only; rows with current-positive labels and incomplete future horizons are excluded.

The terms **outside-window alert** and **warning lead to challenge-label entry** are deliberate. Neither metric is a verified clinical false-alarm rate or lead time to onset. The challenge label's lead-time convention makes that distinction essential. The fixed threshold and refractory interval are research settings, not clinically selected alarm policies.

## Validation gates

1. Unit tests verify future-target alignment, patient-boundary isolation, excluded tails, patient-level alert windows, refractory logic, and cluster bootstrap intervals.
2. Run the CLI on the authorized local full cohort and review positive prevalence at each horizon, split counts, warning burden, and uncertainty.
3. Repeat across predeclared split seeds and evaluate training on Set A / testing on Set B without tuning on Set B.
4. Compare fixed thresholds and calibration using validation data only; if selecting an operating point, predeclare a clinical objective and report the test result once.
5. Seek independent statistical and clinical review before any prospective or patient-facing study.

This experiment is a more explicit supervised forecasting target, but it does not establish clinical performance or validate VITALIS for patient care.
