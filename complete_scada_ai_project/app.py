import streamlit as st
import time
from virtual_plant import VirtualPlant
from diagnostic_engine import evaluate_diagnostics
from prognostics_engine import PrognosticsEngine
from dashboard import render_svg_schematic, create_trend_chart
from agents.groq_client import DiagnosticAgent

st.set_page_config(page_title="Industrial SCADA & AI Diagnostics", layout="wide", page_icon="🏭")

st.title("🏭 Industrial Process SCADA & Autonomous AI Diagnostics")
st.markdown("**Tank T-101 Monitoring & Diagnostic Control Center**")

st.sidebar.header("🕹 Virtual Plant Controls")
selected_tag = st.sidebar.selectbox("Select Instrument Tag", ["LT_101", "PT_101", "TT_101", "FT_101"])
scenario = st.sidebar.selectbox(
    "Inject Fault / Condition Scenario",
    [
        "NORMAL",
        "LOOP_LOSS",
        "UNDERRANGE",
        "OVERRANGE",
        "STUCK_SIGNAL",
        "NOISY_SIGNAL",
        "PROCESS_HIGH",
        "PROCESS_LOW",
        "PLC_DCS_SCALING_MISMATCH"
    ]
)

plant = VirtualPlant(tag=selected_tag)
prognostics = PrognosticsEngine()
ai_agent = DiagnosticAgent()

payload = plant.generate_payload(scenario)
diag_result = evaluate_diagnostics(payload)
prog_result = prognostics.calculate_rul(selected_tag, payload["current_ma"], payload["history"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Instrument Tag", payload["tag"])
col2.metric("Raw Current (mA)", f"{payload['current_ma']} mA")
col3.metric("Engineering Value", f"{diag_result['engineering_value']}")
col4.metric("Signal Status", diag_result["status"], delta_color="normal" if diag_result["status"] == "NORMAL" else "inverse")

st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📍 Tank T-101 Interactive Schematic")
    eng_val = diag_result["engineering_value"]
    svg_html = render_svg_schematic(eng_val if eng_val is not None else 0.0, diag_result["status"])
    st.components.v1.html(svg_html, height=290)

with col_right:
    st.subheader("📈 Signal Telemetry (4-20 mA Trend)")
    fig = create_trend_chart(payload["history"], tag=selected_tag)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col_diag, col_prog = st.columns([1, 1])

with col_diag:
    st.subheader("🔍 Deterministic Diagnostic Engine")
    st.json(diag_result)

with col_prog:
    st.subheader("⏳ Stage 2 Prognostics & Remaining Useful Life (RUL)")
    st.write(f"**Health Index:** {prog_result['health_index_pct']}%")
    st.progress(int(prog_result['health_index_pct']))
    st.write(f"**Estimated RUL:** {prog_result['estimated_rul_days']} Days")
    st.write(f"**Degradation Stage:** `{prog_result['degradation_stage']}`")
    st.warning(f"**SOP Guidance:** {prog_result['recommended_sop']}")

st.divider()

st.subheader("🤖 AI Field Technician Briefing")
briefing = ai_agent.format_technician_briefing(diag_result)
st.markdown(briefing)
