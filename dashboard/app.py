"""Streamlit viewer for validated aggregate-only VITALIS reports."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from vitalis.reporting import AggregateReportError, normalize_aggregate_report

MAX_REPORT_BYTES = 10 * 1024 * 1024

st.set_page_config(page_title="VITALIS Research Dashboard", page_icon="🩺", layout="wide")
st.title("VITALIS · Research Evaluation")
st.warning(
    "Research prototype only. Not for diagnosis, triage, treatment, or patient-care decisions."
)
st.write(
    "View aggregate evaluation summaries from the baseline and horizon experiments. "
    "Upload aggregate-only JSON; never upload patient records, row-level predictions, "
    "identifiers, or score archives."
)

uploaded = st.file_uploader("Aggregate metrics JSON", type=["json"])
if uploaded is None:
    st.info("No report loaded.")
    st.code(
        "python scripts/train_baseline.py /path/to/local_psv_data "
        "--output outputs/baseline_metrics.json"
    )
    st.caption(
        "Horizon reports can be generated with scripts/evaluate_horizon_cross_cohort.py. "
        "Keep cohort files and feature caches outside the repository."
    )
    st.stop()

if uploaded.size > MAX_REPORT_BYTES:
    st.error("This file exceeds the 10 MiB aggregate-report limit.")
    st.stop()

try:
    report = json.loads(uploaded.getvalue().decode("utf-8"))
    normalized = normalize_aggregate_report(report)
except (json.JSONDecodeError, UnicodeDecodeError, AggregateReportError) as exc:
    st.error(f"Report rejected: {exc}")
    st.info(
        "Accepted schemas: baseline test_metrics/patient_counts, cross-cohort "
        "aggregate_by_horizon, or source-verified aggregate_metrics."
    )
    st.stop()

metadata = normalized["metadata"]
left, middle, right = st.columns(3)
left.metric("Report type", normalized["kind"].replace("_", " ").title())
middle.metric("Run date", str(metadata.get("run_date") or "Not recorded"))
right.metric("Feature count", str(metadata.get("feature_count") or "Not recorded"))

if metadata.get("status"):
    st.info(str(metadata["status"]))
if metadata.get("archive_sha256"):
    st.caption(f"Source archive SHA-256: {metadata['archive_sha256']}")

protocol = metadata.get("protocol", {})
if protocol:
    with st.expander("Experiment protocol and provenance"):
        st.json(protocol)
cohorts = metadata.get("cohorts", {})
if cohorts:
    with st.expander("Aggregate cohort inventory"):
        st.json(cohorts)

frame = pd.DataFrame(normalized["rows"])
st.subheader("Aggregate metrics")
if normalized["kind"] == "baseline":
    counts = normalized.get("patient_counts", {})
    st.write("Baseline report patient counts")
    st.json(counts)
    st.dataframe(frame[["metric", "model", "value"]], use_container_width=True, hide_index=True)
    chart_frame = frame.set_index("metric")[["value"]]
    st.bar_chart(chart_frame)
    if normalized.get("test_alert_burden"):
        st.subheader("Alert burden against challenge-label windows")
        st.json(normalized["test_alert_burden"])
    if normalized.get("confusion_matrix") is not None:
        st.subheader("Confusion matrix at the stated threshold")
        st.json(normalized["confusion_matrix"])
    if normalized.get("limitations"):
        st.subheader("Report-specific limitations")
        for limitation in normalized["limitations"]:
            st.write(f"- {limitation}")
else:
    if "horizon_hours" in frame:
        horizon_values = sorted(
            int(value) for value in frame["horizon_hours"].dropna().unique()
        )
        selected_horizon = st.selectbox("Forecast horizon (hours)", horizon_values)
        frame = frame[frame["horizon_hours"] == selected_horizon]
    metrics = sorted(str(value) for value in frame["metric"].unique())
    selected_metric = st.selectbox("Metric", metrics)
    metric_frame = frame[frame["metric"] == selected_metric].copy()
    display_columns = ["model", "metric"]
    if "horizon_hours" in metric_frame:
        display_columns.insert(0, "horizon_hours")
    display_columns.extend(
        column for column in ("mean", "sample_sd") if column in metric_frame
    )
    st.dataframe(
        metric_frame[display_columns].sort_values("model"),
        use_container_width=True,
        hide_index=True,
    )
    if "mean" in metric_frame:
        chart_frame = metric_frame.set_index("model")[["mean"]]
        st.bar_chart(chart_frame)

st.subheader("Interpretation limits")
st.markdown(
    "- Results are retrospective benchmark summaries, not prospective or clinical validation.\n"
    "- Challenge-label horizons forecast entry into the benchmark's positive-label window, "
    "not independently adjudicated biological sepsis onset.\n"
    "- Set B is a benchmark evaluation cohort, not a genuinely independent clinical cohort.\n"
    "- Fixed thresholds and alert policies are research settings, not approved clinical operating points."
)
st.caption(
    "VITALIS is research-only. Do not use this software or its outputs to guide patient care."
)
