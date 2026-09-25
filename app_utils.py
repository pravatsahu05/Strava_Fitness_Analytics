"""
Streamlit Application Utilities Module
Provides cached data loading, CSS injection, sidebar filtering, and UI card rendering.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

from src.etl.config import BASE_DIR, PROCESSED_DATA_DIR
from src.etl.utils import safe_read_csv

CSS_PATH = BASE_DIR / "assets" / "style.css"


def inject_custom_css():
    """Inject assets/style.css stylesheet into Streamlit app."""
    if CSS_PATH.exists():
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_daily_master_data() -> pd.DataFrame:
    """Load cached daily_master dataset."""
    file_path = PROCESSED_DATA_DIR / "daily_master.csv"
    if not file_path.exists():
        try:
            from src.etl.run_pipeline import run_full_etl_pipeline
            run_full_etl_pipeline()
        except Exception as e:
            return pd.DataFrame()

    if not file_path.exists():
        return pd.DataFrame()

    df = safe_read_csv(file_path)
    if not df.empty:
        df["participant_id"] = df["participant_id"].astype(str).str.strip()
        df["date_dt"] = pd.to_datetime(df["date"])
    return df


@st.cache_data(ttl=3600)
def load_hourly_master_data() -> pd.DataFrame:
    """Load cached hourly_master dataset."""
    file_path = PROCESSED_DATA_DIR / "hourly_master.csv"
    if not file_path.exists():
        try:
            from src.etl.run_pipeline import run_full_etl_pipeline
            run_full_etl_pipeline()
        except Exception as e:
            return pd.DataFrame()

    if not file_path.exists():
        return pd.DataFrame()

    df = safe_read_csv(file_path)
    if not df.empty:
        df["participant_id"] = df["participant_id"].astype(str).str.strip()
        df["date_dt"] = pd.to_datetime(df["date"])
    return df


def render_sidebar_filters(df_daily: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Render interactive sidebar filter controls and return filtered DataFrame."""
    st.sidebar.markdown("## ⚡ FITLIFE")
    st.sidebar.markdown("*Wellness Intelligence Platform*")
    st.sidebar.markdown("---")

    if df_daily.empty:
        return df_daily, {}

    min_date = df_daily["date_dt"].min().date()
    max_date = df_daily["date_dt"].max().date()

    st.sidebar.markdown("### 🎛️ Dashboard Filters")

    # 1. Date Range Filter
    selected_dates = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # 2. Participant Filter
    all_participants = ["All Participants"] + sorted(list(df_daily["participant_id"].unique()))
    selected_participant = st.sidebar.selectbox("Participant", options=all_participants)

    # 3. Weekday Filter
    weekdays = ["All Days", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    selected_weekday = st.sidebar.selectbox("Day of Week", options=weekdays)

    # 4. Activity Level Filter
    activity_levels = ["All Activity Levels", "High Activity (>=10k steps)", "Moderate (5k-10k steps)", "Low/Sedentary (<5k steps)"]
    selected_level = st.sidebar.selectbox("Activity Threshold", options=activity_levels)

    # Filter Logic Application
    filtered = df_daily.copy()

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_d, end_d = selected_dates
        filtered = filtered[(filtered["date_dt"].dt.date >= start_d) & (filtered["date_dt"].dt.date <= end_d)]

    if selected_participant != "All Participants":
        filtered = filtered[filtered["participant_id"] == selected_participant]

    if selected_weekday != "All Days":
        filtered = filtered[filtered["weekday"] == selected_weekday]

    if selected_level == "High Activity (>=10k steps)":
        filtered = filtered[filtered["total_steps"] >= 10000]
    elif selected_level == "Moderate (5k-10k steps)":
        filtered = filtered[(filtered["total_steps"] >= 5000) & (filtered["total_steps"] < 10000)]
    elif selected_level == "Low/Sedentary (<5k steps)":
        filtered = filtered[filtered["total_steps"] < 5000]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"Filtered Records: **{len(filtered)}** / {len(df_daily)}")

    filter_state = {
        "selected_participant": selected_participant,
        "selected_weekday": selected_weekday,
        "selected_level": selected_level
    }

    return filtered, filter_state


def render_kpi_card(title: str, value: str, subtitle: str = "", card_type: str = "cyan", icon: str = "⚡", badge_text: str = ""):
    """Render futuristic glowing cyber KPI card matching reference picture."""
    badge_html = f'<span class="cyber-badge badge-{card_type}">{badge_text}</span>' if badge_text else ''
    html = f"""
    <div class="cyber-card cyber-card-{card_type}">
        <div class="cyber-card-header">
            <span class="cyber-card-title">{title}</span>
            <span class="cyber-card-icon">{icon}</span>
        </div>
        <div class="cyber-card-value">{value}</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="cyber-card-subtitle">{subtitle}</span>
            {badge_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_business_insight_banner(insight_text: str):
    """Render highlighted business insight banner."""
    html = f"""
    <div class="insight-box">
        <p>💡 <b>Business Insight:</b> {insight_text}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
