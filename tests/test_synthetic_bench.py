"""Synthetic-only bench contract tests for the VITALIS stream boundary.

These tests verify software behavior using generated observations. They do not
verify sensor accuracy, electrical safety, clinical performance, or device integration.
"""
from datetime import datetime, timedelta, timezone
import math

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

UTC = timezone.utc
START = datetime(2026, 10, 17, 0, 0, tzinfo=UTC)
UNITS = {"heart_rate": "bpm", "spo2": "%"}
CHANNELS = ("heart_rate", "spo2")


def make_stream(max_age_seconds=120):
    twin = AdaptivePhysiologicalTwin(
        channels=CHANNELS,
        config=TwinConfig(min_history=3, history_window=6, min_channels=2, min_systems=2),
    )
    return TimestampedTwinStream(twin, max_age_seconds=max_age_seconds)


def obs(channel, timestamp, value, unit=None, quality="good", source="bench-A"):
    return Observation(
        channel=channel,
        timestamp=timestamp,
        value=value,
        unit=unit or UNITS[channel],
        quality=quality,
        source=source,
    )


def feed_frame(stream, step, hr=72, spo2=98, source="bench-A"):
    timestamp = START + timedelta(minutes=step)
    assert stream.ingest(obs("heart_rate", timestamp, hr, source=source))
    assert stream.ingest(obs("spo2", timestamp, spo2, source=source))
    return timestamp


def test_synthetic_replay_builds_baseline_and_scores_without_patient_data():
    stream = make_stream()
    for step in range(6):
        at = feed_frame(stream, step, hr=72 + (step % 2), spo2=98)
        result = stream.score(at)
    assert stream.twin.steps == 6
    assert result["coverage"] > 0
    assert result["stream_semantics"].startswith("Latest fresh value per channel")
    assert "patient_id" not in result and "predictions" not in result


def test_stream_rejects_unknown_channel_bad_unit_quality_nonfinite_and_naive_time():
    stream = make_stream()
    assert not stream.ingest(Observation("unknown", START, 1, "x"))
    assert not stream.ingest(obs("heart_rate", START, 72, unit="beats/min"))
    assert not stream.ingest(obs("heart_rate", START, 72, quality="poor"))
    assert not stream.ingest(obs("heart_rate", START, math.nan))
    assert not stream.ingest(Observation("heart_rate", datetime(2026, 10, 17), 72, "bpm"))
    assert stream.rejected["unknown_channel"] == 1
    assert stream.rejected["bad_unit"] == 1
    assert stream.rejected["bad_quality"] == 1
    assert stream.rejected["bad_value"] == 1
    assert stream.rejected["bad_time"] == 1


def test_out_of_order_sample_is_rejected_without_replacing_latest():
    stream = make_stream()
    latest = feed_frame(stream, 3)
    assert not stream.ingest(obs("heart_rate", latest - timedelta(minutes=1), 150))
    assert stream.rejected["out_of_order"] == 1
    result = stream.score(latest)
    assert result["channel_age_seconds"]["heart_rate"] == 0


def test_stale_values_are_reported_as_missing_at_score_time():
    stream = make_stream(max_age_seconds=60)
    at = feed_frame(stream, 0)
    result = stream.score(at + timedelta(minutes=5))
    assert result["channel_age_seconds"]["heart_rate"] == 300
    assert result["channel_age_seconds"]["spo2"] == 300
    assert result["coverage"] == 0


def test_source_replacement_is_counted_and_starts_new_channel_history():
    stream = make_stream()
    at = feed_frame(stream, 0, source="bench-A")
    replacement_time = at + timedelta(minutes=1)
    assert stream.ingest(obs("heart_rate", replacement_time, 74, source="bench-B"))
    assert stream.source_change_counts["heart_rate"] == 1
    # The stream buffers accepted observations; the twin consumes the replacement
    # sample only when the next aligned frame is scored.
    stream.score(replacement_time)
    assert stream.twin.states["heart_rate"].values == [74.0]


def test_reset_clears_session_state_and_diagnostics():
    stream = make_stream()
    at = feed_frame(stream, 0)
    stream.ingest(obs("heart_rate", at, 100))
    stream.score(at)
    stream.reset()
    assert stream.twin.steps == 0
    assert stream.rejected["out_of_order"] == 0
    assert stream.source_change_counts["heart_rate"] == 0
    result = stream.score(at + timedelta(minutes=1))
    assert result["coverage"] == 0
