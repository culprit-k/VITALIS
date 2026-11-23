import json
import pytest

from vitalis.transport import (
    SequenceTracker,
    parse_envelope,
    to_stream_observation,
)


def payload(**overrides):
    value = {
        "schema_version": "1.0.0",
        "session_id": "bench-session-1",
        "source_id": "simulator-1",
        "sequence": 0,
        "channel": "heart_rate",
        "timestamp": "2026-11-23T10:00:00Z",
        "quality": "good",
        "value": 72.5,
        "unit": "bpm",
    }
    value.update(overrides)
    return value


def parse(**overrides):
    return parse_envelope(json.dumps(payload(**overrides)))


def test_valid_envelope_normalizes_utc_timestamp():
    envelope = parse(timestamp="2026-11-23T15:00:00+05:00")
    assert envelope.timestamp.utcoffset().total_seconds() == 0
    assert envelope.value == 72.5


@pytest.mark.parametrize("overrides", [
    {"schema_version": "2.0.0"},
    {"sequence": -1},
    {"sequence": True},
    {"channel": "unknown"},
    {"unit": "mmHg"},
    {"timestamp": "2026-11-23T10:00:00"},
    {"quality": "excellent"},
    {"value": float("inf")},
    {"value": "72"},
    {"unexpected": "field"},
])
def test_invalid_envelopes_are_rejected(overrides):
    with pytest.raises(ValueError):
        parse(**overrides)


def test_bad_and_missing_values_require_null_and_reason():
    with pytest.raises(ValueError):
        parse(quality="missing", value=None)
    missing = parse(
        quality="missing", value=None, missing_reason="transport_loss"
    )
    assert missing.value is None
    with pytest.raises(ValueError):
        parse(quality="bad", value=72.0, missing_reason="quality_rejected")


def test_suspect_observation_cannot_be_mapped_to_twin():
    envelope = parse(quality="suspect")
    with pytest.raises(ValueError):
        to_stream_observation(envelope)


def test_ecg_placeholder_is_not_mapped_to_scalar_twin():
    envelope = parse(channel="ecg_sample", unit="mV")
    with pytest.raises(ValueError):
        to_stream_observation(envelope)


def test_supported_observation_maps_with_source_and_timestamp():
    envelope = parse()
    observation = to_stream_observation(envelope)
    assert observation.channel == "heart_rate"
    assert observation.value == 72.5
    assert observation.source == "simulator-1"
    assert observation.timestamp.tzinfo is not None


def test_sequence_tracker_detects_gaps_and_rejects_duplicates():
    tracker = SequenceTracker()
    first = parse(sequence=2)
    next_frame = parse(sequence=5)
    assert tracker.accept(first) == 0
    assert tracker.accept(next_frame) == 2
    assert tracker.gaps[("bench-session-1", "simulator-1")] == 2
    with pytest.raises(ValueError):
        tracker.accept(next_frame)


def test_sequence_tracker_isolated_by_session_and_source():
    tracker = SequenceTracker()
    assert tracker.accept(parse(sequence=3)) == 0
    assert tracker.accept(parse(session_id="bench-session-2", sequence=0)) == 0
    assert tracker.accept(parse(source_id="simulator-2", sequence=0)) == 0


def test_sequence_tracker_explicit_session_reset():
    tracker = SequenceTracker()
    tracker.accept(parse(sequence=4))
    tracker.reset_session("bench-session-1")
    assert tracker.accept(parse(sequence=0)) == 0


def test_message_size_and_utf8_are_checked():
    with pytest.raises(ValueError):
        parse_envelope(b"\xff")
    with pytest.raises(ValueError):
        parse_envelope(" " * 2049)


def test_non_object_and_malformed_json_are_rejected():
    with pytest.raises(ValueError):
        parse_envelope("[]")
    with pytest.raises(ValueError):
        parse_envelope("{bad json")
