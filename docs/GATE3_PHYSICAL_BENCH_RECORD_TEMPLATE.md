# Gate 3 physical bench record template

**Status:** blank template only; no physical bench run or safety approval is implied.  
**Boundary:** non-clinical engineering bench with simulated/replay data and electrically appropriate dummy loads only. Never connect this prototype to a person, patient monitor feed, hospital network, or clinical workflow.

## 0. Authorization and stop conditions

- [ ] Exact architecture and wiring reviewed by a qualified engineer before power-on.
- [ ] Intended use is limited to software/hardware interface evaluation.
- [ ] No human connection, clinical sensor attached to a person, patient data, or care-system connection.
- [ ] Power supply, isolation, enclosure, thermal behavior, and any applicable electrical/EMC requirements reviewed by qualified personnel.
- [ ] Emergency power-off and safe shutdown procedure defined.
- [ ] Operator knows stop criteria and has authority to stop the test.

**If any item is unchecked, do not energize the setup.** A software replay pass or dummy-load run does not establish medical electrical safety.

## 1. Test identity

| Field | Record |
|---|---|
| Test ID | |
| Date/time and timezone | |
| Operator | |
| Independent/qualified engineering reviewer | |
| Repository commit SHA | |
| Firmware/software versions | |
| Runbook/protocol revision | |
| Report path and SHA-256 | |
| Deviations/incident reference | |

## 2. Hardware and interface inventory

| Component | Manufacturer/model/revision | Firmware | Interface/protocol | Power source | Datasheet reviewed by |
|---|---|---|---|---|---|
| Compute gateway | | | | | |
| Sensor simulator/replay source | | | | | |
| Dummy load/interface fixture | | | | | |
| Power supply | | | | | |
| Isolation / protection equipment, if applicable | | | | | |

Record data-contract details:

- Schema/version:
- Timestamp source and timezone:
- Clock-skew assumption and measured skew:
- Expected update rate and payload size:
- Units and permitted ranges:
- Quality/freshness flags and mapping:
- Disconnect and source-replacement semantics:
- Dummy-load verification method:

## 3. Environment and setup

- OS/kernel:
- Python/runtime and dependency lock/hash:
- CPU/architecture:
- Power mode and power supply rating:
- Ambient temperature:
- Background load:
- Network state (prefer disconnected/local-only unless specifically required):
- Logging destination and retention:
- Confirmation no patient-level data or identifiers are present:

## 4. Predeclared test sequence

Record command/script version and expected result before each test. Do not change acceptance criteria after observing outcomes.

| Test | Procedure | Expected safe behavior | Result (PASS/FAIL/NOT RUN) | Evidence reference |
|---|---|---|---|---|
| Startup/self-check | Start from a clean state using replay input | Explicit readiness state; no clinical/diagnostic claim | | |
| Nominal replay | Run deterministic synthetic/replay frames | Valid messages handled per schema | | |
| Invalid units/value | Inject unit mismatch and non-finite values | Reject and count; no silent conversion | | |
| Poor quality/stale data | Inject bad-quality and stale observations | Mark unavailable; do not present stale data as fresh | | |
| Timestamp regression/duplicate | Replay out-of-order and duplicate timestamps | Reject or explicitly flag; never silently overwrite latest accepted state | | |
| Source disconnect | Disconnect replay source or interface | Explicit data unavailable state; no false normal state | | |
| Reconnect | Restore source with fresh observations | Recovery observable; stale history not misrepresented | | |
| Process restart | Restart process during replay | Defined reset/recovery; no state leakage | | |
| Sustained load | At least 30 minutes, if approved | No unsafe thermal/power behavior; report drops and resource use | | |
| Power interruption/recovery | Only if the engineer-approved fixture/procedure supports it | Safe shutdown/restart; no corrupted or misleading stale state | | |
| Privacy review | Inspect retained outputs | Aggregate diagnostics only; no raw patient data or row-level output | | |

## 5. Measurements

Record sample count and measurement method for every metric.

- Total input frames:
- Accepted / rejected / dropped frames:
- Disconnect count and total outage duration:
- Recovery time per disconnect:
- End-to-end latency: median / p95 / maximum:
- Throughput (frames/second):
- Peak memory and CPU:
- Temperature and power observations:
- Clock skew / timestamp anomalies:
- Error/restart counts:
- Any unexplained output transitions:

The provisional software targets in the synthetic runbook (p95 ≤100 ms and ≥10 frames/s) are engineering targets only. A miss must be investigated and documented, not silently waived. Do not infer clinical timing performance from replay measurements.

## 6. Stop criteria

Stop, power down safely, and mark the test **FAIL / INVESTIGATION REQUIRED** if any of the following occurs:

- unexpected heating, odor, electrical noise, damaged wiring, power instability, or protective-device activation;
- unreviewed exposed conductors, uncertain isolation, or uncertain power path;
- stale or invalid input represented as fresh/normal without an explicit unavailable state;
- source replacement mixes histories or process restart leaks state;
- data are written to an unintended destination or privacy boundary is violated;
- test setup differs materially from the approved diagram/protocol;
- operator or reviewer is uncertain that the setup is safe.

Do not resume until the qualified reviewer documents the corrective action and authorizes a new run.

## 7. Results and disposition

- Overall outcome: **PASS / FAIL / INCOMPLETE / NOT AUTHORIZED**
- Deviations and rationale:
- Defects filed (issue links):
- Corrective actions and retest reference:
- Evidence/report hash:
- Qualified engineering reviewer findings:
- Required electrical/EMC/cybersecurity/safety assessments still outstanding:
- Approved scope of any conclusion:

## 8. Sign-off

**Operator:** ____________________  **Date:** __________

**Qualified engineering reviewer:** ____________________  **Date:** __________

**Scope limitation acknowledged:** This is bench evidence for the exact recorded setup only. It does not establish clinical validity, medical electrical safety, regulatory compliance, or authorization for use on people. Gate 3 remains open until the required physical measurements and applicable independent safety reviews are complete.
