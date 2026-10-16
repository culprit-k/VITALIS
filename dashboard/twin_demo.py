"""Synthetic-only interactive Streamlit demo for the VITALIS adaptive twin."""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

UNITS = {
    "heart_rate": "bpm", "spo2": "%", "respiratory_rate": "breaths/min",
    "systolic_bp": "mmHg", "temperature": "degC",
}

st.set_page_config(page_title="VITALIS Twin Sandbox", page_icon="🧬", layout="wide")
st.title("VITALIS · Adaptive Physiological Twin Sandbox")
st.warning(
    "Synthetic demonstration only. This is not a clinical predictor, alarm system, "
    "medical device, or patient-care recommendation."
)
st.write(
    "Explore how causal personal baselines, missingness checks, multisystem deviation, "
    "and trajectory smoothing behave on generated measurements. No patient data are used."
)
seed = st.slider("Synthetic-data seed", min_value=1, max_value=9999, value=2026)
rng = random.Random(seed)
twin = AdaptivePhysiologicalTwin(
    config=TwinConfig(min_history=5, history_window=24, min_channels=2, min_systems=2)
)
stream = TimestampedTwinStream(twin, max_age_seconds=120)
start = datetime(2026, 10, 14, tzinfo=timezone.utc)
rows = []
for step in range(36):
    drift = max(0, step - 23)
    observations = {
        "heart_rate": rng.gauss(74 + 2.0 * drift, 2.0),
        "spo2": rng.gauss(98 - 0.45 * drift, 0.35),
        "respiratory_rate": rng.gauss(15 + 0.7 * drift, 1.0),
        "systolic_bp": rng.gauss(122 - 1.5 * drift, 3.0),
        "temperature": rng.gauss(36.8 + 0.06 * drift, 0.08),
    }
    timestamp = start + timedelta(minutes=step)
    for channel, value in observations.items():
        stream.ingest(Observation(channel, timestamp, value, UNITS[channel]))
    result = stream.score(timestamp)
    rows.append({
        "step": step + 1,
        **observations,
        "trajectory_score": result["trajectory_score"],
        "trajectory_direction": result["trajectory_direction"],
        "state": result["state"],
        "coverage": result["coverage"],
    })

frame = pd.DataFrame(rows).set_index("step")
latest = frame.iloc[-1]
left, middle, right = st.columns(3)
left.metric("Latest heuristic score", "Not available" if pd.isna(latest["trajectory_score"]) else f'{latest["trajectory_score"]:.3f}')
middle.metric("Latest state", str(latest["state"]).replace("_", " ").title())
right.metric("Latest trajectory", str(latest["trajectory_direction"] or "not established").title())

st.subheader("Generated physiological signals")
st.line_chart(frame[["heart_rate", "spo2", "respiratory_rate", "systolic_bp", "temperature"]])
st.caption(
    "Signals use different units and scales; this plot is for demonstration, not a clinical display."
)
st.subheader("Within-person deviation trajectory")
st.line_chart(frame[["trajectory_score"]])
st.dataframe(
    frame[["trajectory_score", "trajectory_direction", "state", "coverage"]],
    use_container_width=True,
)
st.caption(
    "The score is a unitless heuristic, not a probability. The demo intentionally does not "
    "display confidence percentages, time-to-deterioration estimates, or recommendations."
)
