import json

import pytest

from scripts.generate_bench_stream import envelopes
from vitalis.transport import SequenceTracker, parse_envelope, to_stream_observation


def test_generator_is_deterministic_for_fixed_seed():
    first = list(envelopes(frames=12, seed=17, scenario="nominal"))
    second = list(envelopes(frames=12, seed=17, scenario="nominal"))
    assert first == second


def test_nominal_generator_emits_valid_mappable_observations():
    tracker = SequenceTracker()
    generated = list(envelopes(frames=8, seed=2026, scenario="nominal"))
    assert len(generated) == 32

    for item in generated:
        envelope = parse_envelope(json.dumps(item))
        assert tracker.accept(envelope) == 0
        observation = to_stream_observation(envelope)
        assert observation.quality == "good"
        assert observation.timestamp.tzinfo is not None


def test_dropout_generator_marks_missing_values_explicitly():
    generated = list(envelopes(frames=10, seed=3, scenario="dropout"))
    missing = [
        parse_envelope(json.dumps(item))
        for item in generated
        if item["quality"] == "missing"
    ]
    assert len(missing) == 3
    assert all(item.value is None for item in missing)
    assert all(item.missing_reason == "not_sampled" for item in missing)
    with pytest.raises(ValueError):
        to_stream_observation(missing[0])


def test_packet_loss_generator_produces_sequence_gaps_without_filling_them():
    tracker = SequenceTracker()
    generated = list(envelopes(frames=15, seed=5, scenario="packet_loss"))
    assert len(generated) == 52

    gaps = 0
    for item in generated:
        gaps += tracker.accept(parse_envelope(json.dumps(item)))

    assert gaps == 8
    assert tracker.gaps[("synthetic-bench-session", "synthetic-simulator-1")] == 8
