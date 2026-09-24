"""
Analytics Metrics Engine Module
Computes KPI summary metrics, aggregations, user segmentations,
weekday trends, and participant profiles from processed data.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import PROCESSED_DATA_DIR
from src.etl.utils import safe_read_csv, logger


def get_executive_kpis(df_daily: pd.DataFrame) -> dict:
    """Compute high-level executive KPI metrics from daily_master dataframe."""
    if df_daily.empty:
        return {}

    # Exclude zero-activity days for active metric averages
    active_df = df_daily[df_daily["total_steps"] > 0]
    sleep_df = df_daily[df_daily["sleep_minutes"] > 0]
    hr_df = df_daily[df_daily["avg_heart_rate"].notnull()]

    kpis = {
        "total_participants": int(df_daily["participant_id"].nunique()),
        "total_monitored_days": int(len(df_daily)),
        "avg_daily_steps": int(round(active_df["total_steps"].mean(), 0)) if not active_df.empty else 0,
        "avg_daily_calories": int(round(active_df["calories"].mean(), 0)) if not active_df.empty else 0,
        "avg_very_active_mins": float(round(active_df["very_active_minutes"].mean(), 1)) if not active_df.empty else 0.0,
        "avg_fairly_active_mins": float(round(active_df["fairly_active_minutes"].mean(), 1)) if not active_df.empty else 0.0,
        "avg_lightly_active_mins": float(round(active_df["lightly_active_minutes"].mean(), 1)) if not active_df.empty else 0.0,
        "avg_total_active_mins": float(round((active_df["very_active_minutes"] + active_df["fairly_active_minutes"] + active_df["lightly_active_minutes"]).mean(), 1)) if not active_df.empty else 0.0,
        "avg_sedentary_mins": float(round(df_daily["sedentary_minutes"].mean(), 1)),
        "avg_sedentary_hours": float(round(df_daily["sedentary_minutes"].mean() / 60.0, 1)),
        "avg_sleep_hours": float(round(sleep_df["sleep_hours"].mean(), 2)) if not sleep_df.empty else 0.0,
        "avg_sleep_efficiency_pct": float(round(sleep_df["sleep_efficiency"].mean(), 1)) if not sleep_df.empty else 0.0,
        "sleep_users_count": int(sleep_df["participant_id"].nunique()) if not sleep_df.empty else 0,
        "avg_heart_rate_bpm": float(round(hr_df["avg_heart_rate"].mean(), 1)) if not hr_df.empty else 0.0,
        "compliance_rate_pct": float(round((len(active_df) / len(df_daily)) * 100, 1))
    }

    return kpis


def get_weekday_activity_summary(df_daily: pd.DataFrame) -> pd.DataFrame:
    """Group daily metrics by weekday ordered Monday to Sunday."""
    if df_daily.empty:
        return pd.DataFrame()

    active_df = df_daily[df_daily["total_steps"] > 0]
    grp = active_df.groupby(["weekday_num", "weekday"]).agg(
        record_count=("participant_id", "count"),
        avg_steps=("total_steps", "mean"),
        avg_calories=("calories", "mean"),
        avg_very_active_mins=("very_active_minutes", "mean"),
        avg_fairly_active_mins=("fairly_active_minutes", "mean"),
        avg_lightly_active_mins=("lightly_active_minutes", "mean"),
        avg_sedentary_mins=("sedentary_minutes", "mean")
    ).reset_index().sort_values("weekday_num")

    for col in ["avg_steps", "avg_calories"]:
        grp[col] = grp[col].round(0).astype(int)
    for col in ["avg_very_active_mins", "avg_fairly_active_mins", "avg_lightly_active_mins", "avg_sedentary_mins"]:
        grp[col] = grp[col].round(1)

    return grp


def get_participant_segmentation(df_daily: pd.DataFrame) -> pd.DataFrame:
    """Segment participants by CDC daily step benchmarks."""
    if df_daily.empty:
        return pd.DataFrame()

    active_df = df_daily[df_daily["total_steps"] > 0]
    user_avg = active_df.groupby("participant_id").agg(
        avg_steps=("total_steps", "mean"),
        avg_calories=("calories", "mean"),
        avg_active_mins=("very_active_minutes", lambda x: (x + active_df.loc[x.index, "fairly_active_minutes"] + active_df.loc[x.index, "lightly_active_minutes"]).mean())
    ).reset_index()

    conditions = [
        (user_avg["avg_steps"] >= 10000),
        (user_avg["avg_steps"] >= 7500) & (user_avg["avg_steps"] < 10000),
        (user_avg["avg_steps"] >= 5000) & (user_avg["avg_steps"] < 7500),
        (user_avg["avg_steps"] < 5000)
    ]
    labels = ["Highly Active (>=10k steps)", "Moderately Active (7.5k-10k steps)", "Low Active (5k-7.5k steps)", "Sedentary (<5k steps)"]
    user_avg["activity_segment"] = np.select(conditions, labels, default="Sedentary (<5k steps)")

    seg_summary = user_avg.groupby("activity_segment").agg(
        participant_count=("participant_id", "count"),
        avg_segment_steps=("avg_steps", "mean"),
        avg_segment_calories=("avg_calories", "mean")
    ).reset_index()

    seg_summary["pct_of_users"] = (seg_summary["participant_count"] / len(user_avg) * 100).round(1)
    seg_summary["avg_segment_steps"] = seg_summary["avg_segment_steps"].round(0).astype(int)
    seg_summary["avg_segment_calories"] = seg_summary["avg_segment_calories"].round(0).astype(int)

    return seg_summary


def get_hourly_heatmap_matrix(df_hourly: pd.DataFrame) -> pd.DataFrame:
    """Create a Weekday x Hour step intensity matrix for heatmap visualization."""
    if df_hourly.empty:
        return pd.DataFrame()

    pivot = df_hourly.pivot_table(
        index="weekday_num",
        columns="hour",
        values="steps",
        aggfunc="mean"
    ).round(0)

    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot.index = [weekday_names[i] for i in pivot.index]
    return pivot


if __name__ == "__main__":
    df_daily = safe_read_csv(PROCESSED_DATA_DIR / "daily_master.csv")
    kpis = get_executive_kpis(df_daily)
    print("\nExecutive KPIs Test:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
