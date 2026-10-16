"""Run a deterministic synthetic-data demonstration of the adaptive twin.

No real patient data are read or generated. The script illustrates software flow
only; its values and outputs have no clinical meaning.
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

UNITS = {
    "heart_rate": "bpm", "spo2": "%", "respiratory_rate": "breaths/min",
    "systolic_bp": "mmHg", "temperature": "degC",
}


def synthetic_stream(seed: int = 2026):
    rng = random.Random(seed)
    for step in range(36):
        drift = max(0, step - 23)
        yield {
            "heart_rate": rng.gauss(74 + 2.0 * drift, 2.0),
            "spo2": rng.gauss(98 - 0.45 * drift, 0.35),
            "respiratory_rate": rng.gauss(15 + 0.7 * drift, 1.0),
            "systolic_bp": rng.gauss(122 - 1.5 * drift, 3.0),
            "temperature": rng.gauss(36.8 + 0.06 * drift, 0.08),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    twin = AdaptivePhysiologicalTwin(
        config=TwinConfig(min_history=5, history_window=24, min_channels=2, min_systems=2)
    )
    stream = TimestampedTwinStream(twin, max_age_seconds=120)
    start = datetime(2026, 10, 14, tzinfo=timezone.utc)
    for step, observations in enumerate(synthetic_stream(args.seed)):
        timestamp = start + timedelta(minutes=step)
        for channel, value in observations.items():
            stream.ingest(Observation(channel, timestamp, value, UNITS[channel]))
        result = stream.score(timestamp)
        print(json.dumps({
            "step": step + 1,
            "state": result["state"],
            "coverage": round(float(result["coverage"]), 3),
            "trajectory_score": (
                None if result["trajectory_score"] is None
                else round(float(result["trajectory_score"]), 4)
            ),
            "trajectory_direction": result["trajectory_direction"],
            "cross_system_concordance": result["cross_system_concordance"],
        }, sort_keys=True))
    print(json.dumps({
        "notice": "Synthetic demonstration only; not a clinical forecast or patient-care tool."
    }))


if __name__ == "__main__":
    main()
