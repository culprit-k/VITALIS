"""Timestamped, unit-checked observation adapter for VITALIS.

This module is the boundary between future sensor adapters and the twin. It
keeps no patient identifier and persists no data. Unit and freshness defaults
are engineering contracts, not clinical quality or alarm thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Mapping

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin

DEFAULT_UNITS = {
    "heart_rate": "bpm",
    "hrv": "ms",
    "systolic_bp": "mmHg",
    "diastolic_bp": "mmHg",
    "spo2": "%",
    "respiratory_rate": "breaths/min",
    "temperature": "degC",
    "peripheral_temperature": "degC",
    "capillary_refill_seconds": "s",
}


@dataclass(frozen=True)
class Observation:
    channel: str
    timestamp: datetime
    value: float | int | None
    unit: str
    quality: str = "good"
    source: str | None = None


class TimestampedTwinStream:
    """Validate measurements, retain the latest fresh value, then score a frame."""

    def __init__(
        self,
        twin: AdaptivePhysiologicalTwin,
        *,
        channel_units: Mapping[str, str] | None = None,
        max_age_seconds: float | Mapping[str, float] = 60.0,
    ):
        self.twin = twin
        units = dict(DEFAULT_UNITS)
        units.update(channel_units or {})
        missing = set(twin.channels).difference(units)
        if missing:
            raise ValueError("Provide units for channels: " + ", ".join(sorted(missing)))
        self.channel_units = {name: units[name] for name in twin.channels}
        if isinstance(max_age_seconds, Mapping):
            missing_age_channels = set(twin.channels).difference(max_age_seconds)
            unknown_age_channels = set(max_age_seconds).difference(twin.channels)
            if missing_age_channels or unknown_age_channels:
                details = []
                if missing_age_channels:
                    details.append("missing: " + ", ".join(sorted(missing_age_channels)))
                if unknown_age_channels:
                    details.append("unknown: " + ", ".join(sorted(unknown_age_channels)))
                raise ValueError("max_age_seconds channel mapping mismatch (" + "; ".join(details) + ")")
            try:
                self.max_age = {name: float(max_age_seconds[name]) for name in twin.channels}
            except (TypeError, ValueError) as exc:
                raise ValueError("all max_age_seconds values must be numeric") from exc
        else:
            try:
                self.max_age = {name: float(max_age_seconds) for name in twin.channels}
            except (TypeError, ValueError) as exc:
                raise ValueError("max_age_seconds must be numeric or a per-channel mapping") from exc
        if any(not isfinite(age) or age <= 0 for age in self.max_age.values()):
            raise ValueError("all max_age_seconds values must be finite and positive")
        self._latest: dict[str, Observation] = {}
        self._last_timestamp: dict[str, datetime] = {}
        self._source_by_channel: dict[str, str | None] = {}
        self.source_change_counts = {name: 0 for name in twin.channels}
        self.rejected = {"unknown_channel": 0, "bad_time": 0, "bad_unit": 0,
                         "bad_quality": 0, "bad_value": 0, "out_of_order": 0}

    @staticmethod
    def _utc(value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(timezone.utc)

    def ingest(self, observation: Observation) -> bool:
        """Accept only known, good-quality, finite, correctly-unitized new samples."""
        channel = observation.channel
        if channel not in self.channel_units:
            self.rejected["unknown_channel"] += 1
            return False
        try:
            timestamp = self._utc(observation.timestamp)
        except (AttributeError, ValueError):
            self.rejected["bad_time"] += 1
            return False
        if observation.unit != self.channel_units[channel]:
            self.rejected["bad_unit"] += 1
            return False
        if observation.quality != "good":
            self.rejected["bad_quality"] += 1
            return False
        if observation.value is None:
            self.rejected["bad_value"] += 1
            return False
        try:
            value = float(observation.value)
        except (TypeError, ValueError):
            self.rejected["bad_value"] += 1
            return False
        if not isfinite(value):
            self.rejected["bad_value"] += 1
            return False
        previous = self._last_timestamp.get(channel)
        if previous is not None and timestamp <= previous:
            self.rejected["out_of_order"] += 1
            return False
        previous_source = self._source_by_channel.get(channel)
        if previous_source is not None and observation.source is not None and previous_source != observation.source:
            # Never mix two identified sensors' histories. The replacement sample
            # starts a fresh channel history and resets aggregate trajectory continuity.
            self.twin.reset_channel(channel)
            self.source_change_counts[channel] += 1
        normalized = Observation(
            channel=channel, timestamp=timestamp, value=value,
            unit=observation.unit, quality=observation.quality, source=observation.source,
        )
        self._latest[channel] = normalized
        self._last_timestamp[channel] = timestamp
        if observation.source is not None:
            self._source_by_channel[channel] = observation.source
        return True

    def score(self, at_time: datetime) -> dict[str, object]:
        """Align latest values to a timezone-aware time; stale values become missing."""
        now = self._utc(at_time)
        values: dict[str, float | None] = {}
        ages: dict[str, float | None] = {}
        for channel in self.twin.channels:
            observation = self._latest.get(channel)
            if observation is None:
                values[channel] = None
                ages[channel] = None
                continue
            age = (now - observation.timestamp).total_seconds()
            if 0 <= age <= self.max_age[channel]:
                values[channel] = float(observation.value)
                ages[channel] = age
            else:
                values[channel] = None
                ages[channel] = age
        result = self.twin.update(values)
        result["channel_age_seconds"] = ages
        result["rejected_observation_counts"] = dict(self.rejected)
        result["source_change_counts"] = dict(self.source_change_counts)
        result["stream_semantics"] = (
            "Latest fresh value per channel; unit-checked; no persistence; not clinical validation."
        )
        return result

    def reset(self) -> None:
        """Clear buffers and patient-specific twin state before a new session."""
        self._latest.clear()
        self._last_timestamp.clear()
        self._source_by_channel.clear()
        for channel in self.source_change_counts:
            self.source_change_counts[channel] = 0
        for key in self.rejected:
            self.rejected[key] = 0
        self.twin.reset()
