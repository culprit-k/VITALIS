# VITALIS hardware and transport specification — engineering baseline v0.1

**Status:** design baseline for review; not a frozen PCB/BOM or medical-device specification  
**Scope:** synthetic and non-human bench testing only  
**Parent:** VITALIS 2.0 execution plan and draft PR #59

## 1. Architecture decision

Adopt a **two-tier modular architecture** for the first integrated bench demonstrator:

- **ESP32-S3 development board:** acquisition-side controller, local sequence counter, monotonic clock capture, bounded buffer and transport.
- **Raspberry Pi 5, 4GB target:** gateway host, protocol validation, UTC alignment, local research services, VITALIS Python engine and dashboard.
- **Sensor/signal layer:** begin with deterministic simulator or electrical dummy fixture; later add one documented module at a time after interface review.
- **Transport:** USB CDC serial for the first demonstrator. BLE/Wi-Fi are later options, not simultaneous first-phase requirements.
- **Storage:** local-only append-only NDJSON bench logs with rotation and explicit retention; no cloud upload by default.

This is a design selection, not procurement approval. The Raspberry Pi is not required for the ESP32 to acquire samples; it provides a convenient host for the existing Python stack. The ESP32-S3 includes dual-core processing, Wi-Fi, BLE and SPI/I²C/UART/USB peripherals. The Raspberry Pi 5 provides a quad-core Cortex-A76 CPU, USB, Ethernet, Wi-Fi, BLE and GPIO. Verify board/module revisions and power requirements against the exact vendor documents before ordering.

## 2. First demonstrator scope

The first working prototype must demonstrate the full software/data path with **synthetic signals only**:

1. Deterministic simulator emits timestamped values and controlled faults.
2. ESP32-S3 or host-side serial simulator transmits one framed JSON message per line.
3. Raspberry Pi gateway validates framing, schema version, session token, source, sequence, timestamp, quality, unit and value.
4. Gateway maps only supported scalar channels to the current `Observation` interface.
5. Existing `TimestampedTwinStream` performs its current validation and freshness checks.
6. Adaptive twin output and data-quality diagnostics are logged locally and rendered by the existing dashboard or a small diagnostic viewer.
7. A run manifest records code revision, schema version, simulator seed, scenario, start/end time and test results; it must not contain participant identifiers.

No ECG waveform should be represented as a scalar `ecg_sample` through the current adaptive twin without a separately specified sampling/buffering interface. The first schema includes this channel only as a transport placeholder; waveform handling is explicitly out of scope for the scalar prototype.

## 3. Transport framing

- Encoding: UTF-8 JSON Lines (one JSON object followed by LF).
- Maximum message size: 2,048 bytes for the initial scalar envelope; reject oversize frames.
- One envelope per line; reject malformed JSON and unknown schema versions.
- Require a monotonically increasing per-source sequence number within a session; detect gaps, duplicates and resets.
- Require RFC 3339 timestamp with explicit offset. Store original timestamp and normalized UTC timestamp in gateway diagnostics.
- Use monotonic device time for elapsed intervals where available; wall-clock timestamps alone do not prove clock synchronisation.
- USB CDC serial first; no BLE pairing or Wi-Fi provisioning required for v0.1.
- Buffer bounds and overflow policy must be explicit. On overflow, count dropped frames and preserve sequence gaps; never silently fabricate samples.
- A reconnect starts a new transport connection but must not silently create a new session. Session reset is an explicit operator/test action.

## 4. Canonical envelope

The machine-readable draft is `schemas/observation-v1.schema.json`.

Required fields:
- `schema_version`: exact version.
- `session_id`: ephemeral non-person token, generated for each bench run.
- `source_id`: opaque source identity within the session.
- `sequence`: non-negative integer.
- `channel`: allow-listed channel.
- `timestamp`: timezone-aware RFC 3339 timestamp.
- `quality`: good, suspect, bad or missing.
- `value`: finite number or null.
- `unit`: explicit unit string.

Optional metadata:
- `missing_reason`, `sample_rate_hz`, `calibration_revision`.

Rules:
- `good` requires a finite numeric value.
- `bad` or `missing` requires null value and an explicit reason.
- `suspect` is retained for diagnostics but must not be passed to the current stream as quality='good'.
- A unit is validated against a channel-specific allow-list, not accepted merely because it is a string.
- Do not add patient IDs, names, MRNs, dates of birth, free-text clinical notes or location fields.
- The current Python `Observation` model does not yet carry all envelope fields. The gateway adapter must preserve session/sequence/quality diagnostics and map only validated data; do not silently discard metadata needed for audit.

## 5. Initial channel policy

| Channel | Unit | First demonstrator status | Notes |
|---|---|---|---|
| heart_rate | bpm | Synthetic scalar | Not a clinical heart-rate measurement |
| spo2 | % | Synthetic scalar | No oximeter accuracy claim |
| respiratory_rate | breaths/min | Synthetic scalar | Method not yet defined for physical sensor |
| temperature | degC | Synthetic scalar | Skin and core temperature must remain distinct |
| systolic_bp | mmHg | Synthetic scalar | Intermittent cuff value; not continuous |
| diastolic_bp | mmHg | Synthetic scalar | Intermittent cuff value; not continuous |
| hrv | ms | Deferred | Specify metric and beat-interval window first |
| accelerometer_x/y/z | m/s^2 | Deferred | Establish coordinate frame and calibration |
| ecg_sample | mV | Deferred | Requires waveform schema, sample rate, lead and isolation design |

## 6. Component candidates and selection gates

### Main computer — Raspberry Pi 5, 4GB
Candidate for gateway and dashboard host. Verify official product brief, cooling, 5V/5A USB-C power requirement, storage, case and regional supply. 4GB is a pragmatic software-development target; benchmark memory before claiming it is sufficient for all future models.

### Acquisition MCU — ESP32-S3 development board
Candidate for USB serial acquisition controller. Choose a board with documented USB interface, exposed pins, stable power and accessible firmware flashing. Do not assume all ESP32-S3 boards expose identical native USB or peripheral pin routing.

### Optical acquisition — MAX86141 evaluation platform
Candidate for later PPG bench work because it exposes a dedicated optical AFE and has official documentation/evaluation resources. It is a component/evaluation ecosystem, not a turnkey SpO2 instrument. Verify raw access, optical/mechanical design, LED/photodiode configuration, algorithm licensing, reference method and calibration before selection.

### ECG acquisition
Do not choose a generic ECG breakout solely because it is inexpensive. Compare documented ECG AFEs/evaluation boards for input protection, isolation, lead configuration, sample rate, resolution, reference design, raw waveform access and intended use. All early tests must use a signal simulator or dummy fixture. No human connection.

### Temperature and motion
Choose modules only after defining the measurand and output contract. Temperature location (skin vs ambient vs core proxy) must be explicit. Motion needs axes, units, coordinate frame, sample rate and calibration.

## 7. Power, safety and mechanical requirements

- Separate power domains for host, MCU and any sensor evaluation board according to vendor guidance.
- Use certified external power supplies; no custom mains circuitry.
- Do not charge Li-ion/LiPo cells on an improvised circuit. Use a protected, manufacturer-supported charger/power module and qualified review.
- No patient-connected electrodes or powered circuits. No human testing.
- Do not design a wearable enclosure until the bench architecture, thermal behaviour, ingress protection, skin-contact materials, cleaning and battery safety requirements have been reviewed.
- Electrical isolation, EMC, cybersecurity, usability and regulatory analysis are mandatory future gates before any human-connected design.

## 8. Bench verification plan

| ID | Scenario | Instrumentation | Report |
|---|---|---|---|
| B01 | Nominal 1-channel replay | Known simulator sequence | Accepted frames, sequence integrity, latency |
| B02 | Multi-channel replay | Deterministic seed | Per-channel values, alignment and coverage |
| B03 | Duplicate/out-of-order | Inject repeated and reversed sequence | Rejection counts and no state corruption |
| B04 | Packet loss | Drop known sequence numbers | Gap detection and recovery |
| B05 | Malformed/oversize JSON | Inject invalid frames | Rejection reason, gateway remains alive |
| B06 | Unknown schema/unit/channel | Mutate one field per case | Fail-closed behaviour |
| B07 | Stale/future timestamps | Controlled clock offset | Stale/future handling and audit |
| B08 | Disconnect/reconnect | Unplug USB during replay | Recovery, buffer policy, session continuity |
| B09 | Buffer overflow | Replay above configured capacity | Counted loss; no silent substitution |
| B10 | Session reset | Start a new session token | No baseline/state carryover |
| B11 | Long-duration soak | Fixed replay scenario | Memory, CPU, temperature, dropped frames |
| B12 | Privacy/log inspection | Inspect generated files | No personal identifiers or row-level patient data |

Predeclare numeric acceptance limits for latency, throughput, loss and recovery after exact board/firmware selection. Do not choose limits retrospectively to fit results.

## 9. Implementation milestones

- **H0:** validate schema and simulator messages on the development computer.
- **H1:** ESP32-S3 USB serial transport with deterministic replay.
- **H2:** Raspberry Pi gateway validates frames and maps scalar observations.
- **H3:** integration with `TimestampedTwinStream` using synthetic signals.
- **H4:** fault-injection tests and reproducible bench report.
- **H5:** component-specific sensor evaluation, one channel at a time, on non-human fixtures.

## 10. References

- Raspberry Pi 5 official product brief: https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-10-raspberry-pi-5-product-brief.pdf
- ESP32-S3 official datasheet: https://documentation.espressif.com/esp32-s3_datasheet_en.pdf
- ESP32-S3 technical documentation: https://www.espressif.com/en/support/documents/technical-documents/esp32-wroom
- Analog Devices MAX86141 product and documentation: https://www.analog.com/en/products/max86141.html

## 11. Open decisions

- Exact ESP32-S3 development board model and USB implementation.
- Whether Raspberry Pi 5 is needed for H0/H1 (it is not; laptop/desktop can validate the gateway first).
- Serial baud rate and frame-rate requirement based on declared synthetic workload.
- Exact ECG AFE/evaluation platform and isolation strategy.
- Optical evaluation platform and access to raw PPG.
- Storage endurance and log retention policy.
- Numeric bench acceptance limits.

**Safety boundary:** research and education only. The system must not be connected to a person, used to diagnose/triage/monitor/treat a patient, or represented as a medical device.
