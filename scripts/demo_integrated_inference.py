"""Synthetic-only demonstration of the twin + optional supervised interface.

No patient data or trained clinical model is used. The default demonstration
intentionally shows supervised outputs as unavailable because no frozen model
artifact is supplied. It must not be used for patient-care decisions.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.integrated_inference import IntegratedResearchInference
from vitalis.stream import Observation, TimestampedTwinStream


UNITS = {"heart_rate": "bpm", "spo2": "%"}


def main() -> None:
    twin = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2"],
        config=TwinConfig(min_history=3, history_window=8, min_channels=2, min_systems=2),
    )
    stream = TimestampedTwinStream(twin, max_age_seconds=120)
    app = IntegratedResearchInference(stream)
    start = datetime(2026, 10, 16, tzinfo=timezone.utc)

    for step in range(8):
        timestamp = start + timedelta(minutes=step)
        drift = max(0, step - 4)
        app.ingest(Observation("heart_rate", timestamp, 72 + 9 * drift, UNITS["heart_rate"]))
        app.ingest(Observation("spo2", timestamp, 98 - 2 * drift, UNITS["spo2"]))
        result = app.score(timestamp)
        print(json.dumps(result, sort_keys=True))

    print(json.dumps({
        "notice": "Synthetic software demonstration only.",
        "supervised_model": "not supplied; probabilities intentionally unavailable",
        "clinical_use": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
