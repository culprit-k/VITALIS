"""Mobile-friendly synthetic VITALIS digital-twin dashboard.

All observations, labs, events and medication rows in this demo are generated.
This is a software demonstration, not a clinical predictor or medical device.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

CHANNELS = {
    "heart_rate": ("Heart rate", "bpm", "cardiovascular"),
    "spo2": ("SpO₂", "%", "oxygenation"),
    "respiratory_rate": ("Respiratory rate", "breaths/min", "respiratory"),
    "systolic_bp": ("Systolic BP", "mmHg", "cardiovascular"),
    "temperature": ("Temperature", "°C", "temperature"),
}
SCENARIOS = {
    "Stable baseline": "stable",
    "Gradual multisystem drift": "gradual",
    "Abrupt synthetic shift": "abrupt",
    "Missing / noisy measurements": "missing",
}
st.set_page_config(page_title="VITALIS | Digital Twin Sandbox", page_icon="🧬", layout="wide")

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(ellipse at top left, #0b2740 0%, #061523 42%, #030b14 100%); }
.block-container { max-width: 1600px; padding-top: 1.1rem; padding-bottom: 3rem; }
[data-testid="stMetric"] { background: linear-gradient(145deg,rgba(13,43,67,.96),rgba(5,22,37,.96)); border:1px solid #16415f; border-radius:14px; padding:14px 16px; }
[data-testid="stMetricLabel"] { color:#b8d2e6; }
[data-testid="stMetricValue"] { color:#f3f8ff; }
div[data-testid="stTabs"] button { color:#c5e3f8; }
div[data-testid="stAlert"] { border-radius:12px; }
.vitalis-eyebrow { color:#45d8ff; font-size:.8rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
.vitalis-title { font-size:clamp(2rem,4vw,3.4rem); font-weight:850; letter-spacing:-.045em; line-height:1.05; color:#f5fbff; margin:.15rem 0; }
.vitalis-subtitle { color:#a8c4da; font-size:1rem; margin-bottom:.75rem; }
.panel { background:linear-gradient(145deg,rgba(9,34,54,.95),rgba(4,19,32,.96)); border:1px solid #16415f; border-radius:16px; padding:16px; margin-bottom:12px; }
.small-muted { color:#8fb0c8; font-size:.84rem; }
.status-pill { display:inline-block; padding:4px 10px; border:1px solid #1d8c8a; border-radius:999px; color:#6af3d0; font-size:.8rem; background:#082f36; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧬 VITALIS")
    st.caption("Adaptive Physiological Digital Twin")
    st.markdown("---")
    st.markdown("### Simulation controls")
    scenario_label = st.selectbox("Synthetic scenario", list(SCENARIOS), index=1)
    seed = st.slider("Simulation seed", 1, 9999, 2026)
    steps = st.slider("Timeline length", 12, 60, 36, step=6)
    noise = st.select_slider("Signal noise", options=["Low", "Medium", "High"], value="Medium")
    show_events = st.toggle("Show simulated event log", value=True)
    show_labs = st.toggle("Show illustrative lab panel", value=True)
    st.markdown("---")
    st.markdown("**Data source**")
    st.success("Generated synthetic measurements")
    st.caption("No patient data, connected sensors, or live clinical feeds are used.")

st.markdown('<div class="vitalis-eyebrow">Research prototype · mobile-ready sandbox</div>', unsafe_allow_html=True)
st.markdown('<div class="vitalis-title">VITALIS <span style="color:#45d8ff">/</span> Digital Twin</div>', unsafe_allow_html=True)
st.markdown('<div class="vitalis-subtitle">Explore changing personal baselines, signal quality, multisystem deviation and trajectory smoothing.</div>', unsafe_allow_html=True)
st.warning("SYNTHETIC DEMO ONLY — not a clinical predictor, probability of sepsis, medical device, alarm system, or patient-care recommendation.")

rng = random.Random(seed)
noise_scale = {"Low": 0.55, "Medium": 1.0, "High": 1.65}[noise]
scenario = SCENARIOS[scenario_label]
twin = AdaptivePhysiologicalTwin(config=TwinConfig(min_history=5, history_window=24, min_channels=2, min_systems=2))
stream = TimestampedTwinStream(twin, max_age_seconds=120)
start = datetime(2026, 10, 18, tzinfo=timezone.utc)
rows: list[dict] = []
events: list[dict] = []
for step in range(steps):
    gradual = max(0, step - int(steps * .58))
    abrupt = step >= int(steps * .68)
    drift = gradual if scenario == "gradual" else (max(0, step - int(steps * .68)) * 1.7 if scenario == "abrupt" and abrupt else 0)
    observations = {
        "heart_rate": rng.gauss(74 + (2.0 * drift if scenario == "gradual" else (12 if abrupt and scenario == "abrupt" else 0)), 2.0 * noise_scale),
        "spo2": rng.gauss(98 - (0.40 * drift if scenario == "gradual" else (3.0 if abrupt and scenario == "abrupt" else 0)), .35 * noise_scale),
        "respiratory_rate": rng.gauss(15 + (.65 * drift if scenario == "gradual" else (5.0 if abrupt and scenario == "abrupt" else 0)), 1.0 * noise_scale),
        "systolic_bp": rng.gauss(122 - (1.3 * drift if scenario == "gradual" else (13.0 if abrupt and scenario == "abrupt" else 0)), 3.0 * noise_scale),
        "temperature": rng.gauss(36.8 + (.05 * drift if scenario == "gradual" else (.8 if abrupt and scenario == "abrupt" else 0)), .08 * noise_scale),
    }
    timestamp = start + timedelta(minutes=step)
    available = dict(observations)
    if scenario == "missing":
        for channel in list(available):
            if rng.random() < .28:
                available[channel] = None
    for channel, value in available.items():
        if value is not None:
            label, unit, _ = CHANNELS[channel]
            stream.ingest(Observation(channel, timestamp, value, {"°C": "degC"}.get(unit, unit)))
    result = stream.score(timestamp)
    rows.append({
        "step": step + 1, "time": timestamp.strftime("%H:%M"),
        **observations,
        "trajectory_score": result.get("trajectory_score"),
        "trajectory_direction": result.get("trajectory_direction"),
        "state": result.get("state", "unknown"),
        "coverage": result.get("coverage", 0),
    })
    if step and rows[-1]["state"] != rows[-2]["state"]:
        events.append({"Time": timestamp.strftime("%H:%M"), "Event": "Twin state changed", "Detail": str(rows[-1]["state"]).replace("_", " ").title(), "Type": "System"})
    if scenario == "missing" and any(v is None for v in available.values()):
        events.append({"Time": timestamp.strftime("%H:%M"), "Event": "Measurement missing", "Detail": "Synthetic channel dropout", "Type": "Data quality"})
frame = pd.DataFrame(rows).set_index("step")
latest = frame.iloc[-1]
prev_state = str(latest["state"]).replace("_", " ").title()
score = latest["trajectory_score"]
score_text = "Not established" if pd.isna(score) else f"{float(score):.3f}"
direction = str(latest["trajectory_direction"] or "not established").replace("_", " ").title()
coverage = float(latest["coverage"] or 0)
score_delta = None
valid_scores = frame["trajectory_score"].dropna()
if len(valid_scores) > 1:
    score_delta = float(valid_scores.iloc[-1] - valid_scores.iloc[-2])

# Summary metrics
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Heart rate", f'{latest["heart_rate"]:.0f} bpm', help="Generated synthetic value")
m2.metric("SpO₂", f'{latest["spo2"]:.1f}%', help="Generated synthetic value")
m3.metric("Respiratory rate", f'{latest["respiratory_rate"]:.1f}/min', help="Generated synthetic value")
m4.metric("Systolic BP", f'{latest["systolic_bp"]:.0f} mmHg', help="Generated synthetic value")
m5.metric("Temperature", f'{latest["temperature"]:.1f} °C', help="Generated synthetic value")

overview, twin_tab, signals_tab, data_tab = st.tabs(["▦ Overview", "◎ Digital twin", "〰 Signals & trends", "▤ Data & events"])
with overview:
    left, right = st.columns([1.65, 1], gap="medium")
    with left:
        st.markdown('<div class="panel"><h3>Physiological signal timeline</h3><div class="small-muted">Separate charts preserve each signal\'s own units. All traces are synthetic.</div></div>', unsafe_allow_html=True)
        a, b = st.columns(2)
        with a:
            st.caption("Heart rate · bpm")
            st.line_chart(frame[["heart_rate"]], height=180, color=["#ff5268"])
            st.caption("SpO₂ · %")
            st.line_chart(frame[["spo2"]], height=180, color=["#29c8ff"])
            st.caption("Respiratory rate · breaths/min")
            st.line_chart(frame[["respiratory_rate"]], height=180, color=["#ffc34e"])
        with b:
            st.caption("Systolic BP · mmHg")
            st.line_chart(frame[["systolic_bp"]], height=180, color=["#c78cff"])
            st.caption("Temperature · °C")
            st.line_chart(frame[["temperature"]], height=180, color=["#49e4a6"])
            st.caption("Within-person deviation heuristic · unitless")
            st.line_chart(frame[["trajectory_score"]], height=180, color=["#46d8ff"])
    with right:
        st.markdown('<div class="panel"><h3>Digital twin status</h3><span class="status-pill">SYNTHETIC MODE</span></div>', unsafe_allow_html=True)
        st.metric("Latest twin state", prev_state)
        st.metric("Trajectory heuristic", score_text, delta=None if score_delta is None else f"{score_delta:+.3f} vs prior step", help="Unitless algorithmic heuristic; not a clinical probability.")
        st.metric("Trajectory direction", direction)
        st.metric("Measurement coverage", f"{coverage:.0%}")
        st.markdown('<div class="panel"><h4>Systems being represented</h4><p>❤️ Cardiovascular</p><p>🫁 Respiratory / oxygenation</p><p>🌡️ Temperature</p><p>🧠 Cross-system trajectory integration</p><div class="small-muted">System labels explain software channels; they are not organ diagnoses.</div></div>', unsafe_allow_html=True)
        st.markdown("#### Simulation summary")
        st.write(f"**Scenario:** {scenario_label}")
        st.write(f"**Generated timeline:** {steps} samples at one-minute intervals")
        st.write(f"**Noise setting:** {noise}")
with twin_tab:
    st.markdown("### Personal baseline → current deviation")
    st.info("The twin compares generated measurements against a causal within-person history. Early steps may show insufficient data while the baseline is being established.")
    chart1, chart2 = st.columns(2)
    with chart1:
        st.markdown("#### State across time")
        state_frame = frame[["trajectory_score"]].copy()
        st.line_chart(state_frame, height=280, color=["#40d7ff"])
    with chart2:
        st.markdown("#### Coverage across time")
        st.line_chart(frame[["coverage"]], height=280, color=["#48e3a4"])
    st.markdown("#### Current channel snapshot")
    snapshot = pd.DataFrame([
        {"Signal": CHANNELS[ch][0], "Latest synthetic value": f"{float(latest[ch]):.1f} {CHANNELS[ch][1]}", "System": CHANNELS[ch][2].title()}
        for ch in CHANNELS
    ])
    st.dataframe(snapshot, use_container_width=True, hide_index=True)
with signals_tab:
    st.markdown("### Signal explorer")
    selected = st.multiselect("Choose signals", list(CHANNELS), default=list(CHANNELS)[:3], format_func=lambda x: f"{CHANNELS[x][0]} ({CHANNELS[x][1]})")
    if selected:
        chart = frame[selected].copy()
        chart.columns = [CHANNELS[c][0] for c in selected]
        st.line_chart(chart, height=360)
    else:
        st.caption("Select at least one signal to draw a chart.")
    st.markdown("### Trajectory timeline")
    st.line_chart(frame[["trajectory_score"]], height=220, color=["#4edcff"])
    st.caption("Scores may be unavailable early in the sequence while the twin gathers baseline history.")
with data_tab:
    st.markdown("### Generated sample table")
    view_cols = ["time", *CHANNELS.keys(), "trajectory_score", "trajectory_direction", "state", "coverage"]
    st.dataframe(frame[view_cols], use_container_width=True, height=360)
    st.download_button("Download synthetic demo CSV", frame[view_cols].to_csv(index=True).encode("utf-8"), file_name="vitalis_synthetic_demo.csv", mime="text/csv")
    if show_events:
        st.markdown("### Synthetic event log")
        if events:
            st.dataframe(pd.DataFrame(events[-30:]), use_container_width=True, hide_index=True)
        else:
            st.caption("No state transitions or missing-data events were recorded in this run.")
    if show_labs:
        st.markdown("### Illustrative lab panel (generated examples only)")
        st.caption("These values are placeholders for interface design, not patient results or clinical reference advice.")
        labs = pd.DataFrame([
            {"Parameter": "WBC", "Synthetic value": "8.4 ×10⁹/L", "Display trend": "→"},
            {"Parameter": "CRP", "Synthetic value": "12 mg/L", "Display trend": "↑"},
            {"Parameter": "Lactate", "Synthetic value": "1.2 mmol/L", "Display trend": "→"},
            {"Parameter": "Creatinine", "Synthetic value": "0.9 mg/dL", "Display trend": "→"},
        ])
        st.dataframe(labs, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("**VITALIS research prototype** · Synthetic data only · No patient records or live sensors · Not for diagnosis, triage, treatment, or clinical decisions.")
