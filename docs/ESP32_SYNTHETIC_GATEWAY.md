# ESP32 synthetic gateway: implementation and first bench procedure

**Status:** firmware and laptop receiver are software artifacts only. No physical board has been connected or tested. Synthetic values only; no sensor, person, clinical monitor, hospital feed, Wi-Fi, or treatment/triage workflow.

## Data path

```mermaid
flowchart LR
    A[ESP32-S3 synthetic signal generator] -->|USB serial, 115200 baud, newline JSON| B[Python receiver]
    B --> C[Schema, unit, quality, sequence validation]
    C --> D[TimestampedTwinStream]
    D --> E[AdaptivePhysiologicalTwin]
    E --> F[Aggregate research-only summary]
```

The firmware emits two toy channels once per second: heart rate in `bpm` and SpO₂ in `%`. Values are deterministic bounded sinusoids, not physiological simulation suitable for validation. Each message has `seq`, `elapsed_ms`, `channel`, `value`, `unit`, `quality`, and `source`. The laptop anchors device elapsed time to a UTC session start. This is adequate for a simple bench transport demonstration, not synchronized clinical acquisition or clock-drift testing.

## Software-only checks

From the repository root:

```bash
pip install -e ".[dev]"
pytest -q tests/test_esp32_gateway.py tests/test_stream.py
python scripts/receive_esp32_stream.py --stdin < synthetic_messages.jsonl
```

The receiver reads stdin for replay or USB serial with `--port COM4` (Windows) or `--port /dev/ttyACM0` (Linux; exact name varies). Serial mode requires `pip install pyserial`. On macOS, select the corresponding `/dev/cu.*` device. Do not guess a port; inspect the OS device list.

## Firmware upload after the board arrives

1. Install Arduino IDE and the Espressif ESP32 board package.
2. Select the exact ESP32-S3 DevKitC-1 board/USB port after confirming the board revision.
3. Open `firmware/esp32_synthetic_gateway/esp32_synthetic_gateway.ino`, compile, and upload.
4. Open the serial monitor at **115200 baud** to confirm the ready banner and two JSON lines per second.
5. Close the serial monitor before starting the Python receiver; serial ports are usually exclusive.
6. In a terminal, install the project and serial extra, then run:
   ```bash
   pip install -e ".[dev]"
   pip install pyserial
   python scripts/receive_esp32_stream.py --port <YOUR_SERIAL_PORT>
   ```
7. Verify accepted messages increase, coverage is visible, and the receiver prints no repeated rejections. Stop with Ctrl+C.

## Failure cases and limits

- Malformed JSON, unknown channels, unit mismatch, non-finite values, wrong quality/source, wrong schema fields, invalid timestamps, and regressing sequence numbers are rejected.
- Core stream validation rejects per-channel duplicate/out-of-order timestamps and values older than the freshness window.
- Output is summary-only: it does not print sample values and does not write files. Terminal output is still a live operational record; do not pipe it into a public log with sensitive environment information.
- The simple session-time anchor uses host wall-clock time at receiver start. It does not establish device clock accuracy or cross-device synchronization.
- The current firmware is synthetic-only and deliberately has no sensor drivers. Do not connect sensors or people to this bench.
- The twin state is a unitless heuristic, not a probability, diagnosis, clinical alarm, or treatment recommendation. No supervised predictor is loaded by this receiver.

## What this milestone does not complete

It does not prove physical serial behavior, ESP32 board compatibility, USB stability, electrical safety, sensor validity, clinical performance, or real-time guarantees. After hardware arrives, record the exact board/firmware revision and run a minimum 30-minute dummy/synthetic stream, disconnect/reconnect, process restart, and dropped/invalid-message checks. Physical Gate 3 remains open until the test is actually performed and reviewed.
