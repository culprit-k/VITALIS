"""Run a synthetic-only VITALIS replay bench and emit aggregate diagnostics.

No patient data is read or written. Per-frame observations and scores remain in
memory and are not included in the JSON report. This measures software replay
behavior only; it does not test sensor accuracy, electronics, electrical safety,
clinical performance, or a medical device.
"""
from __future__ import annotations

import argparse
import json
import math
import platform
import statistics
import sys
import time
import tracemalloc
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

CHANNELS = ("heart_rate", "spo2")
UNITS = {"heart_rate": "bpm", "spo2": "%"}
START = datetime(2026, 10, 17, 0, 0, tzinfo=timezone.utc)
MAX_AGE_SECONDS = 5.0
P95_TARGET_MS = 100.0
THROUGHPUT_TARGET_FPS = 10.0


def make_stream() -> TimestampedTwinStream:
    twin = AdaptivePhysiologicalTwin(
        channels=CHANNELS,
        config=TwinConfig(min_history=3, history_window=16, min_channels=2, min_systems=2),
    )
    return TimestampedTwinStream(twin, max_age_seconds=MAX_AGE_SECONDS)


def synthetic_observation(channel: str, at: datetime, step: int, source: str = "synthetic-A") -> Observation:
    # Deterministic, non-clinical signal. Values are test fixtures, not physiological guidance.
    if channel == "heart_rate":
        value = 72 + (step % 3) + max(0, step - 20) * 0.2
    else:
        value = 98 - max(0, step - 20) * 0.05
    return Observation(channel, at, value, UNITS[channel], quality="good", source=source)


def replay(frames: int, *, measure: bool) -> tuple[list[tuple[Any, ...]], list[float], int]:
    stream = make_stream()
    signatures: list[tuple[Any, ...]] = []
    latencies_ms: list[float] = []
    rejected_before = sum(stream.rejected.values())
    if measure:
        tracemalloc.start()
    for step in range(frames):
        at = START + timedelta(seconds=step)
        started = time.perf_counter()
        for channel in CHANNELS:
            if not stream.ingest(synthetic_observation(channel, at, step)):
                raise RuntimeError("generated valid observation was rejected")
        result = stream.score(at)
        latencies_ms.append((time.perf_counter() - started) * 1000)
        signatures.append((
            result["state"],
            round(float(result["coverage"]), 9),
            None if result["trajectory_score"] is None else round(float(result["trajectory_score"]), 12),
            result["eligible"],
        ))
    peak_bytes = tracemalloc.get_traced_memory()[1] if measure else 0
    if measure:
        tracemalloc.stop()
    rejected = sum(stream.rejected.values()) - rejected_before
    return signatures, latencies_ms, peak_bytes if measure else rejected


def run_bench(frames: int = 1000) -> dict[str, Any]:
    if frames < 30:
        raise ValueError("frames must be at least 30 to exercise warm-up and drift")
    signature, latencies, peak_bytes = replay(frames, measure=True)
    replay_signature, _, _ = replay(frames, measure=False)
    deterministic = signature == replay_signature

    # Fault-injection checks: all observations are synthetic and remain in memory.
    fault = make_stream()
    at = START
    fault.ingest(Observation("heart_rate", at, 72, "bpm", source="synthetic-A"))
    fault.ingest(Observation("spo2", at, 98, "%", source="synthetic-A"))
    fault.score(at)
    assert not fault.ingest(Observation("heart_rate", at + timedelta(seconds=1), 70, "beats/min"))
    assert not fault.ingest(Observation("spo2", at + timedelta(seconds=1), math.nan, "%"))
    assert not fault.ingest(Observation("spo2", at + timedelta(seconds=1), 98, "%", quality="poor"))
    assert not fault.ingest(Observation("heart_rate", at, 72, "bpm", source="synthetic-A"))
    fault.score(at + timedelta(seconds=MAX_AGE_SECONDS + 2))
    stale_coverage_zero = fault.score(at + timedelta(seconds=MAX_AGE_SECONDS + 2))["coverage"] == 0

    recovery_time = at + timedelta(seconds=MAX_AGE_SECONDS + 3)
    assert fault.ingest(Observation("heart_rate", recovery_time, 73, "bpm", source="synthetic-A"))
    assert fault.ingest(Observation("spo2", recovery_time, 97, "%", source="synthetic-A"))
    recovery_coverage_full = fault.score(recovery_time)["coverage"] == 1.0

    replacement_time = recovery_time + timedelta(seconds=1)
    assert fault.ingest(Observation("heart_rate", replacement_time, 74, "bpm", source="synthetic-B"))
    fault.score(replacement_time)
    source_replacement_counted = fault.source_change_counts["heart_rate"] == 1
    bad_unit_rejected = fault.rejected["bad_unit"] == 1
    non_finite_value_rejected = fault.rejected["bad_value"] == 1
    poor_quality_rejected = fault.rejected["bad_quality"] == 1
    out_of_order_rejected = fault.rejected["out_of_order"] == 1
    fault.reset()
    reset_clears_state = fault.twin.steps == 0 and all(not state.values for state in fault.twin.states.values())
    reset_coverage_zero = fault.score(replacement_time + timedelta(seconds=1))["coverage"] == 0

    sorted_latencies = sorted(latencies)
    p95 = sorted_latencies[min(len(sorted_latencies) - 1, math.ceil(0.95 * len(sorted_latencies)) - 1)]
    elapsed_seconds = sum(latencies) / 1000
    throughput = frames / elapsed_seconds if elapsed_seconds else 0.0
    functional_checks = {
        "valid_replay_completed": len(signature) == frames,
        "deterministic_replay": deterministic,
        "bad_unit_rejected": bad_unit_rejected,
        "non_finite_value_rejected": non_finite_value_rejected,
        "poor_quality_rejected": poor_quality_rejected,
        "out_of_order_rejected": out_of_order_rejected,
        "stale_data_not_scored": stale_coverage_zero,
        "valid_data_recovers_after_dropout": recovery_coverage_full,
        "source_replacement_counted": source_replacement_counted,
        "reset_clears_session_state": reset_clears_state and reset_coverage_zero,
    }
    return {
        "report_schema": "vitalis.synthetic-replay-bench.v1",
        "scope": "synthetic_software_replay_only",
        "clinical_use": False,
        "patient_data_used": False,
        "row_level_data_retained": False,
        "frames_replayed": frames,
        "channels_per_frame": len(CHANNELS),
        "max_age_seconds": MAX_AGE_SECONDS,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "processor": platform.processor() or "not-reported",
        },
        "latency_ms": {
            "median": round(statistics.median(latencies), 4),
            "p95": round(p95, 4),
            "max": round(max(latencies), 4),
        },
        "throughput_frames_per_second": round(throughput, 2),
        "tracemalloc_peak_bytes": peak_bytes,
        "provisional_engineering_targets": {
            "p95_latency_ms_at_most": P95_TARGET_MS,
            "throughput_frames_per_second_at_least": THROUGHPUT_TARGET_FPS,
            "targets_met": p95 <= P95_TARGET_MS and throughput >= THROUGHPUT_TARGET_FPS,
            "note": "Prototype engineering targets only; not clinical or safety limits.",
        },
        "functional_checks": functional_checks,
        "functional_status": "pass" if all(functional_checks.values()) else "fail",
        "performance_status": "within_provisional_targets" if p95 <= P95_TARGET_MS and throughput >= THROUGHPUT_TARGET_FPS else "needs_review",
        "limitations": [
            "Synthetic values only; no real sensor or hardware was connected.",
            "Latency is host- and load-dependent and must be remeasured on the intended bench computer.",
            "No electrical safety, sensor accuracy, cybersecurity, clinical validity, or medical-device compliance is established.",
            "Twin scores are unitless research heuristics, not calibrated clinical probabilities.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=int, default=1000, help="synthetic frames to replay (minimum 30)")
    parser.add_argument("--output", type=Path, help="optional path for aggregate JSON report")
    args = parser.parse_args()
    report = run_bench(args.frames)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["functional_status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
