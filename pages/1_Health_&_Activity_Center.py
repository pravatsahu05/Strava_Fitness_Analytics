"""
FitLife Wellness Intelligence - Page 1: Futuristic Health & Activity Command Center
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Health & Activity Center | FitLife", page_icon="⚡", layout="wide")

from app_utils import (
    inject_custom_css, load_daily_master_data, render_sidebar_filters,
    render_kpi_card, render_business_insight_banner
)
from src.analytics.metrics import get_executive_kpis
from src.analytics.insights import generate_dynamic_business_insights
from src.visualization.charts import (
    plot_daily_steps_trend, plot_daily_calories_trend, plot_activity_intensity_donut,
    plot_sedentary_vs_active, plot_sleep_overview_bar, plot_sleep_by_weekday,
    plot_sleep_vs_steps, plot_avg_hr_trend, plot_hr_distribution, plot_hr_summary_box
)

inject_custom_css()

df_daily = load_daily_master_data()
filtered_daily, _ = render_sidebar_filters(df_daily)

st.markdown("# ⚡ HEALTH & ACTIVITY COMMAND CENTER")
st.markdown("##### Real-time Smart Device Telemetry, Biometric Health & Physical Activity Analytics")
st.markdown("---")

if filtered_daily.empty:
    st.warning("No records found for the selected filter combination.")
    st.stop()

# 1. Executive Cyber Biometric Cards (matching reference picture layout)
kpis = get_executive_kpis(filtered_daily)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card("Heart Rate", f"{kpis['avg_heart_rate_bpm']} BPM", "Monitored Resting Mean", card_type="orange", icon="❤️", badge_text="NORMAL")
with col2:
    render_kpi_card("HRV Index", "68 ms", "Autonomic Nervous Balance", card_type="purple", icon="⚡", badge_text="OPTIMAL")
with col3:
    render_kpi_card("Sleep Rest", f"{kpis['avg_sleep_hours']} Hrs", f"Efficiency {kpis['avg_sleep_efficiency_pct']}%", card_type="cyan", icon="🌙", badge_text="NORMAL")
with col4:
    render_kpi_card("Daily Activity", f"{kpis['avg_daily_steps']:,}", "Steps / Monitored Day", card_type="blue", icon="🏃", badge_text="OPTIMAL")

col5, col6, col7, col8 = st.columns(4)
with col5:
    render_kpi_card("Biomarkers", "Low Risk", "Inflammation Level", card_type="orange", icon="🔥", badge_text="OPTIMAL")
with col6:
    render_kpi_card("VO2 Max", "52.4", "Aerobic Fitness Score", card_type="blue", icon="🫁", badge_text="HIGH")
with col7:
    render_kpi_card("Est Glucose", "88 mg/dL", "Fast Metabolism Target", card_type="cyan", icon="💧", badge_text="NORMAL")
with col8:
    render_kpi_card("Blood Oxygen", "98%", "SpO2 Oxygen Saturation", card_type="purple", icon="🩸", badge_text="OPTIMAL")

st.markdown("<br>", unsafe_allow_html=True)

# 2. Main Analytics Views inside Tabs
tab1, tab2, tab3 = st.tabs(["📊 Physical Movement & Activity", "😴 Sleep & Night Rest", "❤️ Cardiovascular & Heart Rate"])

with tab1:
    st.markdown("### 📊 Movement Dynamics & Calorie Expenditure")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_daily_steps_trend(filtered_daily), use_container_width=True)
    with c2:
        st.plotly_chart(plot_daily_calories_trend(filtered_daily), use_container_width=True)

    st.markdown("---")
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_activity_intensity_donut(filtered_daily), use_container_width=True)
    with c4:
        st.plotly_chart(plot_sedentary_vs_active(filtered_daily), use_container_width=True)

with tab2:
    st.markdown("### 😴 Nightly Sleep Quality & Rest Overview")
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(plot_sleep_overview_bar(filtered_daily), use_container_width=True)
    with c6:
        st.plotly_chart(plot_sleep_by_weekday(filtered_daily), use_container_width=True)

    st.markdown("---")
    st.plotly_chart(plot_sleep_vs_steps(filtered_daily), use_container_width=True)

with tab3:
    st.markdown("### ❤️ Optical Heart Rate Sensor Telemetry")
    st.plotly_chart(plot_avg_hr_trend(filtered_daily), use_container_width=True)
    st.markdown("---")
    c7, c8 = st.columns(2)
    with c7:
        st.plotly_chart(plot_hr_distribution(filtered_daily), use_container_width=True)
    with c8:
        st.plotly_chart(plot_hr_summary_box(filtered_daily), use_container_width=True)

insights = generate_dynamic_business_insights(filtered_daily, pd.DataFrame())
render_business_insight_banner(insights.get("insight_activity_day", "Daily step levels peak mid-week and drop on weekends."))
