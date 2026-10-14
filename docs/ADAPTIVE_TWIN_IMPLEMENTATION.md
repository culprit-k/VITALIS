# Adaptive physiological twin: algorithm and validation contract

**Implementation:** `src/vitalis/adaptive_twin.py`  
**Timestamped input adapter:** `src/vitalis/stream.py`  
**Demonstration:** `python scripts/demo_adaptive_twin.py`  
**Status:** streaming research component; not a clinical prediction model.

## Purpose

This component implements the first online layer of VITALIS: compare incoming measurements with a patient's own recent history, aggregate deviations across physiological systems, and track whether deviation is persistent. It is deliberately separate from the supervised sepsis classifier and its retrospective benchmark evaluation.

The output is a **unitless deviation heuristic**, not a probability, diagnosis, triage level, or time-to-event prediction. No clinical action is generated.

## Mathematics

For channel (j) and time (t), use only the previous valid observations in a bounded history (H_{j,t}):

[
m_{j,t}=\operatorname{median}(H_{j,t}),\qquad
s_{j,t}=\max(1.4826\operatorname{MAD}(H_{j,t}),\epsilon).
]

The current standardized deviation is:

[
z_{j,t}=\frac{x_{j,t}-m_{j,t}}{s_{j,t}},\qquad
q_{j,t}=\min\left(\frac{|z_{j,t}|}{z_{\max}},1\right).
]

Here, (\epsilon) is a numerical scale floor. It is **not** a clinically established sensor noise floor. It must be chosen per measurement and validated before interpreting scores.

After the first minimum-history window, the implementation freezes a robust reference center and scale, while retaining a rolling baseline. The reference-normalized deviation is

\\[
z^0_{j,t}=\\frac{x_{j,t}-m^0_j}{s^0_j}.
\\]

To avoid losing gradual shifts as the rolling baseline adapts, a two-sided cumulative-sum detector tracks positive and negative departures from this fixed reference:

\\[
C^+_{j,t}=\\max(0,C^+_{j,t-1}+z^0_{j,t}-k),\\qquad
C^-_{j,t}=\\max(0,C^-_{j,t-1}-z^0_{j,t}-k).
\\]

A cumulative shift is flagged when \\(\\max(C^+_{j,t},C^-_{j,t})\\ge h\\). The allowance \\(k\\) and threshold \\(h\\) are configurable engineering parameters and require validation; they are not clinical alarm cutoffs. The per-channel score uses the larger absolute deviation from the rolling and frozen reference baselines, clipped to \\(z_{\\max}\\). Channel-specific scale floors can be supplied to avoid using the same absolute noise floor for measurements with different units.

For each physiological system (g), average the available channel scores:

[
Q_{g,t}=\frac{1}{|J_{g,t}|}\sum_{j\in J_{g,t}}q_{j,t}.
]

When data coverage, scored-channel count, and system count pass the configured minimums, average systems with equal weight and smooth the result:

[
u_t=\frac{1}{|G_t|}\sum_{g\in G_t}Q_{g,t},\qquad
S_t=\alpha u_t+(1-\alpha)S_{t-1}.
]

Equal system weighting avoids letting a system dominate merely because more channels are mapped to it. These weights are engineering defaults, not fitted medical weights. The implementation also tracks consecutive observations whose absolute z-score exceeds a configurable deviation threshold and reports the fraction of represented systems with elevated scores.

## Causality and adaptation safeguards

1. Score the current measurement before adding it to history, so the measurement cannot move its own baseline.
2. Do not update the rolling baseline with a point whose absolute rolling z-score exceeds the configured update limit or while its CUSUM detector is triggered.
3. Bound the history length to limit memory and permit adaptation to gradual changes.
4. Ignore missing, non-numeric, and non-finite observations; reset a channel's consecutive-deviation streak on missing samples, expose coverage, and withhold an eligible score when data sufficiency checks fail.
5. Call `reset()` at patient/session boundaries. The module does not persist identity or patient data.

The fixed reference helps reveal gradual drift, but it can become stale after recovery or major treatment changes; re-baselining is explicit via session reset. These safeguards do not solve a reference already affected by illness, correlated sensors, irregular sampling, artifact detection, or full asynchronous signal synchronization. Those need explicit design and validation.

## Output contract

- `state`: one of `insufficient_data`, `within_person_range`, `deviation_detected`, `marked_deviation`, `persistent_multisystem_deviation`, `cumulative_shift_detected`, or `cumulative_multisystem_shift`.
- `trajectory_score`: unitless heuristic in the approximate range 0–1 when eligible; **not a risk probability**.
- `cross_system_concordance`: fraction of represented systems whose normalized deviation score exceeds the configured comparison threshold.
- `coverage`, per-channel baselines/z-scores, history counts, and baseline-update flags support debugging and audit.
- `clinical_recommendation` is always null.

The state cutoffs and persistence rules are configurable demonstration defaults. They have not been clinically selected and must not be used as alarm thresholds.

## What this does not yet do

- It does not estimate sepsis probability or predict a 1–3 hour deterioration window.
- It does not infer whether a high or low value is directionally dangerous for a particular channel.
- The timestamped adapter validates units, timestamps, sample quality flags, freshness, and out-of-order samples. It does not implement device-specific protocols, sophisticated multi-rate synchronization, or signal-quality/artifact detection.
- It does not integrate laboratory results, fluid balance, medication, or movement data into a unified online model.
- It does not establish novelty, patentability, prospective validity, or clinical utility.

## Validation plan before hardware integration

1. Unit-test causality, missingness, patient reset, robust scaling, baseline freeze, and deterministic output.
2. Add a timestamped observation schema with unit metadata, sensor-quality flags, and explicit sampling policies.
3. Test the stream processor on synthetic edge cases: flatline, spikes, dropout, drift, sensor replacement, and conflicting systems.
4. Evaluate offline against patient-disjoint retrospective cohorts without tuning on Set B; report false alerts per patient-hour, lead time, calibration, and subgroup/missingness diagnostics.
5. Freeze model/configuration and thresholds before any prospective shadow-mode study with appropriate clinical governance.
6. Only then specify hardware sampling rates, sensor interfaces, synchronization, compute, power, and enclosure requirements.

All work remains research-only. Do not use this module for patient care.
