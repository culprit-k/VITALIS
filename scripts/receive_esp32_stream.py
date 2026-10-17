"""USB-serial receiver for VITALIS synthetic ESP32 gateway.

Generated bench data only. Does not persist observations or make clinical predictions.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from typing import TextIO

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

SOURCE = "esp32-synthetic-v1"
CHANNELS = {"heart_rate": "bpm", "spo2": "%"}
SCHEMA_VERSION = 1


def parse_message(line: str, session_start: datetime) -> tuple[int, Observation] | None:
    """Parse one newline-delimited gateway message; return None for its boot banner."""
    if session_start.tzinfo is None or session_start.utcoffset() is None:
        raise ValueError("session_start must be timezone-aware")
    try:
        message = json.loads(line)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ValueError("invalid JSON line") from exc
    if not isinstance(message, dict):
        raise ValueError("message must be a JSON object")
    if message.get("type") == "vitalis_gateway_ready":
        if message.get("mode") != "synthetic_only" or message.get("schema") != SCHEMA_VERSION:
            raise ValueError("unsupported gateway banner")
        return None

    required = {"seq", "elapsed_ms", "channel", "value", "unit", "quality", "source"}
    if set(message) != required:
        raise ValueError("message fields do not match schema v1")
    seq = message["seq"]
    elapsed_ms = message["elapsed_ms"]
    if isinstance(seq, bool) or not isinstance(seq, int) or seq < 0:
        raise ValueError("seq must be a non-negative integer")
    if isinstance(elapsed_ms, bool) or not isinstance(elapsed_ms, int) or elapsed_ms < 0:
        raise ValueError("elapsed_ms must be a non-negative integer")
    channel = message["channel"]
    if channel not in CHANNELS:
        raise ValueError("unsupported channel")
    if message["unit"] != CHANNELS[channel]:
        raise ValueError("unit mismatch")
    if message["quality"] != "good":
        raise ValueError("quality must be good")
    if message["source"] != SOURCE:
        raise ValueError("unexpected source")
    raw_value = message["value"]
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
        raise ValueError("value must be numeric")
    value = float(raw_value)
    if not math.isfinite(value):
        raise ValueError("value must be finite")

    timestamp = (session_start.astimezone(timezone.utc) +
                 timedelta(milliseconds=elapsed_ms))
    return seq, Observation(channel, timestamp, value, message["unit"],
                            quality=message["quality"], source=message["source"])


def make_stream() -> TimestampedTwinStream:
    twin = AdaptivePhysiologicalTwin(
        channels=list(CHANNELS),
        config=TwinConfig(min_history=5, history_window=48, min_channels=2, min_systems=2),
    )
    return TimestampedTwinStream(twin, channel_units=CHANNELS, max_age_seconds=10)


def run_lines(lines: TextIO, *, output: TextIO = sys.stdout) -> int:
    """Process input lines without writing raw messages or per-sample values to disk."""
    session_start: datetime | None = None
    stream = make_stream()
    accepted = rejected = banners = 0
    last_seq = -1
    last_seq_by_channel: dict[str, int] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        try:
            provisional_anchor = session_start or datetime.now(timezone.utc)
            parsed = parse_message(line, provisional_anchor)
            if parsed is None:
                banners += 1
                if session_start is not None:
                    # A repeated ready banner indicates a gateway reboot. Start
                    # a clean in-memory twin session so the device sequence can
                    # restart at zero without mixing pre- and post-reboot data.
                    stream.reset()
                    session_start = None
                    last_seq = -1
                    last_seq_by_channel.clear()
                continue
            seq, observation = parsed
            if session_start is None:
                # The ESP32 elapsed clock began at boot, possibly before the
                # laptop receiver started. Anchor the first sample to receipt
                # time, then preserve subsequent elapsed-time differences.
                elapsed = observation.timestamp - provisional_anchor
                session_start = datetime.now(timezone.utc) - elapsed
                observation = Observation(
                    observation.channel,
                    session_start + elapsed,
                    observation.value,
                    observation.unit,
                    quality=observation.quality,
                    source=observation.source,
                )
            if seq < last_seq:
                raise ValueError("sequence number regressed")
            previous_channel_seq = last_seq_by_channel.get(observation.channel, -1)
            if seq <= previous_channel_seq:
                raise ValueError("duplicate or regressed channel sequence")
            last_seq = seq
            last_seq_by_channel[observation.channel] = seq
            if not stream.ingest(observation):
                rejected += 1
                continue
            accepted += 1
            result = stream.score(observation.timestamp)
            summary = {
                "type": "vitalis_twin_summary",
                "accepted_messages": accepted,
                "rejected_messages": rejected,
                "sequence": seq,
                "coverage": result["coverage"],
                "eligible": result["eligible"],
                "state": result["state"],
                "trajectory_score": result["trajectory_score"],
                "score_semantics": "unitless heuristic; not a probability or clinical risk",
                "research_only": True,
            }
            print(json.dumps(summary, separators=(",", ":"), allow_nan=False), file=output)
        except (ValueError, OverflowError) as exc:
            rejected += 1
            print(json.dumps({"type": "gateway_rejection", "reason": str(exc),
                              "rejected_messages": rejected}), file=output)
    print(json.dumps({"type": "gateway_session_summary", "accepted_messages": accepted,
                      "rejected_messages": rejected, "ready_banners": banners,
                      "raw_data_persisted": False, "research_only": True}),
          file=output)
    return 0 if rejected == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--port", help="USB serial port, e.g. COM4 or /dev/ttyACM0")
    source.add_argument("--stdin", action="store_true",
                        help="read newline-delimited messages from stdin for offline tests")
    parser.add_argument("--baud", type=int, default=115200)
    args = parser.parse_args()
    if args.baud <= 0:
        parser.error("--baud must be positive")
    if args.stdin:
        return run_lines(sys.stdin)
    try:
        import serial  # type: ignore[import-not-found]
    except ImportError:
        print('Install optional serial support with: pip install pyserial', file=sys.stderr)
        return 3
    try:
        with serial.Serial(args.port, args.baud, timeout=1) as device:
            print("Connected. Ctrl+C to stop. Synthetic bench mode only.", file=sys.stderr)
            return run_lines(device)
    except KeyboardInterrupt:
        return 130
    except serial.SerialException as exc:
        print(f"Serial connection failed: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
