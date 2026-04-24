import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Safran Sensor Dashboard", layout="wide")
st.title("🏭 Industrial Sensor Dashboard — Safran Composites")

# ── SIDEBAR UPLOAD ─────────────────────────────────────────────────────────
st.sidebar.header("📂 Upload Sensor Data")
uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])

if not uploaded:
    st.info("👈 Upload a sensor CSV file to get started.")
    st.stop()

# ── SEND FILE TO FASTAPI ───────────────────────────────────────────────────
response = requests.post(
    f"{API_URL}/upload",
    files={"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
)
result = response.json()

if "error" in result:
    st.error(f"❌ Invalid file: {result['error']}")
    st.stop()

st.sidebar.success(f"✅ {result['rows']} rows loaded & formalized")

with st.sidebar.expander("🔍 Formalization preview"):
    st.json(result["preview"])

# ── SIDEBAR FILTERS ────────────────────────────────────────────────────────
st.sidebar.header("🎛️ Filters & Thresholds")
limit        = st.sidebar.slider("Data points", 100, 10000, 1000)
failure_only = st.sidebar.checkbox("Show failures only")
torque_thresh = st.sidebar.slider("⚠️ Torque alert (Nm)", 20.0, 80.0, 60.0)
wear_thresh   = st.sidebar.slider("⚠️ Tool wear alert (min)", 50, 250, 200)

# ── KPI CARDS ─────────────────────────────────────────────────────────────
kpis = requests.get(f"{API_URL}/kpis").json()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("⚙️ Health Score",    f"{kpis['avg_health_score']}%")
c2.metric("🔴 Failures",         kpis['total_failures'])
c3.metric("🌱 Total CO₂ (kg)",  kpis['total_co2_kg'])
c4.metric("🔧 Avg Tool Wear",   f"{kpis['avg_tool_wear_min']} min")
c5.metric("⚠️ Outliers",         kpis['outlier_count'])

# ── LOAD SENSOR DATA ───────────────────────────────────────────────────────
df = pd.DataFrame(requests.get(
    f"{API_URL}/sensors",
    params={"limit": limit, "failure_only": failure_only}
).json())

if df.empty:
    st.warning("No data returned. Try adjusting your filters.")
    st.stop()

# ── TABS ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📈 Sensor Trends", "🔥 Correlation", "🌱 Eco-Design"])

with tab1:
    sensor = st.selectbox("Select sensor", [
        "air_temp_c", "proc_temp_c", "rot_speed_rpm", "torque_nm", "tool_wear_min"
    ])
    fig = px.line(
        df.reset_index(), x="index", y=sensor,
        color_discrete_sequence=["#2E75B6"],
        title=f"{sensor} over time"
    )
    failures = df[df["machine_failure"] == 1].index.tolist()
    for f in failures[:50]:
        fig.add_vline(x=f, line_color="red", line_width=0.5, opacity=0.4)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("🔴 Red lines = machine failure events")

with tab2:
    cols = ["air_temp_c", "proc_temp_c", "rot_speed_rpm",
            "torque_nm", "tool_wear_min", "health_score"]
    corr = df[cols].corr().round(2)
    fig2 = px.imshow(
        corr, text_auto=True,
        color_continuous_scale="Blues",
        title="Sensor Correlation Heatmap"
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.info("💡 Strong correlations between process temperature and torque indicate thermal stress on tooling.")

with tab3:
    st.subheader("🌱 Eco-Design KPI Tracker")
    e1, e2 = st.columns(2)
    with e1:
        fig3 = px.area(
            df.reset_index(), x="index", y="energy_kwh",
            title="Energy Consumption (kWh)",
            color_discrete_sequence=["#70AD47"]
        )
        st.plotly_chart(fig3, use_container_width=True)
    with e2:
        fig4 = px.bar(
            df.reset_index(), x="index", y="co2_kg",
            title="CO₂ Emissions (kg)",
            color_discrete_sequence=["#ED7D31"]
        )
        st.plotly_chart(fig4, use_container_width=True)
    st.metric("♻️ Total CO₂ This Dataset", f"{df['co2_kg'].sum():.2f} kg")
    st.caption("Formula: Power (W) = Torque × (RPM × 2π/60) → Energy (kWh) → CO₂ using ADEME French grid factor 0.233")