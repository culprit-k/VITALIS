from datetime import datetime, timedelta, timezone

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream


def make_stream(max_age=60):
    twin = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2"],
        config=TwinConfig(min_history=2, history_window=4, min_channels=2, min_systems=2),
    )
    return TimestampedTwinStream(twin, max_age_seconds=max_age)


def test_ingest_requires_known_units_and_good_quality():
    stream = make_stream()
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    assert stream.ingest(Observation("heart_rate", now, 70, "bpm"))
    assert not stream.ingest(Observation("spo2", now, 98, "mmHg"))
    assert not stream.ingest(Observation("spo2", now, 98, "%", quality="suspect"))
    assert stream.rejected["bad_unit"] == 1
    assert stream.rejected["bad_quality"] == 1


def test_naive_timestamp_is_rejected():
    stream = make_stream()
    assert not stream.ingest(Observation("heart_rate", datetime(2026, 10, 14), 70, "bpm"))
    assert stream.rejected["bad_time"] == 1


def test_out_of_order_sample_does_not_replace_latest_value():
    stream = make_stream()
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    assert stream.ingest(Observation("heart_rate", now, 70, "bpm"))
    assert not stream.ingest(Observation("heart_rate", now - timedelta(seconds=1), 99, "bpm"))
    result = stream.score(now + timedelta(seconds=2))
    assert result["channels"]["heart_rate"]["value"] == 70
    assert stream.rejected["out_of_order"] == 1


def test_stale_samples_become_missing():
    stream = make_stream(max_age=10)
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    stream.ingest(Observation("heart_rate", now, 70, "bpm"))
    result = stream.score(now + timedelta(seconds=11))
    assert result["coverage"] == 0
    assert result["channels"] == {}
    assert result["channel_age_seconds"]["heart_rate"] == 11


def test_reset_clears_stream_and_twin_state():
    stream = make_stream()
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    stream.ingest(Observation("heart_rate", now, 70, "bpm"))
    stream.reset()
    result = stream.score(now + timedelta(seconds=1))
    assert result["coverage"] == 0
    assert result["step"] == 1
    assert stream.rejected["bad_unit"] == 0


def test_timestamped_stream_drives_twin_after_warmup():
    stream = make_stream(max_age=60)
    start = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    for index in range(3):
        timestamp = start + timedelta(seconds=index)
        stream.ingest(Observation("heart_rate", timestamp, 70, "bpm"))
        stream.ingest(Observation("spo2", timestamp, 98, "%"))
        result = stream.score(timestamp)
    timestamp = start + timedelta(seconds=3)
    stream.ingest(Observation("heart_rate", timestamp, 110, "bpm"))
    stream.ingest(Observation("spo2", timestamp, 90, "%"))
    result = stream.score(timestamp)
    assert result["eligible"] is True
    assert result["channels"]["heart_rate"]["baseline"] == 70
    assert result["trajectory_score"] is not None
    assert result["channel_age_seconds"]["spo2"] == 0



def test_per_channel_freshness_limits_are_respected_independently():
    twin = AdaptivePhysiologicalTwin(
        channels=["heart_rate", "spo2"],
        config=TwinConfig(min_history=2, history_window=4, min_channels=1, min_systems=1),
    )
    stream = TimestampedTwinStream(twin, max_age_seconds={"heart_rate": 5, "spo2": 30})
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    assert stream.ingest(Observation("heart_rate", now, 70, "bpm"))
    assert stream.ingest(Observation("spo2", now, 98, "%"))
    result = stream.score(now + timedelta(seconds=10))
    assert result["channels"] == {"spo2": {"value": 98.0, "baseline": None,
        "reference_baseline": None, "z_score": None, "reference_z_score": None,
        "cusum_score": 0.0, "cusum_triggered": False, "history_count": 0,
        "baseline_updated": True}}
    assert result["coverage"] == 0.5
    assert result["channel_age_seconds"]["heart_rate"] == 10
    assert result["channel_age_seconds"]["spo2"] == 10


def test_per_channel_freshness_mapping_must_match_twin_channels():
    twin = AdaptivePhysiologicalTwin(channels=["heart_rate", "spo2"])
    try:
        TimestampedTwinStream(twin, max_age_seconds={"heart_rate": 10})
    except ValueError as exc:
        assert "missing: spo2" in str(exc)
    else:
        raise AssertionError("missing channel freshness policy should be rejected")


def test_future_dated_sample_is_not_used_until_stream_time_catches_up():
    stream = make_stream(max_age=10)
    now = datetime(2026, 10, 14, 12, tzinfo=timezone.utc)
    future = now + timedelta(seconds=5)
    assert stream.ingest(Observation("heart_rate", future, 80, "bpm"))
    result = stream.score(now)
    assert result["coverage"] == 0
    assert result["channel_age_seconds"]["heart_rate"] == -5
