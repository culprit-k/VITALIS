"""Replay synthetic JSONL envelopes through the VITALIS adaptive twin.

This is an aggregate-only software bench. It emits no per-observation values,
patient records, clinical probabilities or recommendations.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Iterable, TextIO

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import TimestampedTwinStream
from vitalis.transport import SequenceTracker, parse_envelope, to_stream_observation


def replay_lines(lines: Iterable[str]) -> dict[str, object]:
    twin = AdaptivePhysiologicalTwin(
        channels=("heart_rate", "spo2", "respiratory_rate", "temperature"),
        config=TwinConfig(min_history=5, history_window=24, min_channels=2, min_systems=2),
    )
    stream = TimestampedTwinStream(twin, max_age_seconds=5.0)
    tracker = SequenceTracker()
    counts = Counter()
    states = Counter()
    coverages: list[float] = []
    eligible_frames = 0
    scored_frames = 0
    active_session: str | None = None
    current_timestamp: datetime | None = None
    current_observations = []

    def score_bucket() -> None:
        nonlocal scored_frames, eligible_frames
        if current_timestamp is None:
            return
        for observation in current_observations:
            if stream.ingest(observation):
                counts["stream_accepted"] += 1
            else:
                counts["stream_rejected"] += 1
        result = stream.score(current_timestamp)
        scored_frames += 1
        states[str(result["state"])] += 1
        coverages.append(float(result["coverage"]))
        if result["eligible"]:
            eligible_frames += 1

    for raw_line in lines:
        if not raw_line.strip():
            continue
        counts["lines_seen"] += 1
        try:
            envelope = parse_envelope(raw_line)
        except (TypeError, ValueError):
            counts["parse_rejected"] += 1
            continue

        if active_session is None:
            active_session = envelope.session_id
        elif envelope.session_id != active_session:
            counts["session_rejected"] += 1
            continue

        try:
            gap = tracker.accept(envelope)
        except ValueError:
            counts["sequence_rejected"] += 1
            continue
        counts["sequence_gaps"] += gap

        if current_timestamp is not None and envelope.timestamp < current_timestamp:
            counts["timestamp_order_rejected"] += 1
            continue
        if current_timestamp is not None and envelope.timestamp > current_timestamp:
            score_bucket()
            current_observations.clear()
            current_timestamp = envelope.timestamp
        elif current_timestamp is None:
            current_timestamp = envelope.timestamp

        if envelope.quality != "good":
            counts["non_good_quality"] += 1
            if envelope.quality == "missing":
                counts["explicit_missing"] += 1
            continue
        try:
            current_observations.append(to_stream_observation(envelope))
            counts["mappable_good_envelopes"] += 1
        except ValueError:
            counts["mapping_rejected"] += 1

    score_bucket()
    rejected_total = sum(
        counts[key] for key in (
            "parse_rejected", "session_rejected", "sequence_rejected",
            "timestamp_order_rejected", "mapping_rejected", "stream_rejected",
        )
    )
    return {
        "schema": "vitalis-bench-replay-summary-1.0.0",
        "mode": "synthetic_aggregate_only",
        "lines_seen": counts["lines_seen"],
        "mappable_good_envelopes": counts["mappable_good_envelopes"],
        "stream_accepted": counts["stream_accepted"],
        "stream_rejected": counts["stream_rejected"],
        "explicit_missing": counts["explicit_missing"],
        "non_good_quality": counts["non_good_quality"],
        "sequence_gaps": counts["sequence_gaps"],
        "rejected_total": rejected_total,
        "scored_frames": scored_frames,
        "eligible_frames": eligible_frames,
        "mean_coverage": round(sum(coverages) / len(coverages), 4) if coverages else 0.0,
        "trajectory_state_counts": dict(sorted(states.items())),
        "stream_rejection_counts": dict(sorted(stream.rejected.items())),
        "score_semantics": "unitless adaptive-twin heuristic; not a probability or clinical risk",
        "notice": "Synthetic software replay only; not sensor validation or a patient-care tool.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="JSONL file; defaults to stdin")
    args = parser.parse_args()
    if args.input:
        with args.input.open("r", encoding="utf-8") as handle:
            summary = replay_lines(handle)
    else:
        summary = replay_lines(sys.stdin)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
