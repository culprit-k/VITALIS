# VITALIS bench prototype — requirements and verification matrix

**Status:** requirements draft for engineering review; not a frozen BOM or safety approval  
**Scope:** non-human bench prototype using synthetic signals, signal simulators or electrical dummy fixtures only.

## 1. Prototype objective

Demonstrate reliable acquisition, timestamping, validation and transport of physiological-like test signals into the existing VITALIS canonical observation interface. The first prototype is a gateway and software integration bench, not a wearable medical device.

## 2. Functional architecture

Signal simulator / approved bench source → acquisition interface → timestamped gateway → canonical observation adapter → VITALIS stream validator → adaptive-twin research output → local dashboard and aggregate test log.

Use one channel first, then add channels incrementally. Do not purchase a complete sensor set until exact interfaces and requirements have been reviewed.

## 3. Channel requirements to resolve before component selection

| Channel | Unit expected by current stream contract | Required evidence from candidate source | Key unresolved questions |
|---|---|---|---|
| Heart rate | bpm | Numeric value, timestamp, quality indicator, update rate | Is it derived or directly measured? What is its averaging window? |
| ECG | waveform schema not yet established in core contract | Raw waveform access, sample rate, lead configuration, isolation and calibration | Is waveform support actually implemented or only derived HR/HRV? |
| HRV | ms | Definition (e.g. RMSSD/SDNN), window, units and quality | Which metric and window are scientifically justified? |
| SpO₂ | % | Numeric saturation, pulse rate, signal-quality/perfusion flags, update rate | Does the device expose quality and raw PPG or only a smoothed estimate? |
| Respiratory rate | breaths/min | Method, timestamp, quality, update rate | Is it directly measured or inferred? |
| Temperature | degC | Sensor location, calibration, resolution, update rate | Skin vs core temperature must not be conflated. |
| Blood pressure | mmHg | SBP/DBP/MAP, measurement timestamp, device export | Cuff measurements are intermittent, not continuous. |
| Movement | device-specific units/schema | Accelerometer axes, sample rate, orientation and calibration | Define canonical units and activity features separately. |

The current stream contract has declared units for selected channels. It does not establish that physical sensor drivers, ECG waveform ingestion, clinical plausibility limits, or device-specific quality mapping exist.

## 4. Gateway and data contract requirements

- Every observation must have channel, timezone-aware timestamp, finite value or explicit missing value, exact unit, quality and source.
- Normalize timestamps to UTC and reject non-increasing per-channel timestamps.
- Preserve device sequence numbers and explicit missing reasons in the adapter layer until the core schema is deliberately extended.
- Reject unknown channels, unit mismatches, non-finite values and invalid quality states.
- Mark stale data as stale/missing; never replace missing data with normal values.
- Maintain explicit session reset/isolation. No state may leak between test sessions.
- Use local-first transport and storage. Do not send names, medical record numbers or identifiers into logs.
- Record software, firmware, adapter and schema versions with each bench run.

## 5. Verification matrix

| Test | Method | Measurements | Pass condition to predeclare |
|---|---|---|---|
| Timestamp integrity | Replay known monotonic sequence, then inject duplicates/out-of-order values | Accepted/rejected counts and ordering | All invalid ordering rejected; accepted timestamps preserved |
| Unit/schema validation | Inject correct and incorrect units/channels | Rejection reason and counts | Every invalid unit/channel fails closed |
| Missingness/staleness | Drop samples and advance replay clock | Stale detection delay and missing-state output | Missing/stale state visible; no fabricated normal value |
| Packet loss | Inject controlled loss at several rates | Loss detection and recovery | Measured recovery meets agreed bench requirement |
| Reconnect | Disconnect/reconnect simulator/interface | Recovery time, duplicate samples, state reset | No duplicate acceptance or cross-session contamination |
| Clock drift | Inject known clock offsets/drift | Timestamp error and synchronisation correction | Error remains within a predeclared engineering tolerance |
| End-to-end latency | Timestamp at source and at accepted output | Median, p95, maximum latency | Meets a declared non-clinical prototype target |
| Throughput | Sustained replay at declared rate | Frames/s, dropped frames, CPU/memory | No unreported loss at target bench load |
| Resource/thermal | Sustained bench run | Power, temperature, memory, CPU | Within component manufacturer limits |
| Restart/state | Restart gateway during replay | Recovery and baseline warm-up state | Fail-safe restart; no unintended persisted state |
| Privacy/logging | Inspect logs and output files | Fields and retention | No direct identifiers or row-level clinical data in public artifacts |

Numeric tolerances must be chosen before testing based on selected hardware, interface specifications and engineering review. Do not invent acceptance values after observing results.

## 6. Component selection scorecard

For each candidate, capture:
- Manufacturer, exact model and revision.
- Datasheet and interface documentation URL.
- Output fields, units, sampling/update rate and timestamps.
- Signal-quality flags and missing-data semantics.
- BLE/USB/UART/I²C/SPI or other interface and supported libraries.
- Power, thermal and enclosure constraints.
- Calibration/reference requirements and limitations.
- Data-export/API restrictions, firmware dependencies and licensing.
- Cost and availability with date checked.
- Electrical isolation and safety review required.
- Proposed bench test and acceptance criteria.

No part is selected in this document. A candidate must not be described as medically accurate solely because it is marketed for health or wellness.

## 7. Bench-only safety boundary

- Use signal simulators, dummy loads or other non-human test fixtures.
- Do not connect DIY ECG front ends, electrodes, powered circuits or prototypes to a person.
- Any future human-connected design requires qualified biomedical/electrical safety assessment, institutional governance, ethics review, security and regulatory assessment before testing.
- Consumer wearables are not automatically suitable reference instruments.
- A successful bench test does not establish clinical accuracy or patient safety.

## 8. Immediate engineering decisions

1. Confirm which existing VITALIS channels and units are implemented in the stream contract.
2. Decide whether the first demonstration is a pure software simulator, USB serial gateway, or BLE gateway; prefer the simplest documented interface.
3. Freeze the synthetic/replay message format and acceptance tests.
4. Compare actual candidate components only after the above requirements are reviewed.
5. Keep the hardware challenge open for external biomedical and embedded-systems critique.

**Current status:** no physical VITALIS wearable, custom PCB, or validated sensor acquisition system is claimed to exist.
