from datetime import datetime, timezone
import json
from io import StringIO

import pytest

from scripts.receive_esp32_stream import parse_message, run_lines

START = datetime(2026, 10, 18, 12, tzinfo=timezone.utc)


def payload(**overrides):
    data = {
        "seq": 3, "elapsed_ms": 1000, "channel": "heart_rate",
        "value": 72.5, "unit": "bpm", "quality": "good",
        "source": "esp32-synthetic-v1",
    }
    data.update(overrides)
    return json.dumps(data)


def test_valid_message_maps_elapsed_time_to_utc_session_time():
    seq, observation = parse_message(payload(), START)
    assert seq == 3
    assert observation.channel == "heart_rate"
    assert observation.timestamp == START.replace(second=1)
    assert observation.value == 72.5
    assert observation.unit == "bpm"


def test_ready_banner_is_not_a_sample():
    assert parse_message(json.dumps({
        "type": "vitalis_gateway_ready", "mode": "synthetic_only", "schema": 1
    }), START) is None


@pytest.mark.parametrize("line", [
    "not json",
    json.dumps([]),
    payload(extra="not-allowed"),
    payload(seq=True),
    payload(elapsed_ms=-1),
    payload(channel="temperature"),
    payload(unit="%"),
    payload(quality="suspect"),
    payload(source="unknown-device"),
    payload(value=float("nan")),
    payload(value=True),
])
def test_malformed_or_unsafe_messages_fail_closed(line):
    with pytest.raises(ValueError):
        parse_message(line, START)


def test_naive_session_start_rejected():
    with pytest.raises(ValueError):
        parse_message(payload(), datetime(2026, 10, 18, 12))


def test_stdin_replay_reports_aggregate_summary_only():
    rows = "\n".join([
        json.dumps({"type": "vitalis_gateway_ready", "mode": "synthetic_only", "schema": 1}),
        payload(seq=0, elapsed_ms=0),
        payload(seq=0, elapsed_ms=0, channel="spo2", value=98.0, unit="%"),
        payload(seq=1, elapsed_ms=1000),
        payload(seq=1, elapsed_ms=1000, channel="spo2", value=97.8, unit="%"),
    ]) + "\n"
    output = StringIO()
    assert run_lines(StringIO(rows), output=output) == 0
    lines = [json.loads(line) for line in output.getvalue().splitlines()]
    assert lines[-1]["type"] == "gateway_session_summary"
    assert lines[-1]["accepted_messages"] == 4
    assert lines[-1]["raw_data_persisted"] is False
    assert all("value" not in item for item in lines)



def test_duplicate_channel_sequence_is_rejected_even_with_a_new_timestamp():
    rows = "\\n".join([
        payload(seq=0, elapsed_ms=0),
        payload(seq=0, elapsed_ms=0, channel="spo2", value=98.0, unit="%"),
        # Same sequence/channel with a changed timestamp must not be treated as new data.
        payload(seq=0, elapsed_ms=500, value=73.0),
    ]) + "\\n"
    output = StringIO()
    assert run_lines(StringIO(rows), output=output) == 2
    lines = [json.loads(line) for line in output.getvalue().splitlines()]
    assert lines[-1]["type"] == "gateway_session_summary"
    assert lines[-1]["accepted_messages"] == 2
    assert lines[-1]["rejected_messages"] == 1
    assert any(
        item.get("type") == "gateway_rejection"
        and item.get("reason") == "duplicate or regressed channel sequence"
        for item in lines
    )
    assert all("value" not in item for item in lines)


def test_global_sequence_regression_is_rejected():
    rows = "\\n".join([
        payload(seq=0, elapsed_ms=0),
        payload(seq=0, elapsed_ms=0, channel="spo2", value=98.0, unit="%"),
        payload(seq=2, elapsed_ms=2000),
        payload(seq=1, elapsed_ms=1000, channel="spo2", value=97.8, unit="%"),
    ]) + "\\n"
    output = StringIO()
    assert run_lines(StringIO(rows), output=output) == 2
    lines = [json.loads(line) for line in output.getvalue().splitlines()]
    assert lines[-1]["accepted_messages"] == 3
    assert lines[-1]["rejected_messages"] == 1
    assert any(
        item.get("type") == "gateway_rejection"
        and item.get("reason") == "sequence number regressed"
        for item in lines
    )
