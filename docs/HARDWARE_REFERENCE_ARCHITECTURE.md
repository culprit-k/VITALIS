# VITALIS non-clinical hardware reference architecture

**Status:** design proposal only; no hardware has been selected, built, energized, or safety-tested.  
**Intended use:** software/interface engineering with synthetic data and electrically appropriate dummy loads.  
**Prohibited scope:** no person connection, patient-monitor connection, hospital-network integration, treatment/triage workflow, or clinical alerting.

## 1. Design objective

Create a modular edge-gateway prototype that can ingest timestamped physiological-like observations, validate their units and quality metadata, pass them to the existing VITALIS stream adapter and adaptive-twin research component, and expose only a clearly labelled engineering visualization. The hardware prototype must not be presented as a medical device or a sepsis detector.

The current adaptive twin emits a unitless deviation heuristic. It does not emit a sepsis probability, predict a 1–3-hour deterioration window, or generate a clinical recommendation. Keep that boundary visible in UI labels, logs, and documentation.

## 2. Reference data path

```text
Synthetic replay / sensor simulator
        |
        v
Input interface + timestamp / unit metadata
        |
        v
Schema, range, freshness, quality and ordering checks
        |
        v
VITALIS stream adapter
        |
        v
Adaptive physiological deviation component
        |
        +------> Aggregate engineering dashboard
        |
        +------> Aggregate-only test report
```

The initial bench should use a software replay source or signal simulator, not a sensor attached to a person. A later hardware-in-loop test may use a simulator and dummy loads only after a qualified engineer reviews the exact wiring, isolation, power, thermal, and stop procedures.

## 3. Subsystems and selection gates

| Subsystem | Minimum design requirement | Selection status |
|---|---|---|
| Compute gateway | Runs the pinned Python runtime and VITALIS package; deterministic local processing; bounded memory | Not selected |
| Replay/simulator interface | Reproducible synthetic frames; configurable dropout, stale values, spikes, drift, and source changes | Software replay exists; physical simulator not selected |
| Input transport | Explicit schema/version, units, timestamps, sequence/order policy, source identity, and quality flags | Contract needs final engineering review |
| Power | Certified appropriate supply for the selected components; documented rating and safe shutdown | Not selected; engineer review required |
| Isolation/protection | Determined from the actual interface and electrical risk assessment | Not specified until parts and wiring are selected |
| Enclosure/thermal | Stable mounting, ventilation, strain relief, no exposed conductive hazards | Not selected |
| Local display | Labels all outputs “engineering deviation heuristic—not a clinical score”; shows coverage/staleness and data-quality status | Existing software demo only |
| Storage/logging | Aggregate test summaries by default; no raw patient data or persistent person identifiers | Aggregate-only reporting intended |
| Network | Disconnected/local-only during first bench unless a reviewed test requires otherwise | Local-only preferred |

Do not choose final parts until interface voltage/current, data rate, operating environment, supply, isolation, and budget are documented. Do not treat a consumer development board or ordinary sensor as medically safe merely because it can communicate with Python.

## 4. Software/data contract at the hardware boundary

Every incoming observation should carry:
- schema version and channel name;
- numeric value and explicit unit;
- acquisition timestamp, timezone/clock basis, and sequence number where available;
- source identifier or simulator identity;
- quality/status flag and freshness limit;
- optional simulator fault annotation for controlled test scenarios.

Reject or explicitly count unknown units, non-finite values, invalid quality flags, stale samples, duplicates, out-of-order timestamps, and impossible schema versions. Never silently convert unknown units or treat missing/stale data as normal. On a declared source replacement, reset that channel's reference/history and aggregate trajectory continuity according to the current adapter contract. Call the session reset at every new synthetic session.

The exact permitted ranges, rates, protocol, clock-skew budget, and channel-specific noise floor are **open engineering decisions**; do not infer clinical limits from demonstration defaults.

## 5. Bench build sequence

1. Freeze the repository commit and dependency lock used for the bench.
2. Run the existing synthetic replay harness and unit tests; retain its aggregate report and SHA-256.
3. Select a simulator/interface and gateway only after the data contract and electrical requirements are reviewed.
4. Produce a wiring diagram, parts list with datasheets, power/isolation review, enclosure/thermal review, and emergency shutdown procedure.
5. Have a qualified engineer independently approve the exact setup before energizing it.
6. Run the blank record in `docs/GATE3_PHYSICAL_BENCH_RECORD_TEMPLATE.md`; use synthetic data and dummy loads only.
7. Exercise startup, nominal replay, malformed frames, flatline, spikes, dropout, stale input, out-of-order frames, source replacement, reconnect, session reset, and safe shutdown.
8. Stop and document any unexpected heating, electrical behavior, data leakage, state leakage, uncontrolled output, or failure to recover.
9. Archive only aggregate test results, software/firmware versions, configuration hashes, and the reviewer-signed bench record.

A successful software benchmark is not evidence of hardware-in-loop performance, electrical safety, medical electrical compliance, or clinical validity.

## 6. Required acceptance evidence

- [ ] Approved interface/schema document with units and timestamp semantics.
- [ ] Component datasheets and reviewed bill of materials.
- [ ] Wiring diagram and power/isolation/thermal assessment.
- [ ] Qualified engineer approval before power-on.
- [ ] Reproducible simulator and dummy-load setup.
- [ ] All replay/fault-injection cases pass, with deviations documented.
- [ ] Disconnect/reconnect and source-change behavior verified.
- [ ] Safe shutdown and stop conditions demonstrated.
- [ ] Aggregate-only report and report hash retained.
- [ ] Independent engineering reviewer signs the record.

Until every applicable item is evidenced, Gate 3 remains open. Do not connect this prototype to a person, clinical monitor, hospital network, or care workflow.
