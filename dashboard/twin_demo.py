"""VITALIS Research Workspace — synthetic-only adaptive physiological twin explorer.

All generated observations, laboratory examples, events, and export rows in this app are
synthetic. This is a research/engineering demonstration, not a validated clinical system.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import streamlit as st

from vitalis.adaptive_twin import AdaptivePhysiologicalTwin, TwinConfig
from vitalis.stream import Observation, TimestampedTwinStream

APP_VERSION = "0.2.0-preview"
CHANNELS = {
    "heart_rate": {"label": "Heart rate", "unit": "bpm", "system": "Cardiovascular", "color": "#ff6b83", "icon": "♥"},
    "spo2": {"label": "SpO₂", "unit": "%", "system": "Oxygenation", "color": "#54c7ec", "icon": "◉"},
    "respiratory_rate": {"label": "Respiratory rate", "unit": "breaths/min", "system": "Respiratory", "color": "#ffc66d", "icon": "≈"},
    "systolic_bp": {"label": "Systolic pressure", "unit": "mmHg", "system": "Cardiovascular", "color": "#c4a1ff", "icon": "↕"},
    "temperature": {"label": "Temperature", "unit": "°C", "system": "Temperature", "color": "#4ce0b3", "icon": "⌁"},
}
SCENARIOS = {
    "Stable baseline": "stable",
    "Gradual multisystem drift": "gradual",
    "Abrupt synthetic shift": "abrupt",
    "Missingness & noisy signals": "missing",
    "Shift followed by recovery": "recovery",
}
RESOURCE_LIBRARY = [
    {"category": "Data", "title": "PhysioNet/CinC Challenge 2019", "summary": "The original sepsis-prediction challenge dataset, documentation, scoring context, and required citation.", "url": "https://physionet.org/content/challenge-2019/1.0.0/", "kind": "Dataset · Open access", "access": "Challenge-specific terms apply"},
    {"category": "Data", "title": "MIMIC-IV v3.1", "summary": "Large critical-care electronic health record database. Credentialed access and training are required.", "url": "https://physionet.org/content/mimiciv/3.1/", "kind": "Dataset · Credentialed", "access": "Approval, training, and data-use terms required"},
    {"category": "Data", "title": "eICU Collaborative Research Database", "summary": "Multi-centre critical-care database that may support a separate external evaluation after governance and endpoint review.", "url": "https://physionet.org/content/eicu-crd/2.0/", "kind": "Dataset · Credentialed", "access": "Approval, training, and data-use terms required"},
    {"category": "Clinical context", "title": "Surviving Sepsis Campaign — Adult Guidelines", "summary": "Current guideline portal from SCCM/ESICM. Use for clinical context and expert review, not as proof that this prototype is clinically valid.", "url": "https://sccm.org/survivingsepsiscampaign/guidelines-and-resources/surviving-sepsis-campaign-adult-guidelines", "kind": "Clinical guideline", "access": "Guidance for qualified clinical teams"},
    {"category": "Methods", "title": "TRIPOD Statement", "summary": "Reporting resources for prediction-model studies; check the current AI-specific extension and companion material before manuscript submission.", "url": "https://www.tripod-statement.org/", "kind": "Reporting guidance", "access": "Public resource"},
    {"category": "Methods", "title": "PROBAST", "summary": "Risk-of-bias and applicability assessment framework for prediction-model studies; verify the applicable AI extension/version.", "url": "https://www.probast.org/", "kind": "Critical appraisal", "access": "Public resource"},
    {"category": "Safety & governance", "title": "FDA — Good Machine Learning Practice", "summary": "Lifecycle principles for development of safe, effective and high-quality ML-enabled medical technologies.", "url": "https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/good-machine-learning-practice-medical-device-development-guiding-principles", "kind": "Safety principles", "access": "Public resource; not local regulatory approval"},
    {"category": "Safety & governance", "title": "FDA — Transparency for ML-enabled Medical Devices", "summary": "Guidance on communicating intended use, development, performance, logic and human-AI workflow considerations.", "url": "https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/transparency-machine-learning-enabled-medical-devices-guiding-principles", "kind": "Transparency principles", "access": "Public resource; not local regulatory approval"},
    {"category": "Safety & governance", "title": "WHO — Ethics and Governance of AI for Health", "summary": "Ethical and human-rights considerations for AI in health research, deployment and oversight.", "url": "https://www.who.int/publications/i/item/9789240029200", "kind": "Global governance guidance", "access": "Public resource"},
    {"category": "Engineering", "title": "Streamlit Documentation", "summary": "Official reference for the interactive Python app framework used for this demo.", "url": "https://docs.streamlit.io/", "kind": "Developer documentation", "access": "Public resource"},
    {"category": "Engineering", "title": "ESP32-S3 Technical Documentation", "summary": "Official Espressif documentation for the proposed embedded gateway platform; board-specific wiring still needs confirmation.", "url": "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html", "kind": "Hardware documentation", "access": "Public resource"},
]

st.set_page_config(page_title="VITALIS | Research Workspace", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; --bg:#06111d; --panel:#0b1c2b; --panel2:#0e2435; --line:#1c3d52; --muted:#88a6b9; --text:#eef7fc; --cyan:#55d7e9; --mint:#59e2bd; }
html, body, [class*="css"] { font-family:'Manrope',sans-serif; }
.stApp { background: radial-gradient(ellipse at 12% 0%, rgba(20,89,115,.38), transparent 34%), radial-gradient(ellipse at 86% 6%, rgba(46,78,137,.20), transparent 28%), linear-gradient(165deg,#071522 0%,#050d17 70%,#081624 100%); color:var(--text); }
.block-container { max-width:1660px; padding-top:1.25rem; padding-bottom:4rem; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#071522,#091a29); border-right:1px solid #17364c; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c0d5e4; }
[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(15,42,62,.96),rgba(8,25,39,.96)); border:1px solid var(--line); border-radius:15px; padding:15px 17px; min-height:112px; box-shadow:0 8px 24px rgba(0,0,0,.12); }
[data-testid="stMetricLabel"] { color:#9cb9cc; font-weight:600; font-size:.82rem; }
[data-testid="stMetricValue"] { color:#f5fbff; font-weight:800; letter-spacing:-.04em; }
[data-testid="stMetricDelta"] { font-family:'DM Mono',monospace; }
div[data-testid="stTabs"] button { color:#b9d4e4; font-weight:650; }
.stButton>button,.stDownloadButton>button { border:1px solid #24516a; border-radius:11px; background:linear-gradient(115deg,#10314a,#0e263a); color:#ecfaff; font-weight:700; transition:all .15s ease; }
.stButton>button:hover,.stDownloadButton>button:hover { border-color:#55d7e9; color:#fff; transform:translateY(-1px); }
[data-testid="stAlert"] { border-radius:13px; border:1px solid #28475b; }
.vh-kicker { color:#55d7e9; letter-spacing:.19em; font-size:.72rem; font-weight:800; text-transform:uppercase; }
.vh-title { font-size:clamp(2.15rem,4.6vw,4.2rem); line-height:1.03; letter-spacing:-.07em; font-weight:800; color:#f6fbff; margin:.35rem 0 .65rem; }
.vh-subtitle { color:#a8c4d5; max-width:900px; font-size:1.02rem; line-height:1.65; }
.vh-section { font-size:1.35rem; letter-spacing:-.04em; font-weight:800; color:#f0f8ff; margin:.4rem 0 .3rem; }
.vh-muted { color:#8caabd; font-size:.84rem; line-height:1.6; }
.vh-panel { background:linear-gradient(145deg,rgba(13,39,58,.90),rgba(7,22,35,.94)); border:1px solid #1b3b50; border-radius:18px; padding:18px 20px; box-shadow:0 12px 28px rgba(0,0,0,.12); margin-bottom:12px; }
.vh-panel h3,.vh-panel h4 { margin:.15rem 0 .6rem; color:#eaf6ff; letter-spacing:-.025em; }
.vh-chip { display:inline-flex; align-items:center; gap:7px; font-size:.75rem; font-weight:800; letter-spacing:.04em; border:1px solid #236b70; color:#75ecd7; padding:5px 10px; border-radius:999px; background:#0a2b32; }
.vh-chip-blue { border-color:#276080; color:#75dff7; background:#0a2939; }
.vh-chip-warn { border-color:#705b31; color:#ffd58e; background:#2c2518; }
.vh-sep { border:0; border-top:1px solid #1b3a4f; margin:1.1rem 0; }
.vh-resource { border:1px solid #1b3b50; border-radius:14px; background:rgba(9,29,44,.78); padding:15px 17px; margin:.55rem 0; }
.vh-resource-title { color:#dff5ff; font-weight:800; font-size:1rem; margin-bottom:.25rem; }
.vh-small { color:#8daec1; font-size:.76rem; }
.vh-big-number { color:#f5fbff; font-size:2.2rem; font-weight:800; letter-spacing:-.06em; }
.vh-flow { display:flex; flex-wrap:wrap; gap:10px; align-items:stretch; margin:.9rem 0; }
.vh-node { background:linear-gradient(145deg,#103149,#0b2030); border:1px solid #28536b; border-radius:12px; padding:13px 15px; min-width:145px; flex:1; }
.vh-node strong { display:block; color:#ecf9ff; margin-bottom:5px; }
.vh-node span { color:#91b1c6; font-size:.78rem; line-height:1.45; }
@media (max-width:700px) { .block-container{padding-left:1rem;padding-right:1rem;} .vh-title{font-size:2.4rem;} .vh-panel{padding:14px;} }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='font-size:1.55rem;font-weight:850;letter-spacing:-.06em;color:#f3fbff'>🧬 VITALIS</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#7fa7bd;font-size:.76rem;letter-spacing:.12em;text-transform:uppercase;margin-top:-.2rem'>Adaptive physiology research</div>", unsafe_allow_html=True)
    st.markdown("<hr class='vh-sep'>", unsafe_allow_html=True)
    page = st.radio("WORKSPACE", ["Command center", "Twin studio", "Signal lab", "Events & data", "Architecture", "Hardware lab", "Research library", "Validation & governance"], label_visibility="visible")
    st.markdown("<hr class='vh-sep'>", unsafe_allow_html=True)
    st.markdown("**Simulation configuration**")
    scenario_label = st.selectbox("Scenario", list(SCENARIOS), index=1)
    seed = st.number_input("Reproducible seed", min_value=1, max_value=999999, value=2026, step=1)
    steps = st.slider("Timeline samples", 12, 96, 48, step=6)
    interval = st.select_slider("Sampling interval", options=[1, 5, 10, 15], value=1, format_func=lambda x: f"{x} min")
    noise = st.select_slider("Noise profile", options=["Low", "Medium", "High"], value="Medium")
    dropout_pct = st.slider("Measurement dropout", min_value=0, max_value=50, value=20 if scenario_label == "Missingness & noisy signals" else 0, step=5, format="%d%%")
    shift_intensity = st.slider("Synthetic shift intensity", min_value=25, max_value=150, value=100, step=25, format="%d%%")
    st.markdown("<hr class='vh-sep'>", unsafe_allow_html=True)
    st.markdown("<span class='vh-chip'>● SYNTHETIC MODE</span>", unsafe_allow_html=True)
    st.caption("No live clinical feed, patient records or sensor data are connected. All plots and exports are generated for demonstration.")
    st.caption(f"Workspace build {APP_VERSION}")

rng = random.Random(int(seed))
noise_scale = {"Low": 0.55, "Medium": 1.0, "High": 1.65}[noise]
scenario = SCENARIOS[scenario_label]
shift = shift_intensity / 100.0
twin = AdaptivePhysiologicalTwin(config=TwinConfig(min_history=5, history_window=24, min_channels=2, min_systems=2))
stream = TimestampedTwinStream(twin, max_age_seconds=max(120, interval * 60 * 3))
start = datetime(2026, 10, 18, 12, 0, tzinfo=timezone.utc)
rows: list[dict[str, Any]] = []
events: list[dict[str, str]] = []
prev_state = None
for step in range(steps):
    timestamp = start + timedelta(minutes=step * interval)
    gradual = max(0, step - int(steps * .52))
    abrupt_start = int(steps * .62)
    abrupt = step >= abrupt_start
    recovery_start = int(steps * .70)
    if scenario == "gradual":
        drift = gradual * shift
    elif scenario == "abrupt":
        drift = (max(0, step - abrupt_start) * 1.6 + 5) * shift if abrupt else 0
    elif scenario == "recovery":
        peak = max(0, step - abrupt_start) * 1.2 if abrupt else 0
        recovered = max(0, step - recovery_start) * 1.35 if step >= recovery_start else 0
        drift = max(0, peak - recovered) * shift
    else:
        drift = 0
    observations: dict[str, float | None] = {
        "heart_rate": rng.gauss(74 + (2.0 * drift if scenario == "gradual" else (9 + drift if scenario in ("abrupt", "recovery") else 0)), 2.0 * noise_scale),
        "spo2": rng.gauss(98 - (0.40 * drift if scenario == "gradual" else (2.0 + .18 * drift if scenario in ("abrupt", "recovery") else 0)), .35 * noise_scale),
        "respiratory_rate": rng.gauss(15 + (.65 * drift if scenario == "gradual" else (3.0 + .30 * drift if scenario in ("abrupt", "recovery") else 0)), 1.0 * noise_scale),
        "systolic_bp": rng.gauss(122 - (1.3 * drift if scenario == "gradual" else (8.0 + .6 * drift if scenario in ("abrupt", "recovery") else 0)), 3.0 * noise_scale),
        "temperature": rng.gauss(36.8 + (.05 * drift if scenario == "gradual" else (.45 + .025 * drift if scenario in ("abrupt", "recovery") else 0)), .08 * noise_scale),
    }
    dropout = max(dropout_pct / 100.0, .28) if scenario == "missing" else dropout_pct / 100.0
    observed: dict[str, float | None] = {}
    for channel, value in observations.items():
        if rng.random() < dropout:
            observed[channel] = None
            events.append({"time": timestamp.strftime("%H:%M"), "category": "Data quality", "event": "Synthetic measurement dropout", "detail": f"{CHANNELS[channel]['label']} unavailable at sample {step + 1}"})
            continue
        observed[channel] = float(value)
        meta = CHANNELS[channel]
        stream.ingest(Observation(channel, timestamp, float(value), {"°C": "degC"}.get(meta["unit"], meta["unit"])))
    result = stream.score(timestamp)
    row: dict[str, Any] = {"sample": step + 1, "timestamp_utc": timestamp.isoformat(), "time": timestamp.strftime("%H:%M"), **observed}
    for channel in CHANNELS:
        row[f"observed_{channel}"] = observed[channel]
    row.update({"trajectory_score": result.get("trajectory_score"), "trajectory_direction": result.get("trajectory_direction"), "state": result.get("state", "unknown"), "coverage": result.get("coverage", 0)})
    state = str(row["state"])
    if prev_state is not None and state != prev_state:
        events.append({"time": timestamp.strftime("%H:%M"), "category": "Twin output", "event": "Illustrative twin state changed", "detail": f"{prev_state.replace('_', ' ').title()} → {state.replace('_', ' ').title()}"})
    prev_state = state
    rows.append(row)
frame = pd.DataFrame(rows).set_index("sample")
latest = frame.iloc[-1]
score = latest["trajectory_score"]
score_text = "—" if pd.isna(score) else f"{float(score):.3f}"
direction = str(latest["trajectory_direction"] or "not established").replace("_", " ").title()
state_text = str(latest["state"]).replace("_", " ").title()
coverage = float(latest["coverage"] or 0)
valid_scores = frame["trajectory_score"].dropna()
score_delta = float(valid_scores.iloc[-1] - valid_scores.iloc[-2]) if len(valid_scores) > 1 else None
n_events = len(events)

def section(title: str, subtitle: str | None = None) -> None:
    st.markdown(f"<div class='vh-section'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div class='vh-muted'>{subtitle}</div>", unsafe_allow_html=True)

def link_card(item: dict[str, str]) -> None:
    st.markdown(
        f"<div class='vh-resource'><div class='vh-small'>{item['category'].upper()} · {item['kind']}</div>"
        f"<div class='vh-resource-title'>{item['title']}</div><div class='vh-muted'>{item['summary']}</div>"
        f"<div class='vh-small' style='margin-top:8px'>{item['access']}</div></div>",
        unsafe_allow_html=True,
    )
    st.link_button("Open original resource ↗", item["url"])

page_titles = {
    "Command center": ("A physiology-first\nresearch workspace.", "Explore a personal-baseline concept through deterministic synthetic signals, visible data-quality context, and a transparent research roadmap."),
    "Twin studio": ("Understand the twin.\nChange the scenario.", "Inspect warm-up, signal coverage, and within-person deviation behavior. Outputs are software heuristics, not clinical risk."),
    "Signal lab": ("Every signal.\nOne coherent timeline.", "Compare channels, explore missingness and noise, and inspect the generated traces without mixing their original units."),
    "Events & data": ("Trace every sample.\nExport the synthetic run.", "Review generated observations, state changes and quality events, then download the current simulation with its configuration."),
    "Architecture": ("From signal to\ntrajectory context.", "A transparent view of the proposed processing pipeline and which components are implemented versus planned."),
    "Hardware lab": ("Prototype the edge.\nKeep the bench safe.", "Explore the proposed USB gateway path from ESP32-S3 to the local Python stream. The current bench remains synthetic-only."),
    "Research library": ("A curated map\nof the research landscape.", "Official datasets, clinical context, methodological guidance and governance references selected for this project. External resources open at their source."),
    "Validation & governance": ("Evidence before\nclinical claims.", "Track the evidence gates that must be cleared before any claim beyond a research prototype can be considered."),
}
title, subtitle = page_titles[page]
st.markdown("<div class='vh-kicker'>VITALIS / PHYSIOLOGICAL SYSTEMS EXPLORER</div>", unsafe_allow_html=True)
st.markdown(f"<div class='vh-title'>{title.replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='vh-subtitle'>{subtitle}</div>", unsafe_allow_html=True)
st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
st.markdown("<span class='vh-chip'>● SYNTHETIC RESEARCH MODE</span> &nbsp; <span class='vh-chip vh-chip-blue'>NO LIVE PATIENT DATA</span> &nbsp; <span class='vh-chip vh-chip-warn'>NOT CLINICALLY VALIDATED</span>", unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

if page == "Command center":
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        st.markdown("<div class='vh-panel'><div class='vh-kicker'>LIVE SIMULATION SNAPSHOT</div><h3 style='font-size:1.35rem'>Current synthetic trajectory</h3><div class='vh-muted'>The display updates when you change the controls. It is a replayed simulation, not a live feed.</div></div>", unsafe_allow_html=True)
        k1, k2, k3 = st.columns(3)
        k1.metric("Latest twin state", state_text)
        k2.metric("Trajectory heuristic", score_text, delta=None if score_delta is None else f"{score_delta:+.3f} vs previous")
        k3.metric("Observed channel coverage", f"{coverage:.0%}")
        st.markdown("#### Physiological signals · independent native units")
        a, b = st.columns(2)
        for idx, channel in enumerate(CHANNELS):
            target = a if idx % 2 == 0 else b
            with target:
                st.caption(f"{CHANNELS[channel]['label']} · {CHANNELS[channel]['unit']}")
                chart = frame[[channel]].copy()
                chart.columns = [CHANNELS[channel]["label"]]
                st.line_chart(chart, height=150, color=[CHANNELS[channel]["color"]])
        st.caption("Scores are dimensionless algorithmic outputs. They are not probabilities, diagnoses, alert thresholds or recommendations.")
    with right:
        st.markdown("<div class='vh-panel'><div class='vh-kicker'>RUN CONFIGURATION</div><h3>Simulation profile</h3>", unsafe_allow_html=True)
        st.write(f"**Scenario:** {scenario_label}")
        st.write(f"**Timeline:** {steps} samples · {interval}-minute spacing")
        st.write(f"**Noise:** {noise} · **Dropout control:** {dropout_pct}%")
        st.write(f"**Intensity:** {shift_intensity}% · **Seed:** {seed}")
        st.markdown("<hr class='vh-sep'>", unsafe_allow_html=True)
        st.markdown("**Systems represented**")
        for system in ["Cardiovascular", "Oxygenation", "Respiratory", "Temperature", "Cross-channel trajectory"]:
            st.markdown(f"<div style='padding:7px 0;border-bottom:1px solid #163449;color:#b9d5e5'>◈ &nbsp; {system}</div>", unsafe_allow_html=True)
        st.markdown("<hr class='vh-sep'>", unsafe_allow_html=True)
        st.markdown(f"<div class='vh-small'>SYNTHETIC EVENT ROWS</div><div class='vh-big-number'>{n_events}</div><div class='vh-muted'>Generated quality events and twin-state transitions in this replay.</div></div>", unsafe_allow_html=True)
    section("Explore next", "Choose a workspace from the sidebar to inspect the mechanics, challenge the signals, or follow the research plan.")
    a, b, c = st.columns(3)
    with a:
        st.markdown("<div class='vh-panel'><h4>◎ Twin studio</h4><div class='vh-muted'>See the baseline warm-up, trajectory direction and coverage over time.</div></div>", unsafe_allow_html=True)
    with b:
        st.markdown("<div class='vh-panel'><h4>〰 Signal lab</h4><div class='vh-muted'>Select channels, normalize units for pattern inspection, and stress-test missingness.</div></div>", unsafe_allow_html=True)
    with c:
        st.markdown("<div class='vh-panel'><h4>▤ Research library</h4><div class='vh-muted'>Open official dataset, methods and safety resources linked to the project.</div></div>", unsafe_allow_html=True)

elif page == "Twin studio":
    section("What the adaptive twin displays", "The algorithm compares a rolling observation history with within-person references; the current output remains a heuristic deviation/trajectory description.")
    x1, x2, x3, x4 = st.columns(4)
    x1.metric("Twin state", state_text)
    x2.metric("Trajectory direction", direction)
    x3.metric("Latest heuristic", score_text)
    x4.metric("Data coverage", f"{coverage:.0%}")
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("<div class='vh-panel'><h3>Trajectory over the replay</h3><div class='vh-muted'>Early outputs can be unavailable while the synthetic baseline warms up.</div></div>", unsafe_allow_html=True)
        st.line_chart(frame[["trajectory_score"]], height=300, color=["#55d7e9"])
        st.markdown("<div class='vh-panel'><h3>Coverage timeline</h3><div class='vh-muted'>Coverage is displayed to encourage interpretation alongside data availability.</div></div>", unsafe_allow_html=True)
        st.area_chart(frame[["coverage"]], height=210, color=["#59e2bd"])
    with right:
        st.markdown("<div class='vh-panel'><h3>Current synthetic channel snapshot</h3><div class='vh-muted'>Values are generated to exercise interface behavior; they are not normal ranges or patient observations.</div></div>", unsafe_allow_html=True)
        snapshot = []
        for ch, meta in CHANNELS.items():
            val = latest[ch]
            snapshot.append({"Signal": meta["label"], "Generated value": "Unavailable" if pd.isna(val) else f"{float(val):.2f} {meta['unit']}", "System": meta["system"], "Observed": "Yes" if not pd.isna(latest[f"observed_{ch}"]) else "No"})
        st.dataframe(pd.DataFrame(snapshot), use_container_width=True, hide_index=True)
        st.markdown("#### Interpretation guardrails")
        st.markdown("- A rising or falling heuristic is not a sepsis probability.\n- ‘Within-person’ does not mean a validated patient-specific normal range.\n- Missing measurements can change the apparent trajectory.\n- No alert threshold is selected by this demo.")
        with st.expander("How the simulation is built"):
            st.write("A fixed seed generates a timeline. Scenario logic adds a stable profile, gradual shift, abrupt shift, dropout/noise, or recovery-like pattern. Observations are ingested through the timestamped twin stream. All charts refresh from the same current run.")

elif page == "Signal lab":
    section("Signal explorer", "Plot native traces separately or use within-channel standardization for shape comparison. Standardized views are for visualization only.")
    selected = st.multiselect("Channels to inspect", list(CHANNELS), default=list(CHANNELS)[:3], format_func=lambda c: f"{CHANNELS[c]['label']} ({CHANNELS[c]['unit']})")
    normalize = st.toggle("Standardize each selected channel for visual comparison", value=False)
    show_missing = st.toggle("Overlay observed-value availability", value=True)
    chart_height = st.slider("Chart height", min_value=250, max_value=650, value=380, step=50)
    if selected:
        chart = frame[selected].copy()
        chart.columns = [f"{CHANNELS[c]['label']} · {CHANNELS[c]['unit']}" for c in selected]
        if normalize:
            chart = chart.apply(lambda col: (col - col.mean()) / (col.std(ddof=0) or 1), axis=0)
            st.info("Standardized z-like values are derived only for visual comparison. They are not model inputs, probabilities or clinical thresholds.")
        st.line_chart(chart, height=chart_height)
        if show_missing:
            presence = frame[[f"observed_{c}" for c in selected]].notna().astype(int)
            presence.columns = [f"{CHANNELS[c]['label']} observed" for c in selected]
            st.markdown("#### Observation availability map")
            st.line_chart(presence, height=180)
    else:
        st.info("Choose at least one signal to render the explorer.")
    st.markdown("<div class='vh-panel'><h3>Signal quality indicators</h3><div class='vh-muted'>Synthetic dropout is applied by the scenario controls. Real deployments would require sensor-specific validity flags, timestamp quality, calibration records and explicit stale-data behavior.</div></div>", unsafe_allow_html=True)
    quality = []
    for c, meta in CHANNELS.items():
        seen = int(frame[f"observed_{c}"].notna().sum())
        quality.append({"Signal": meta["label"], "Observed samples": seen, "Missing samples": steps - seen, "Availability": f"{seen/steps:.0%}"})
    st.dataframe(pd.DataFrame(quality), use_container_width=True, hide_index=True)

elif page == "Events & data":
    section("Event timeline", "Generated events are audit-style interface examples, not clinical alerts. Use the event-category filter to focus on transitions or data quality.")
    event_df = pd.DataFrame(events, columns=["time", "category", "event", "detail"])
    if len(event_df):
        cats = sorted(event_df["category"].unique().tolist())
        chosen_cats = st.multiselect("Event categories", cats, default=cats)
        filtered = event_df[event_df["category"].isin(chosen_cats)] if chosen_cats else event_df.iloc[0:0]
        e1, e2, e3 = st.columns(3)
        e1.metric("Total generated events", len(event_df))
        e2.metric("State transition rows", int((event_df["category"] == "Twin output").sum()))
        e3.metric("Data-quality rows", int((event_df["category"] == "Data quality").sum()))
        st.dataframe(filtered, use_container_width=True, hide_index=True, height=300)
    else:
        st.info("No events were generated for this run. Try a dropout scenario or a different seed.")
    section("Synthetic samples", "The table contains generated values and stream output fields for this run only.")
    base_cols = ["timestamp_utc", "time", *CHANNELS.keys(), *[f"observed_{c}" for c in CHANNELS], "trajectory_score", "trajectory_direction", "state", "coverage"]
    visible_cols = st.multiselect("Columns to display", base_cols, default=["time", *CHANNELS.keys(), "trajectory_score", "state", "coverage"])
    st.dataframe(frame[visible_cols] if visible_cols else frame.iloc[:, 0:0], use_container_width=True, height=350)
    export_cols = ["timestamp_utc", "time", *CHANNELS.keys(), *[f"observed_{c}" for c in CHANNELS], "trajectory_score", "trajectory_direction", "state", "coverage"]
    export_frame = frame[export_cols].copy()
    config = {"app_version": APP_VERSION, "mode": "synthetic_only", "scenario": scenario_label, "seed": int(seed), "samples": int(steps), "sampling_interval_minutes": int(interval), "noise_profile": noise, "dropout_control_percent": int(dropout_pct), "shift_intensity_percent": int(shift_intensity), "clinical_validity": "not established", "patient_data_used": False}
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("↓ Download synthetic CSV", export_frame.to_csv(index=False).encode("utf-8"), file_name="vitalis_synthetic_run.csv", mime="text/csv", use_container_width=True)
    with d2:
        bundle = {"configuration": config, "summary": {"state": state_text, "trajectory_score_heuristic": None if pd.isna(score) else float(score), "trajectory_direction": direction, "coverage": coverage, "generated_event_count": n_events}, "events": events, "data_notice": "Synthetic demonstration only; not for clinical use."}
        st.download_button("↓ Download run summary JSON", json.dumps(bundle, indent=2, allow_nan=False).encode("utf-8"), file_name="vitalis_synthetic_summary.json", mime="application/json", use_container_width=True)
    st.caption("Exports contain only the generated simulation. Do not add real patient data or upload raw patient-level data to this app.")

elif page == "Architecture":
    section("System architecture", "The visual below separates implemented software components from planned acquisition and governance work.")
    st.markdown("""
    <div class="vh-flow">
      <div class="vh-node"><strong>01 · Input signals</strong><span>Timestamped values, channel names, units and quality context</span></div>
      <div class="vh-node"><strong>02 · Stream contract</strong><span>Freshness, units, order, missingness and session handling</span></div>
      <div class="vh-node"><strong>03 · Adaptive twin</strong><span>Rolling baseline, deviation features and trajectory smoothing</span></div>
      <div class="vh-node"><strong>04 · Research UI</strong><span>Signals, coverage, heuristic state, events and aggregate exports</span></div>
    </div>
    <div class="vh-panel"><h3>Proposed extension path</h3><div class="vh-muted">Device adapters → validation and quality controls → frozen feature schema → separately validated outcome model (only after governance and independent review). These stages are not represented as complete by this demo.</div></div>
    """, unsafe_allow_html=True)
    items = [
        ("Stream input contract", "Implemented", "Timestamped input handling, units, freshness and quality semantics are part of the Python streaming component."),
        ("Adaptive deviation component", "Research component", "Computes deviation/trajectory heuristics. It is not a calibrated sepsis prediction model."),
        ("Supervised horizon model", "Separate research path", "Retrospective model experiments exist; this dashboard does not load a frozen predictor or display supervised probabilities."),
        ("Live sensor acquisition", "Not implemented here", "This app generates values locally. It does not connect to sensors, serial devices or hospital systems."),
        ("Clinical action / alerting", "Not authorized", "No clinical alarm policy, diagnosis, treatment recommendation or patient-care workflow is enabled."),
    ]
    for name, status, detail in items:
        with st.expander(f"{name} · {status}"):
            st.write(detail)
    st.markdown("#### Interface boundaries")
    st.code("Synthetic generator → Observation(channel, timestamp, value, unit) → TimestampedTwinStream → AdaptivePhysiologicalTwin → dashboard", language="text")

elif page == "Hardware lab":
    section("Hardware demonstrator roadmap", "A bench demo can demonstrate data transport and software behavior. It cannot establish clinical accuracy or replace external clinical validation.")
    st.markdown("<div class='vh-panel'><div class='vh-kicker'>CURRENT STATE</div><h3>Software-only synthetic gateway</h3><div class='vh-muted'>The documented ESP32-S3 gateway emits toy data for bench tests. Physical connection, sensor integration and any human-facing measurement have not been validated here.</div></div>", unsafe_allow_html=True)
    l, r = st.columns(2, gap="large")
    with l:
        st.markdown("#### Proposed build order")
        for n, title_, detail in [
            ("01", "ESP32-S3 development board", "USB serial gateway; verify board variant, USB connector and fitted headers before purchase."),
            ("02", "Laptop + Python receiver", "Receive generated serial frames and forward them to the timestamped stream."),
            ("03", "Transport fault tests", "Disconnects, malformed frames, stale timestamps, duplicates and out-of-order observations."),
            ("04", "Sensor adapter planning", "Only after component specs, electrical limits, device documentation and safe isolation are reviewed."),
        ]:
            st.markdown(f"<div class='vh-resource'><div class='vh-small'>PHASE {n}</div><div class='vh-resource-title'>{title_}</div><div class='vh-muted'>{detail}</div></div>", unsafe_allow_html=True)
    with r:
        st.markdown("#### Bench acceptance checklist")
        items = ["Board enumerates as a serial device", "Receiver parses only documented frames", "Timestamp and unit validation tested", "Disconnect/reconnect behavior recorded", "Synthetic-only label stays visible", "Raw personal/clinical data are not logged"]
        for item in items:
            st.checkbox(item, value=False, key="bench_" + str(items.index(item)))
        st.caption("This checklist is an interactive planning aid; checking a box does not create verified test evidence.")
        st.link_button("Open ESP32-S3 official documentation ↗", "https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html")
        st.link_button("Open gateway setup guide in repository ↗", "https://github.com/culprit-k/VITALIS/blob/main/docs/ESP32_SYNTHETIC_GATEWAY.md")
    st.warning("Do not connect a prototype to a patient, use it for care, or interpret a consumer sensor as a clinically validated monitor. Physical bench work must remain non-human and supervised appropriately.")

elif page == "Research library":
    section("Curated external resource library", "A focused starter collection of original sources, not an exhaustive index or live web crawler. Links are external; review the current source, version, access conditions and citation before use.")
    categories = ["All"] + sorted({x["category"] for x in RESOURCE_LIBRARY})
    c1, c2 = st.columns([1, 1.7])
    with c1:
        category_filter = st.selectbox("Resource domain", categories)
    with c2:
        query = st.text_input("Search titles and descriptions", placeholder="e.g., external cohort, safety, reporting, sensor")
    query_l = query.strip().lower()
    filtered_resources = [x for x in RESOURCE_LIBRARY if (category_filter == "All" or x["category"] == category_filter) and (not query_l or query_l in " ".join(x.values()).lower())]
    st.caption(f"Showing {len(filtered_resources)} of {len(RESOURCE_LIBRARY)} curated resources")
    if filtered_resources:
        for item in filtered_resources:
            link_card(item)
    else:
        st.info("No curated resources match. Try a broader term or select ‘All’.")
    with st.expander("How to request additions to this library"):
        st.write("Good candidates include official dataset documentation, peer-reviewed methods papers, reporting guidelines, device manuals, regulator/ethics guidance and primary source-code documentation. Before adding, verify publisher authority, publication date/version, terms of access, citation details and relevance to VITALIS.")
    st.info("Dataset pages are not blanket permission to download or re-share records. Credentialing, training, data-use terms, institutional approvals and local governance may apply separately.")

elif page == "Validation & governance":
    section("Evidence gates", "The app exposes research maturity rather than presenting an unsupported single ‘readiness score’. Items marked open or blocked must not be described as completed validation.")
    gates = [
        {"gate": "1 · Reproduction & software quality", "status": "Partially evidenced", "summary": "The repository records retrospective experiments, source-reproduction checks and CI; strict independent reproducibility review remains an explicit gate."},
        {"gate": "2 · Independent scientific review", "status": "Open", "summary": "Independent clinical/statistical review of endpoint semantics, leakage, calibration, uncertainty and practical alert utility is outstanding."},
        {"gate": "3 · Synthetic / physical bench", "status": "Software bench recorded; physical bench open", "summary": "Synthetic replay checks exist. Physical serial testing and hardware records are still needed; no patient or live sensor use."},
        {"gate": "4 · External cohort & governance", "status": "Blocked / not completed", "summary": "No external validation claim. A cohort protocol exists, but access, pre-analysis lock, institutional/ethics/privacy review and independent endpoint mapping remain prerequisites."},
    ]
    for g in gates:
        st.markdown(f"<div class='vh-panel'><div class='vh-small'>{g['gate']}</div><div style='display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;align-items:center'><h3 style='margin:.3rem 0'>{g['status']}</h3></div><div class='vh-muted'>{g['summary']}</div></div>", unsafe_allow_html=True)
    st.markdown("#### Non-negotiable analysis boundaries")
    st.markdown("- Keep Set B evaluation-only; do not tune thresholds or features on it.\n- A challenge-positive label window is not independently adjudicated sepsis onset.\n- Freeze model, threshold, endpoint mapping and metrics before independent-cohort evaluation.\n- Keep restricted clinical data and patient-level predictions outside the repository and this demo.\n- Hardware performance is not clinical performance; synthetic replay is not external validation.")
    st.link_button("Open external validation protocol ↗", "https://github.com/culprit-k/VITALIS/blob/main/docs/EXTERNAL_VALIDATION_PROTOCOL.md")
    st.link_button("Open project status report ↗", "https://github.com/culprit-k/VITALIS/blob/main/docs/PROJECT_STATUS.md")
    st.link_button("Open release readiness audit ↗", "https://github.com/culprit-k/VITALIS/blob/main/docs/RELEASE_READINESS_AUDIT.md")
    st.warning("VITALIS remains a research prototype. It is not a medical device or clinically validated decision-support system and must not guide diagnosis, triage, treatment or patient care.")

st.markdown("<hr class='vh-sep'>", unsafe_allow_html=True)
footer_l, footer_r = st.columns([2, 1])
with footer_l:
    st.markdown("**VITALIS Research Workspace** <span class='vh-muted'>· Adaptive physiological digital-twin prototype</span>", unsafe_allow_html=True)
    st.markdown("<div class='vh-small'>Synthetic data only · No live clinical feed · No patient identifiers · No clinical decision support</div>", unsafe_allow_html=True)
with footer_r:
    st.markdown("<div style='text-align:right;color:#5d8095;font-size:.74rem'>BUILD " + APP_VERSION.upper() + "<br>RESEARCH / ENGINEERING PREVIEW</div>", unsafe_allow_html=True)
