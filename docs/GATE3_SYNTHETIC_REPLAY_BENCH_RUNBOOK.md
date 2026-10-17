# Gate 3 synthetic/replay bench runbook

**Status:** executable software bench harness added; this is not physical hardware testing.
**Boundary:** generated observations only. Do not connect a person, clinical sensor, hospital feed, or treatment/triage workflow.

## Run

From the repository root in the project's Python environment:

```bash
pip install -e ".[dev]"
python scripts/run_synthetic_bench.py --frames 1000 --output outputs/synthetic_replay_bench.json
pytest -q tests/test_synthetic_bench.py
```

The output report contains aggregate timings, environment metadata, counts/check outcomes and limitations. The harness does not write individual observations or per-frame scores. Keep generated reports outside Git if local environment details are sensitive; never add patient data to this harness.

## Functional cases and acceptance criteria

| Case | Expected result | Gate criterion |
|---|---|---|
| Valid deterministic replay | Every generated frame is accepted and scored | Exact replay signature match across two runs in the same environment |
| Unit mismatch | Rejected and counted | No silent conversion |
| Non-finite value | Rejected and counted | No NaN/Infinity enters the twin |
| Poor-quality sample | Rejected and counted | Never silently treated as normal |
| Out-of-order/duplicate timestamp | Rejected and counted | Existing latest sample is not overwritten |
| Stale values | Coverage falls to zero after freshness limit | Stale values are not scored as fresh |
| Recovery after dropout | New fresh samples restore coverage | Recovery is observed and reported |
| Source replacement | Replacement count increments and channel history resets | Old and new source histories are not mixed |
| Session reset | State and counters clear; empty stream has zero coverage | No state leakage into the next session |
| Output privacy | Report contains aggregate measurements and test outcomes only | No raw samples, per-frame outputs, identifiers, or row-level predictions |

The executable tests are a software contract only. They do not prove that a hardware gateway implements this contract.

## Provisional performance targets

The harness reports median, p95 and maximum ingestion-to-score latency, replay throughput, and Python-traced peak memory. It also reports whether the following provisional engineering targets were met:

- p95 processing latency at or below **100 ms per frame**;
- throughput at or above **10 frames/second** for two-channel synthetic frames;
- all functional checks pass.

These are initial prototype engineering targets, **not clinical, electrical-safety, regulatory, or real-time guarantees**. Re-run on the intended bench computer with a documented power mode, OS/Python versions, background load, frame count, and test revision. A target miss is a measurement to investigate—not a reason to relax the target silently. Do not compare measurements across machines without recording the environment.

## Physical bench extension (not yet performed)

Before any physical integration, a qualified engineer should review the exact architecture and electrical design. With only an electrically appropriate dummy load and no human connection, record:

1. device/gateway model, interface, firmware and power configuration;
2. data contract/schema revision, timestamp source, clock-skew assumptions and sensor quality mapping;
3. at least 30 minutes of replay/load operation, disconnect/reconnect and process restart;
4. measured end-to-end latency distribution, throughput, memory, CPU, dropped/invalid messages, and recovery time;
5. fail-safe behavior when data stop, timestamps regress, units mismatch, source changes, or inference fails;
6. isolation, leakage, power, thermal, enclosure, EMC and cybersecurity checks by appropriately qualified reviewers, as applicable.

Do not describe software replay as hardware-in-the-loop testing. Do not connect DIY electronics or unreviewed sensors to a person. A dummy-load run does not by itself establish medical electrical safety.

## Record and sign-off

Record the source commit, run command, report hash, machine/environment, pass/fail outcomes, deviations, and reviewer. Gate 3 remains open until the physical dummy-load measurements and required engineering/safety reviews have actually been performed. No results in this runbook establish clinical performance or authorize patient-care use.
