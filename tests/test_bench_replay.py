import json

from scripts.generate_bench_stream import envelopes
from scripts.run_bench_replay import replay_lines


def jsonl(scenario="nominal", frames=24, seed=2026):
    return [json.dumps(item, separators=(",", ":")) for item in envelopes(frames, seed, scenario)]


def test_nominal_replay_is_deterministic_and_aggregate_only():
    first = replay_lines(jsonl())
    second = replay_lines(jsonl())
    assert first == second
    assert first["mode"] == "synthetic_aggregate_only"
    assert first["lines_seen"] == 96
    assert first["stream_accepted"] == 96
    assert first["scored_frames"] == 24
    assert first["eligible_frames"] > 0
    assert "trajectory_state_counts" in first
    assert "channels" not in first
    assert "value" not in first
    assert "patient_id" not in first


def test_dropout_is_counted_and_does_not_enter_stream():
    summary = replay_lines(jsonl("dropout", frames=20))
    assert summary["explicit_missing"] == 6
    assert summary["non_good_quality"] == 6
    assert summary["stream_accepted"] == 74
    assert summary["scored_frames"] == 20


def test_packet_loss_is_counted_without_gap_filling():
    summary = replay_lines(jsonl("packet_loss", frames=16))
    assert summary["sequence_gaps"] == 8
    assert summary["scored_frames"] == 14
    assert summary["stream_accepted"] == 56


def test_malformed_and_mixed_session_lines_are_rejected():
    items = envelopes(3, 1, "nominal")
    lines = [json.dumps(item) for item in items]
    lines.insert(1, "{not-json")
    changed = dict(items[-1])
    changed["session_id"] = "second-session"
    lines.append(json.dumps(changed))
    summary = replay_lines(lines)
    assert summary["parse_rejected"] == 1
    assert summary["session_rejected"] == 1
