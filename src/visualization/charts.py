"""
Plotly Interactive Charting Module
Implements all 26 dashboard charts with sci-fi cyberpunk aesthetics,
glowing neon lines, custom tooltips, smooth color gradients, and dynamic filtering support.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from src.visualization.theme import (
    theme_layout, ACCENT_CYAN, ACCENT_BLUE, ACCENT_PURPLE, ACCENT_ORANGE,
    ACCENT_PINK, ACCENT_AMBER, ACCENT_GREEN, SEDENTARY_DARK, COLOR_SEQUENCE,
    CYBER_SCALE_CYAN, CYBER_SCALE_ORANGE, CYBER_SCALE_PURPLE
)


def apply_theme(fig: go.Figure, title_text: str = "") -> go.Figure:
    """Apply standard sci-fi cyberpunk layout theme to any Plotly figure."""
    fig.update_layout(theme_layout)
    if title_text:
        fig.update_layout(title_text=title_text)
    return fig


# 1. Executive Dashboard Charts
def plot_daily_steps_trend(df: pd.DataFrame) -> go.Figure:
    """Chart 1: Daily steps trend over time with cyber glow line & area fill."""
    active_df = df[df["total_steps"] > 0]
    daily_avg = active_df.groupby("date")["total_steps"].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_avg["date"],
        y=daily_avg["total_steps"],
        mode="lines+markers",
        name="Average Steps",
        line=dict(color=ACCENT_CYAN, width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.08)',
        marker=dict(size=7, color=ACCENT_BLUE, line=dict(color=ACCENT_CYAN, width=1.5)),
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Steps:</b> %{y:,.0f}<extra></extra>"
    ))
    fig.add_hline(y=10000, line_dash="dash", line_color=ACCENT_GREEN, annotation_text="CDC 10k Goal", annotation_position="top right")
    return apply_theme(fig, "⚡ Daily Steps Trend Across Participants")


def plot_daily_calories_trend(df: pd.DataFrame) -> go.Figure:
    """Chart 2: Daily calories burned trend with orange glowing line."""
    active_df = df[df["calories"] > 0]
    daily_cal = active_df.groupby("date")["calories"].mean().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_cal["date"],
        y=daily_cal["calories"],
        mode="lines+markers",
        name="Avg Calories",
        line=dict(color=ACCENT_ORANGE, width=3),
        fill='tozeroy',
        fillcolor='rgba(255, 107, 53, 0.08)',
        marker=dict(size=7, color=ACCENT_AMBER, line=dict(color=ACCENT_ORANGE, width=1.5)),
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Calories:</b> %{y:,.0f} kcal<extra></extra>"
    ))
    return apply_theme(fig, "🔥 Daily Calorie Burn Trend")


def plot_activity_intensity_donut(df: pd.DataFrame) -> go.Figure:
    """Chart 3: Overall activity intensity minutes distribution pie/donut."""
    active_df = df[df["total_steps"] > 0]
    totals = {
        "Very Active": active_df["very_active_minutes"].sum(),
        "Fairly Active": active_df["fairly_active_minutes"].sum(),
        "Lightly Active": active_df["lightly_active_minutes"].sum(),
        "Sedentary": active_df["sedentary_minutes"].sum()
    }

    fig = go.Figure(data=[go.Pie(
        labels=list(totals.keys()),
        values=list(totals.values()),
        hole=0.6,
        marker=dict(colors=[ACCENT_CYAN, ACCENT_BLUE, ACCENT_ORANGE, SEDENTARY_DARK], line=dict(color='#040711', width=2)),
        hovertemplate="<b>Intensity:</b> %{label}<br><b>Minutes:</b> %{value:,.0f} (%{percent})<extra></extra>"
    )])
    return apply_theme(fig, "⏱️ Daily Time Distribution by Activity Zone")


def plot_sleep_overview_bar(df: pd.DataFrame) -> go.Figure:
    """Chart 4: Daily average sleep hours overview with purple cyber bars."""
    sleep_df = df[df["sleep_minutes"] > 0]
    avg_sleep = sleep_df.groupby("date")["sleep_hours"].mean().reset_index()

    fig = go.Figure(data=[go.Bar(
        x=avg_sleep["date"],
        y=avg_sleep["sleep_hours"],
        marker=dict(color=ACCENT_PURPLE, line=dict(color=ACCENT_CYAN, width=1)),
        hovertemplate="<b>Date:</b> %{x}<br><b>Avg Sleep:</b> %{y:.2f} hrs<extra></extra>"
    )])
    fig.add_hline(y=7.0, line_dash="dash", line_color=ACCENT_GREEN, annotation_text="Recommended 7h", annotation_position="top left")
    return apply_theme(fig, "😴 Daily Average Sleep Hours")


def plot_sedentary_vs_active(df: pd.DataFrame) -> go.Figure:
    """Chart 5: Sedentary vs Active minutes Stacked Bar by Weekday."""
    active_df = df[df["total_steps"] > 0]
    grp = active_df.groupby(["weekday_num", "weekday"]).agg(
        active_mins=("very_active_minutes", lambda x: (x + active_df.loc[x.index, "fairly_active_minutes"] + active_df.loc[x.index, "lightly_active_minutes"]).mean()),
        sedentary_mins=("sedentary_minutes", "mean")
    ).reset_index().sort_values("weekday_num")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=grp["weekday"], y=grp["active_mins"], name="Total Active Mins", marker_color=ACCENT_CYAN))
    fig.add_trace(go.Bar(x=grp["weekday"], y=grp["sedentary_mins"], name="Sedentary Mins", marker_color=SEDENTARY_DARK))
    fig.update_layout(barmode="stack")
    return apply_theme(fig, "🛋️ Active vs Sedentary Minutes by Weekday")


# 2. Activity Analytics Charts
def plot_weekday_steps_bar(df: pd.DataFrame) -> go.Figure:
    """Chart 6: Average Steps by Weekday."""
    active_df = df[df["total_steps"] > 0]
    grp = active_df.groupby(["weekday_num", "weekday"])["total_steps"].mean().reset_index().sort_values("weekday_num")

    colors = [ACCENT_CYAN if w == grp.loc[grp['total_steps'].idxmax(), 'weekday'] else ACCENT_BLUE for w in grp['weekday']]

    fig = go.Figure(data=[go.Bar(
        x=grp["weekday"],
        y=grp["total_steps"],
        marker=dict(color=colors, line=dict(color='rgba(0,242,254,0.4)', width=1)),
        hovertemplate="<b>%{x}:</b> %{y:,.0f} steps<extra></extra>"
    )])
    return apply_theme(fig, "📅 Average Steps by Weekday")


def plot_steps_distribution(df: pd.DataFrame) -> go.Figure:
    """Chart 7: Daily Steps Distribution Histogram."""
    active_df = df[df["total_steps"] > 0]
    fig = px.histogram(active_df, x="total_steps", nbins=30, color_discrete_sequence=[ACCENT_CYAN])
    fig.update_layout(showlegend=False)
    return apply_theme(fig, "📊 Daily Steps Distribution")


def plot_calories_distribution(df: pd.DataFrame) -> go.Figure:
    """Chart 8: Daily Calories Distribution Histogram."""
    active_df = df[df["calories"] > 0]
    fig = px.histogram(active_df, x="calories", nbins=30, color_discrete_sequence=[ACCENT_ORANGE])
    fig.update_layout(showlegend=False)
    return apply_theme(fig, "🔥 Daily Calories Distribution")


def plot_steps_vs_calories(df: pd.DataFrame) -> go.Figure:
    """Chart 9: Steps vs Calories Scatter Plot with cyber scale."""
    active_df = df[df["total_steps"] > 0]
    fig = px.scatter(
        active_df, x="total_steps", y="calories", color="very_active_minutes",
        color_continuous_scale=CYBER_SCALE_CYAN, hover_data=["participant_id", "date"]
    )
    return apply_theme(fig, "⚡ Daily Steps vs Calories Burned")


def plot_active_mins_vs_calories(df: pd.DataFrame) -> go.Figure:
    """Chart 10: Active Minutes vs Calories Scatter Plot."""
    active_df = df[df["total_steps"] > 0].copy()
    active_df["total_active_mins"] = active_df["very_active_minutes"] + active_df["fairly_active_minutes"] + active_df["lightly_active_minutes"]
    fig = px.scatter(active_df, x="total_active_mins", y="calories", color="weekday", color_discrete_sequence=COLOR_SEQUENCE)
    return apply_theme(fig, "🏃 Total Active Minutes vs Calories")


def plot_participant_activity_comparison(df: pd.DataFrame) -> go.Figure:
    """Chart 11: Top 15 Participant Step Comparison Bar."""
    active_df = df[df["total_steps"] > 0]
    grp = active_df.groupby("participant_id")["total_steps"].mean().reset_index().sort_values("total_steps", ascending=False).head(15)
    fig = px.bar(grp, x="participant_id", y="total_steps", color="total_steps", color_continuous_scale=CYBER_SCALE_CYAN)
    return apply_theme(fig, "🏆 Top 15 Participant Average Steps")


# 3. Sleep & Wellness Charts
def plot_sleep_distribution(df: pd.DataFrame) -> go.Figure:
    """Chart 12: Sleep Hours Distribution Histogram."""
    sleep_df = df[df["sleep_minutes"] > 0]
    fig = px.histogram(sleep_df, x="sleep_hours", nbins=25, color_discrete_sequence=[ACCENT_PURPLE])
    return apply_theme(fig, "😴 Sleep Duration Distribution (Hours)")


def plot_sleep_by_weekday(df: pd.DataFrame) -> go.Figure:
    """Chart 13: Sleep Duration by Weekday."""
    sleep_df = df[df["sleep_minutes"] > 0]
    grp = sleep_df.groupby(["weekday_num", "weekday"])["sleep_hours"].mean().reset_index().sort_values("weekday_num")
    fig = px.bar(grp, x="weekday", y="sleep_hours", color_discrete_sequence=[ACCENT_PURPLE])
    return apply_theme(fig, "🛏️ Average Sleep Hours by Weekday")


def plot_sleep_vs_steps(df: pd.DataFrame) -> go.Figure:
    """Chart 14: Sleep Hours vs Total Steps Scatter Plot."""
    sleep_df = df[(df["sleep_minutes"] > 0) & (df["total_steps"] > 0)]
    fig = px.scatter(sleep_df, x="total_steps", y="sleep_hours", color="sleep_efficiency", color_continuous_scale=CYBER_SCALE_PURPLE)
    return apply_theme(fig, "👟 Daily Steps vs Sleep Duration")


def plot_sleep_vs_sedentary(df: pd.DataFrame) -> go.Figure:
    """Chart 15: Sleep Hours vs Sedentary Minutes Scatter Plot."""
    sleep_df = df[df["sleep_minutes"] > 0]
    fig = px.scatter(sleep_df, x="sedentary_minutes", y="sleep_hours", color_discrete_sequence=[ACCENT_AMBER])
    return apply_theme(fig, "🛋️ Sedentary Minutes vs Sleep Duration")


# 4. Heart Rate Charts
def plot_avg_hr_trend(df: pd.DataFrame) -> go.Figure:
    """Chart 16: Average Heart Rate Trend Line."""
    hr_df = df[df["avg_heart_rate"].notnull()]
    daily_hr = hr_df.groupby("date")["avg_heart_rate"].mean().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_hr["date"], y=daily_hr["avg_heart_rate"],
        mode="lines+markers", line=dict(color=ACCENT_ORANGE, width=3),
        fill='tozeroy', fillcolor='rgba(255, 107, 53, 0.08)',
        marker=dict(size=6, color=ACCENT_AMBER)
    ))
    return apply_theme(fig, "❤️ Daily Average Heart Rate Trend (BPM)")


def plot_hr_distribution(df: pd.DataFrame) -> go.Figure:
    """Chart 17: Heart Rate Distribution Histogram."""
    hr_df = df[df["avg_heart_rate"].notnull()]
    fig = px.histogram(hr_df, x="avg_heart_rate", nbins=20, color_discrete_sequence=[ACCENT_ORANGE])
    return apply_theme(fig, "💓 Heart Rate BPM Distribution")


def plot_hr_summary_box(df: pd.DataFrame) -> go.Figure:
    """Chart 18: Min, Max & Average Heart Rate Range Boxplot."""
    hr_df = df[df["avg_heart_rate"].notnull()]
    fig = go.Figure()
    fig.add_trace(go.Box(y=hr_df["min_heart_rate"], name="Min BPM", marker_color=ACCENT_CYAN))
    fig.add_trace(go.Box(y=hr_df["avg_heart_rate"], name="Avg BPM", marker_color=ACCENT_BLUE))
    fig.add_trace(go.Box(y=hr_df["max_heart_rate"], name="Max BPM", marker_color=ACCENT_ORANGE))
    return apply_theme(fig, "📈 Heart Rate Ranges (Min / Avg / Max BPM)")


# 5. Hourly Behavior Charts
def plot_hourly_steps(df_hourly: pd.DataFrame) -> go.Figure:
    """Chart 19: Average Hourly Steps Bar Chart."""
    grp = df_hourly.groupby("hour")["steps"].mean().reset_index()
    fig = px.bar(grp, x="hour", y="steps", color="steps", color_continuous_scale=CYBER_SCALE_CYAN)
    return apply_theme(fig, "⏰ Average Step Intensity by Hour of Day")


def plot_hourly_calories(df_hourly: pd.DataFrame) -> go.Figure:
    """Chart 20: Average Hourly Calories Bar Chart."""
    grp = df_hourly.groupby("hour")["calories"].mean().reset_index()
    fig = px.bar(grp, x="hour", y="calories", color_discrete_sequence=[ACCENT_ORANGE])
    return apply_theme(fig, "🔥 Average Calorie Expenditure by Hour")


def plot_hourly_intensity(df_hourly: pd.DataFrame) -> go.Figure:
    """Chart 21: Average Hourly Activity Intensity Line Chart."""
    grp = df_hourly.groupby("hour")["total_intensity"].mean().reset_index()
    fig = px.line(grp, x="hour", y="total_intensity", color_discrete_sequence=[ACCENT_CYAN])
    return apply_theme(fig, "⚡ Total Activity Intensity by Hour")


def plot_weekday_hour_heatmap(df_hourly: pd.DataFrame) -> go.Figure:
    """Chart 22: Weekday x Hour Heatmap."""
    pivot = df_hourly.pivot_table(index="weekday_num", columns="hour", values="steps", aggfunc="mean").round(0)
    weekday_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    pivot.index = [weekday_names[i] for i in pivot.index if i < len(weekday_names)]

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[f"{h}:00" for h in pivot.columns],
        y=pivot.index,
        colorscale=CYBER_SCALE_CYAN,
        hovertemplate="Day: %{y}<br>Hour: %{x}<br>Avg Steps: %{z:,.0f}<extra></extra>"
    ))
    return apply_theme(fig, "🔥 Activity Heatmap (Weekday × Hour)")


# 6. Participant Explorer Charts
def plot_participant_daily_trend(df_user: pd.DataFrame) -> go.Figure:
    """Chart 23: Participant Daily Step & Calorie Trend."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_user["date"], y=df_user["total_steps"], name="Steps", line=dict(color=ACCENT_CYAN, width=2.5)))
    fig.add_trace(go.Scatter(x=df_user["date"], y=df_user["calories"], name="Calories", yaxis="y2", line=dict(color=ACCENT_ORANGE, width=2.5)))

    fig.update_layout(
        yaxis2=dict(title="Calories (kcal)", overlaying="y", side="right", showgrid=False)
    )
    return apply_theme(fig, "👤 Daily Steps & Calorie Trend")


def plot_participant_activity_profile(df_user: pd.DataFrame) -> go.Figure:
    """Chart 24: Participant Activity Breakdown Donut."""
    totals = {
        "Very Active": df_user["very_active_minutes"].sum(),
        "Fairly Active": df_user["fairly_active_minutes"].sum(),
        "Lightly Active": df_user["lightly_active_minutes"].sum(),
        "Sedentary": df_user["sedentary_minutes"].sum()
    }
    fig = go.Figure(data=[go.Pie(labels=list(totals.keys()), values=list(totals.values()), hole=0.55, marker=dict(colors=[ACCENT_CYAN, ACCENT_BLUE, ACCENT_ORANGE, SEDENTARY_DARK]))])
    return apply_theme(fig, "⏱️ Participant Time Breakdown")


def plot_participant_sleep_profile(df_user: pd.DataFrame) -> go.Figure:
    """Chart 25: Participant Sleep Hours Bar."""
    sleep_df = df_user[df_user["sleep_minutes"] > 0]
    fig = px.bar(sleep_df, x="date", y="sleep_hours", color_discrete_sequence=[ACCENT_PURPLE])
    return apply_theme(fig, "😴 Participant Daily Sleep Duration")


def plot_participant_hr_profile(df_user: pd.DataFrame) -> go.Figure:
    """Chart 26: Participant Heart Rate Profile Line."""
    hr_df = df_user[df_user["avg_heart_rate"].notnull()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hr_df["date"], y=hr_df["max_heart_rate"], name="Max HR", line=dict(color=ACCENT_ORANGE, dash="dot")))
    fig.add_trace(go.Scatter(x=hr_df["date"], y=hr_df["avg_heart_rate"], name="Avg HR", line=dict(color=ACCENT_CYAN, width=2.5)))
    fig.add_trace(go.Scatter(x=hr_df["date"], y=hr_df["min_heart_rate"], name="Min HR", line=dict(color=ACCENT_BLUE, dash="dot")))
    return apply_theme(fig, "❤️ Participant Heart Rate Profile (BPM)")
