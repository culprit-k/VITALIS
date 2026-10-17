# Synthetic software bench result — 18 October 2026

**Status:** software-only synthetic replay pass. This is not a physical hardware test, hardware-in-loop test, medical-device safety assessment, or clinical validation.

## Provenance

- Repository source commit: `f13bb5edd448d8ba160538257523187b335cc3dc`.
- Standard CI workflow: [run #39063755743](https://github.com/culprit-k/VITALIS/actions/runs/39063755743), passed on the exact commit.
- Aggregate/source-audit artifact: [artifact #12112626083](https://github.com/culprit-k/VITALIS/actions/runs/39063755743/artifacts/12112626083).
- ZIP SHA-256, matching GitHub's artifact digest: `2fc4b8ae79cba41d1dc2a2e0839b057d6a8392e17386c83cf61e0653b8b5a0df`.
- Artifact contains the source manifest, history audit, and synthetic replay report. No patient data or per-frame scores are retained.

## Test configuration

- Python 3.11.17 on GitHub-hosted Linux x86_64.
- 1,000 deterministic synthetic frames, two channels per frame.
- Five-second freshness limit.
- No patient data; no real sensor, physical gateway, or hardware was connected.
- Scope: `synthetic_software_replay_only`.

## Results

| Measure | Observed result | Status |
|---|---:|---|
| Frames replayed | 1,000 | Complete |
| Functional checks | 10/10 passed | Pass |
| Median latency | 0.2092 ms | Reported |
| p95 latency | 0.4916 ms | Within provisional target |
| Maximum latency | 0.951 ms | Reported |
| Throughput | 3,787.91 frames/s | Within provisional target |
| Python-traced peak memory | 205,968 bytes | Reported |
| Provisional p95 target | <= 100 ms/frame | Met |
| Provisional throughput target | >= 10 frames/s | Met |

The 10 functional checks confirmed deterministic replay, valid-data completion, rejection of bad units and non-finite values, rejection of out-of-order data, rejection of poor-quality data, stale-data suppression, recovery after dropout, source-replacement accounting, and session-state reset.

## Interpretation

These numbers characterize this particular software run on a GitHub-hosted runner. They are not performance promises for a Raspberry Pi, embedded gateway, selected sensor, local laptop, or any future hardware. The latency target is a provisional engineering target only. It is not a clinical limit, a safety limit, or evidence of real-time clinical suitability.

The adaptive twin emits a unitless research deviation heuristic, not a sepsis probability, diagnosis, triage category, or treatment recommendation.

## Remaining Gate 3 evidence

The physical bench gate remains open. Before energizing a physical setup, the exact hardware, wiring, power, isolation, enclosure, thermal and stop/shutdown procedures must be reviewed by a qualified engineer. Physical testing must use synthetic/replay data and electrically appropriate dummy loads only. Required next measurements include end-to-end latency on the intended gateway, sustained operation, dropout/reconnect/restart behavior, invalid-frame handling, source replacement, resource use, and documented safe shutdown.

Do not connect VITALIS to a person, clinical sensor attached to a person, patient-monitor feed, hospital network, or care workflow.
