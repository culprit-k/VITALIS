"""Strict parser for the VITALIS synthetic/non-human bench transport envelope.

This module validates transport metadata before mapping supported scalar channels
to the existing TimestampedTwinStream Observation model. It is not a clinical
device protocol or a medical-data interchange standard.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Any

from vitalis.stream import DEFAULT_UNITS, Observation

SCHEMA_VERSION = "1.0.0"
MAX_MESSAGE_BYTES = 2048
ALLOWED_FIELDS = {
    "schema_version", "session_id", "source_id", "sequence", "channel",
    "timestamp", "quality", "value", "unit", "missing_reason",
    "sample_rate_hz", "calibration_revision",
}
CHANNEL_UNITS = {
    **DEFAULT_UNITS,
    "accelerometer_x": "m/s^2",
    "accelerometer_y": "m/s^2",
    "accelerometer_z": "m/s^2",
    "ecg_sample": "mV",
}
QUALITIES = {"good", "suspect", "bad", "missing"}
MISSING_REASONS = {
    "not_sampled", "sensor_unavailable", "transport_loss",
    "quality_rejected", "not_applicable",
}


@dataclass(frozen=True)
class BenchEnvelope:
    schema_version: str
    session_id: str
    source_id: str
    sequence: int
    channel: str
    timestamp: datetime
    quality: str
    value: float | None
    unit: str
    missing_reason: str | None = None
    sample_rate_hz: float | None = None
    calibration_revision: str | None = None


def _nonempty_string(value: Any, field: str, max_length: int = 64) -> str:
    if not isinstance(value, str) or not value or len(value) > max_length:
        raise ValueError(f"{field} must be a non-empty string of at most {max_length} characters")
    return value


def parse_envelope(message: str | bytes) -> BenchEnvelope:
    """Parse and strictly validate one UTF-8 JSONL envelope."""
    if isinstance(message, bytes):
        if len(message) > MAX_MESSAGE_BYTES:
            raise ValueError("message exceeds maximum byte length")
        try:
            text = message.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("message must be UTF-8") from exc
    elif isinstance(message, str):
        try:
            encoded = message.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ValueError("message must be valid UTF-8") from exc
        if len(encoded) > MAX_MESSAGE_BYTES:
            raise ValueError("message exceeds maximum byte length")
        text = message
    else:
        raise ValueError("message must be str or bytes")

    text = text.rstrip("\r\n")
    if not text:
        raise ValueError("message is empty")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("message is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("envelope must be a JSON object")

    unknown = set(payload).difference(ALLOWED_FIELDS)
    if unknown:
        raise ValueError("unknown envelope fields: " + ", ".join(sorted(unknown)))
    required = {
        "schema_version", "session_id", "source_id", "sequence",
        "channel", "timestamp", "quality", "value", "unit",
    }
    missing = required.difference(payload)
    if missing:
        raise ValueError("missing envelope fields: " + ", ".join(sorted(missing)))

    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")
    session_id = _nonempty_string(payload["session_id"], "session_id")
    source_id = _nonempty_string(payload["source_id"], "source_id")
    sequence = payload["sequence"]
    if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
        raise ValueError("sequence must be a non-negative integer")

    channel = _nonempty_string(payload["channel"], "channel", 64)
    if channel not in CHANNEL_UNITS:
        raise ValueError("unknown channel")
    unit = _nonempty_string(payload["unit"], "unit", 32)
    if unit != CHANNEL_UNITS[channel]:
        raise ValueError("unit does not match channel")

    timestamp_text = _nonempty_string(payload["timestamp"], "timestamp", 64)
    try:
        timestamp = datetime.fromisoformat(timestamp_text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be RFC 3339 date-time") from exc
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("timestamp must include an explicit UTC offset")

    quality = payload["quality"]
    if not isinstance(quality, str) or quality not in QUALITIES:
        raise ValueError("quality must be good, suspect, bad or missing")

    raw_value = payload["value"]
    value: float | None
    if raw_value is None:
        value = None
    else:
        if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
            raise ValueError("value must be a finite number or null")
        try:
            value = float(raw_value)
        except OverflowError as exc:
            raise ValueError("value must be finite") from exc
        if not isfinite(value):
            raise ValueError("value must be finite")

    missing_reason = payload.get("missing_reason")
    if missing_reason is not None and (not isinstance(missing_reason, str) or missing_reason not in MISSING_REASONS):
        raise ValueError("invalid missing_reason")
    if quality == "good" and value is None:
        raise ValueError("good-quality observations require a numeric value")
    if quality in {"bad", "missing"}:
        if value is not None:
            raise ValueError("bad/missing observations must have a null value")
        if missing_reason is None:
            raise ValueError("bad/missing observations require missing_reason")
    if quality == "suspect" and value is None and missing_reason is None:
        raise ValueError("suspect null observations require missing_reason")

    sample_rate = payload.get("sample_rate_hz")
    if sample_rate is not None:
        if isinstance(sample_rate, bool) or not isinstance(sample_rate, (int, float)):
            raise ValueError("sample_rate_hz must be numeric")
        sample_rate = float(sample_rate)
        if not isfinite(sample_rate) or sample_rate <= 0:
            raise ValueError("sample_rate_hz must be finite and positive")

    calibration = payload.get("calibration_revision")
    if calibration is not None:
        calibration = _nonempty_string(calibration, "calibration_revision")

    return BenchEnvelope(
        schema_version=SCHEMA_VERSION,
        session_id=session_id,
        source_id=source_id,
        sequence=sequence,
        channel=channel,
        timestamp=timestamp,
        quality=quality,
        value=value,
        unit=unit,
        missing_reason=missing_reason,
        sample_rate_hz=sample_rate,
        calibration_revision=calibration,
    )


class SequenceTracker:
    """Track per-session/source monotonic sequence numbers without filling gaps."""

    def __init__(self) -> None:
        self._last: dict[tuple[str, str], int] = {}
        self.gaps: dict[tuple[str, str], int] = {}

    def accept(self, envelope: BenchEnvelope) -> int:
        """Accept a new sequence and return the number of missing frames before it."""
        key = (envelope.session_id, envelope.source_id)
        previous = self._last.get(key)
        if previous is not None and envelope.sequence <= previous:
            raise ValueError("duplicate or out-of-order sequence")
        gap = 0 if previous is None else envelope.sequence - previous - 1
        self._last[key] = envelope.sequence
        self.gaps[key] = self.gaps.get(key, 0) + gap
        return gap

    def reset_session(self, session_id: str) -> None:
        """Forget sequence state for one explicit bench session."""
        for key in [key for key in self._last if key[0] == session_id]:
            self._last.pop(key, None)
            self.gaps.pop(key, None)


def to_stream_observation(envelope: BenchEnvelope) -> Observation:
    """Map a good supported scalar envelope to the existing stream interface."""
    if envelope.quality != "good" or envelope.value is None:
        raise ValueError("only good-quality numeric observations can enter the twin stream")
    if envelope.channel not in DEFAULT_UNITS:
        raise ValueError("channel is not supported by the current scalar twin stream")
    if DEFAULT_UNITS[envelope.channel] != envelope.unit:
        raise ValueError("unit does not match current twin stream contract")
    return Observation(
        channel=envelope.channel,
        timestamp=envelope.timestamp,
        value=envelope.value,
        unit=envelope.unit,
        quality="good",
        source=envelope.source_id,
    )
