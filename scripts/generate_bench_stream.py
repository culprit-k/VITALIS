"""Emit deterministic synthetic VITALIS bench envelopes as JSON Lines.

Examples:
  python scripts/generate_bench_stream.py --scenario nominal
  python scripts/generate_bench_stream.py --scenario dropout --frames 120
  python scripts/generate_bench_stream.py --scenario packet_loss --seed 7

All values are invented software fixtures. This script does not read or create
patient data and is not a physiological simulator or clinical validation tool.
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone

CHANNELS = {
    "heart_rate": ("bpm", 72.0, 2.0),
    "spo2": ("%", 98.0, 0.3),
    "respiratory_rate": ("breaths/min", 15.0, 0.8),
    "temperature": ("degC", 36.8, 0.05),
}


def envelopes(frames: int, seed: int, scenario: str):
    rng = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    sequence = 0
    for frame in range(frames):
        if scenario == "packet_loss" and frame > 0 and frame % 7 == 0:
            sequence += len(CHANNELS)
            continue
        for channel, (unit, center, spread) in CHANNELS.items():
            drift = max(0, frame - frames // 2) if scenario == "gradual_drift" else 0
            value = rng.gauss(center, spread)
            if channel == "heart_rate":
                value += 0.45 * drift
            elif channel == "spo2":
                value -= 0.08 * drift
            elif channel == "respiratory_rate":
                value += 0.12 * drift

            timestamp = start + timedelta(seconds=frame)
            quality = "good"
            missing_reason = None
            if scenario == "dropout" and channel == "spo2" and frame % 10 in {4, 5, 6}:
                quality = "missing"
                missing_reason = "not_sampled"
                value = None

            item = {
                "schema_version": "1.0.0",
                "session_id": "synthetic-bench-session",
                "source_id": "synthetic-simulator-1",
                "sequence": sequence,
                "channel": channel,
                "timestamp": timestamp.isoformat().replace("+00:00", "Z"),
                "quality": quality,
                "value": value,
                "unit": unit,
            }
            if missing_reason:
                item["missing_reason"] = missing_reason
            yield item
            sequence += 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--seed", type=int, default=20261123)
    parser.add_argument(
        "--scenario",
        choices=("nominal", "gradual_drift", "dropout", "packet_loss"),
        default="nominal",
    )
    args = parser.parse_args()
    if args.frames < 1 or args.frames > 100000:
        parser.error("--frames must be between 1 and 100000")
    for item in envelopes(args.frames, args.seed, args.scenario):
        print(json.dumps(item, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
