# Streaming twin and supervised prediction interface

**Status:** interface contract for research integration; no clinical fusion or risk-score blending is defined.

## Design rule

The streaming physiological twin and the supervised horizon model answer different questions and must remain separate outputs:

- **Twin output:** current within-person deviation, signal coverage/quality, persistence, cross-system concordance, and heuristic trajectory direction/score.
- **Supervised output:** retrospective model probability for entry into the Challenge `SepsisLabel`-positive window within a specified 1-, 3-, or 6-hour horizon, produced by a separately fitted and evaluated model.

Do not average, multiply, add, or otherwise fuse the twin heuristic score with supervised probabilities. The twin score is unitless and heuristic; it is not a probability. No clinically validated combined score or action threshold exists.

## Current code boundary

1. `Observation` in `src/vitalis/stream.py` carries `channel`, timezone-aware `timestamp`, numeric `value`, `unit`, `quality`, and optional `source`.
2. `TimestampedTwinStream.ingest()` rejects unknown channels, naive timestamps, mismatched units, non-good quality, non-finite/missing values, and non-increasing per-channel timestamps.
3. `TimestampedTwinStream.score(timestamp)` filters stale measurements and calls the adaptive twin with the latest fresh frame.
4. `AdaptivePhysiologicalTwin.update(frame)` returns heuristic deviation/trajectory fields. Its configuration values are engineering defaults, not clinically selected thresholds.
5. The supervised horizon workflow is currently run through offline scripts and evaluation artifacts. It is **not yet a streaming inference service** and is not wired into the twin's update loop.

## Integration envelope

A future application-level adapter may return a versioned envelope with two independent sections:

```json
{
  "schema_version": "vitalis.output.v1",
  "observed_at": "RFC3339 timestamp with timezone",
  "twin": {
    "status": "eligible or insufficient_data",
    "coverage": "number in [0, 1]",
    "deviation_state": "implementation-defined enum",
    "trajectory_score": "number or null; heuristic, not probability",
    "trajectory_direction": "implementation-defined enum or null"
  },
  "supervised": {
    "status": "not_run, unavailable, or scored",
    "target_definition": "future Challenge-label-window entry",
    "horizon_hours": "1, 3, or 6",
    "probability": "number in [0, 1] or null",
    "model_version": "immutable model identifier or null",
    "calibration_version": "identifier or null"
  },
  "limitations": [
    "research-only",
    "not for patient-care decisions"
  ]
}
```

This is a proposed envelope, not an implemented API or guarantee that all fields already exist. The adapter must not manufacture missing model outputs. If features are unavailable, the model is not loaded, inputs fail quality checks, or model/version metadata do not match, return an explicit unavailable status and a null probability rather than zero.

## Required invariants

- Preserve original observation timestamps, units, quality flags, and provenance through ingestion.
- Reject stale/out-of-order data and expose coverage; do not silently impute a twin score when the twin is ineligible.
- Supervised inference must use only features available at the prediction timestamp. Any preprocessing and calibration must be fitted on the training/calibration partition only.
- Keep patient-level split boundaries intact. Set B is evaluation-only and cannot be used to fit, calibrate, select features, or choose a threshold.
- Record model, feature-schema, calibration, and configuration versions with each supervised result.
- Keep twin heuristic score and supervised probability in distinct fields with distinct semantics.
- Do not emit a clinical action, diagnosis, or recommendation.
- Tests must cover missing/stale channels, out-of-order events, warm-up, unavailable model, output schema, and no accidental twin-score-to-probability conversion.

## Validation required before release

1. Implement the envelope in a separate application adapter without changing either component's semantics.
2. Add contract tests and an end-to-end synthetic-only demonstration.
3. Verify that supervised inference is causal and uses the exact frozen feature schema.
4. Run the full test suite and demo from a clean checkout.
5. Keep all demonstrations synthetic-only unless authorized data governance explicitly permits otherwise.

VITALIS remains a research prototype, not a medical device or clinically validated decision-support system. Do not use outputs to guide patient care.
