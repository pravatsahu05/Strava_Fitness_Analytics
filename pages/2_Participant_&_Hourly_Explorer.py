"""
FitLife Wellness Intelligence - Page 2: Participant Profile & Hourly Diurnal Explorer
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Participant & Hourly Explorer | FitLife", page_icon="👤", layout="wide")

from app_utils import (
    inject_custom_css, load_daily_master_data, load_hourly_master_data,
    render_sidebar_filters, render_kpi_card, render_business_insight_banner
)
from src.visualization.charts import (
    plot_participant_daily_trend, plot_participant_activity_profile,
    plot_participant_sleep_profile, plot_participant_hr_profile,
    plot_hourly_steps, plot_hourly_calories, plot_hourly_intensity, plot_weekday_hour_heatmap
)

inject_custom_css()

df_daily = load_daily_master_data()
df_hourly = load_hourly_master_data()
_, filter_state = render_sidebar_filters(df_daily)

st.markdown("# 👤 PARTICIPANT & HOURLY BEHAVIOR EXPLORER")
st.markdown("##### Individual User Telemetry Deep-Dives and Hour-by-Hour Diurnal Dynamics")
st.markdown("---")

tab1, tab2 = st.tabs(["👤 Participant Explorer", "⏰ Hourly Diurnal Dynamics"])

with tab1:
    if df_daily.empty:
        st.warning("No dataset loaded.")
    else:
        all_participants = sorted(list(df_daily["participant_id"].unique()))
        selected_user = st.selectbox("👤 Select Participant ID to Explore", options=all_participants)

        df_user = df_daily[df_daily["participant_id"] == selected_user].sort_values("date").reset_index(drop=True)
        active_user_days = df_user[df_user["total_steps"] > 0]
        sleep_user_days = df_user[df_user["sleep_minutes"] > 0]
        hr_user_days = df_user[df_user["avg_heart_rate"].notnull()]

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            render_kpi_card("Active Days", f"{len(active_user_days)} Days", f"Total Logged: {len(df_user)}", card_type="cyan", icon="📅")
        with c2:
            render_kpi_card("Avg Steps", f"{int(round(active_user_days['total_steps'].mean(), 0)) if not active_user_days.empty else 0:,}", "Steps / Day", card_type="blue", icon="🏃")
        with c3:
            render_kpi_card("Avg Calories", f"{int(round(active_user_days['calories'].mean(), 0)) if not active_user_days.empty else 0:,}", "kcal / Day", card_type="orange", icon="🔥")
        with c4:
            render_kpi_card("Avg Sleep", f"{round(sleep_user_days['sleep_hours'].mean(), 2) if not sleep_user_days.empty else 0}h", f"{len(sleep_user_days)} Sleep Nights", card_type="purple", icon="😴")
        with c5:
            render_kpi_card("Avg HR", f"{round(hr_user_days['avg_heart_rate'].mean(), 1) if not hr_user_days.empty else 'N/A'} BPM", "Cardio Average", card_type="orange", icon="❤️")

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_participant_daily_trend(df_user), use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(plot_participant_activity_profile(df_user), use_container_width=True)
        with col2:
            if not sleep_user_days.empty:
                st.plotly_chart(plot_participant_sleep_profile(df_user), use_container_width=True)
            else:
                st.info("No sleep logs recorded for this participant.")

        if not hr_user_days.empty:
            st.plotly_chart(plot_participant_hr_profile(df_user), use_container_width=True)

with tab2:
    if df_hourly.empty:
        st.warning("No hourly activity records available.")
    else:
        filtered_hourly = df_hourly.copy()
        if filter_state.get("selected_participant") and filter_state["selected_participant"] != "All Participants":
            filtered_hourly = filtered_hourly[filtered_hourly["participant_id"] == filter_state["selected_participant"]]

        hourly_avg = filtered_hourly.groupby("hour")["steps"].mean()
        peak_h = int(hourly_avg.idxmax())
        peak_h_steps = int(round(hourly_avg.max(), 0))

        c6, c7, c8 = st.columns(3)
        with c6:
            render_kpi_card("Peak Activity Hour", f"{peak_h}:00 ({peak_h%12 or 12} {'PM' if peak_h>=12 else 'AM'})", f"Avg {peak_h_steps:,} Steps", card_type="orange", icon="⏰")
        with c7:
            render_kpi_card("Hourly Logs", f"{len(filtered_hourly):,}", "Recorded 60-Min Windows", card_type="cyan", icon="📊")
        with c8:
            render_kpi_card("Users Monitored", f"{filtered_hourly['participant_id'].nunique()} Users", "Active Devices", card_type="purple", icon="👥")

        st.markdown("<br>", unsafe_allow_html=True)
        st.plotly_chart(plot_weekday_hour_heatmap(filtered_hourly), use_container_width=True)

        c9, c10 = st.columns(2)
        with c9:
            st.plotly_chart(plot_hourly_steps(filtered_hourly), use_container_width=True)
        with c10:
            st.plotly_chart(plot_hourly_calories(filtered_hourly), use_container_width=True)
