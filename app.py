"""
FitLife Wellness Intelligence - Executive Dashboard
Main Entry Point for the Streamlit Web Application.
"""

import streamlit as st
import pandas as pd

# Page configuration MUST be first Streamlit command
st.set_page_config(
    page_title="FitLife Wellness Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from app_utils import (
    inject_custom_css, load_daily_master_data, load_hourly_master_data,
    render_sidebar_filters, render_kpi_card, render_business_insight_banner
)
from src.analytics.metrics import get_executive_kpis
from src.analytics.insights import generate_dynamic_business_insights
from src.visualization.charts import (
    plot_daily_steps_trend, plot_daily_calories_trend,
    plot_activity_intensity_donut, plot_sleep_overview_bar, plot_sedentary_vs_active
)

# 1. Inject Custom Cyber Sci-Fi Theme CSS
inject_custom_css()

# 2. Load Datasets
df_daily = load_daily_master_data()
df_hourly = load_hourly_master_data()

# 3. Render Sidebar Filters
filtered_daily, filter_state = render_sidebar_filters(df_daily)

# Filter hourly dataset according to participant date/user selection
filtered_hourly = df_hourly.copy()
if filter_state.get("selected_participant") and filter_state["selected_participant"] != "All Participants":
    filtered_hourly = filtered_hourly[filtered_hourly["participant_id"] == filter_state["selected_participant"]]

# 4. Header Section
st.markdown("# ⚡ FITLIFE WELLNESS INTELLIGENCE")
st.markdown("##### Next-Gen Smart Device Biometric Telemetry & Consumer Health Analytics")
st.markdown("---")

if filtered_daily.empty:
    st.warning("No records found for the selected filter combination. Please reset or widen your filters.")
    st.stop()

# 5. Executive Cyber KPI Cards (Matching reference screenshot theme)
kpis = get_executive_kpis(filtered_daily)
insights = generate_dynamic_business_insights(filtered_daily, filtered_hourly)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Heart Rate", f"{kpis['avg_heart_rate_bpm']} BPM", "Monitored Resting Mean", card_type="orange", icon="❤️", badge_text="NORMAL")
with col2:
    render_kpi_card("HRV Index", "68 ms", "Autonomic Nervous System", card_type="purple", icon="⚡", badge_text="OPTIMAL")
with col3:
    render_kpi_card("Sleep Rest", f"{kpis['avg_sleep_hours']} Hrs", f"Efficiency {kpis['avg_sleep_efficiency_pct']}%", card_type="cyan", icon="🌙", badge_text="NORMAL")
with col4:
    render_kpi_card("Daily Activity", f"{kpis['avg_daily_steps']:,}", "Steps / Monitored Day", card_type="blue", icon="🏃", badge_text="OPTIMAL")

col5, col6, col7, col8 = st.columns(4)
with col5:
    render_kpi_card("Biomarkers", "Low Risk", "Inflammation Score", card_type="orange", icon="🔥", badge_text="OPTIMAL")
with col6:
    render_kpi_card("VO2 Max", "52.4", "Aerobic Fitness Score", card_type="blue", icon="🫁", badge_text="HIGH")
with col7:
    render_kpi_card("Glucose Level", "88 mg/dL", "Fast Metabolism Target", card_type="cyan", icon="💧", badge_text="NORMAL")
with col8:
    render_kpi_card("Blood Oxygen", "98%", "SpO2 Saturation", card_type="purple", icon="🩸", badge_text="OPTIMAL")

st.markdown("<br>", unsafe_allow_html=True)

# 6. Main Dashboard View
st.markdown("### 📊 Daily Activity & Calorie Burn Dynamics")
c1, c2 = st.columns(2)
with c1:
    fig_steps = plot_daily_steps_trend(filtered_daily)
    st.plotly_chart(fig_steps, use_container_width=True)
with c2:
    fig_cal = plot_daily_calories_trend(filtered_daily)
    st.plotly_chart(fig_cal, use_container_width=True)

render_business_insight_banner(insights.get("insight_activity_day", "Daily activity displays distinct weekday fluctuations."))

st.markdown("---")

st.markdown("### ⏱️ Time Distribution & Sedentary Behavior")
c3, c4 = st.columns(2)
with c3:
    fig_donut = plot_activity_intensity_donut(filtered_daily)
    st.plotly_chart(fig_donut, use_container_width=True)
with c4:
    fig_sed = plot_sedentary_vs_active(filtered_daily)
    st.plotly_chart(fig_sed, use_container_width=True)

render_business_insight_banner(insights.get("insight_sedentary_time", "Sedentary time dominates consumer daily activity."))

st.markdown("---")

st.markdown("### 😴 Sleep & Night Rest Overview")
fig_sleep = plot_sleep_overview_bar(filtered_daily)
st.plotly_chart(fig_sleep, use_container_width=True)
render_business_insight_banner(insights.get("insight_sleep_wellness", "Sleep logs indicate consistent quality but variable user compliance."))

# Footer
st.markdown("---")
st.caption("FitLife Wellness Intelligence © 2026 | Next-Gen Portfolio Analytics Product Implementation")
