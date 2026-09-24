"""
Build Master Dataset Module
Integrates cleaned daily activity, sleep, weight, and heart-rate summary tables into
the daily master analytical table (data/processed/daily_master.csv).

Also builds the hourly master table (data/processed/hourly_master.csv).

Enforces strict logical grain rule:
ONE PARTICIPANT + ONE DATE = EXACTLY ONE ROW
Validates zero duplicates before saving.
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.etl.utils import safe_read_csv, logger
from src.etl.build_hr_daily import aggregate_heart_rate_daily


def build_hourly_master(raw_dir: Path = RAW_DATA_DIR, processed_dir: Path = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """Merge hourly calories, intensities, and steps into data/processed/hourly_master.csv."""
    logger.info("Building hourly master dataset...")

    f_cal = raw_dir / "hourlyCalories_merged.csv"
    f_int = raw_dir / "hourlyIntensities_merged.csv"
    f_stp = raw_dir / "hourlySteps_merged.csv"

    if not (f_cal.exists() and f_int.exists() and f_stp.exists()):
        logger.error("One or more hourly raw files missing!")
        return pd.DataFrame()

    df_cal = safe_read_csv(f_cal)
    df_int = safe_read_csv(f_int)
    df_stp = safe_read_csv(f_stp)

    # Standardize column headers
    for df in [df_cal, df_int, df_stp]:
        df.columns = [c.strip().lower() for c in df.columns]

    df_cal = df_cal.rename(columns={"id": "participant_id", "activityhour": "activity_hour", "calories": "calories"})
    df_int = df_int.rename(columns={"id": "participant_id", "activityhour": "activity_hour", "totalintensity": "total_intensity", "averageintensity": "average_intensity"})
    df_stp = df_stp.rename(columns={"id": "participant_id", "activityhour": "activity_hour", "steptotal": "steps"})

    # Clean IDs & Datetimes
    for df in [df_cal, df_int, df_stp]:
        df["participant_id"] = df["participant_id"].astype(str).str.strip()

    # Merge on participant_id + activity_hour
    df_hourly = pd.merge(df_cal, df_int, on=["participant_id", "activity_hour"], how="outer")
    df_hourly = pd.merge(df_hourly, df_stp, on=["participant_id", "activity_hour"], how="outer")

    # Parse date and hour
    dt_parsed = pd.to_datetime(df_hourly["activity_hour"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
    df_hourly["date"] = dt_parsed.dt.strftime('%Y-%m-%d')
    df_hourly["hour"] = dt_parsed.dt.hour

    df_hourly["weekday"] = dt_parsed.dt.day_name()
    df_hourly["weekday_num"] = dt_parsed.dt.weekday

    # Fill NaNs
    df_hourly["steps"] = df_hourly["steps"].fillna(0).astype(int)
    df_hourly["calories"] = df_hourly["calories"].fillna(0).astype(int)
    df_hourly["total_intensity"] = df_hourly["total_intensity"].fillna(0).astype(int)
    df_hourly["average_intensity"] = df_hourly["average_intensity"].fillna(0.0).astype(float)

    # Sort & reorder
    df_hourly = df_hourly[[
        "participant_id", "date", "hour", "weekday", "weekday_num",
        "steps", "calories", "total_intensity", "average_intensity"
    ]].sort_values(by=["participant_id", "date", "hour"]).reset_index(drop=True)

    out_file = processed_dir / "hourly_master.csv"
    df_hourly.to_csv(out_file, index=False)
    logger.info(f"Hourly master dataset saved to {out_file} ({len(df_hourly):,} rows).")
    return df_hourly


def build_daily_master(processed_dir: Path = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """Integrate cleaned daily tables into data/processed/daily_master.csv."""
    logger.info("Building daily master analytical table...")

    act_path = processed_dir / "daily_activity.csv"
    sleep_path = processed_dir / "sleep_day.csv"
    weight_path = processed_dir / "weight_log.csv"
    hr_path = processed_dir / "heart_rate_daily.csv"

    # Ensure heart rate daily aggregated CSV exists
    if not hr_path.exists():
        aggregate_heart_rate_daily()

    if not act_path.exists():
        logger.error(f"Daily activity file not found at {act_path}! Run data_cleaning.py first.")
        return pd.DataFrame()

    df_act = safe_read_csv(act_path)
    df_act["participant_id"] = df_act["participant_id"].astype(str).str.strip()
    df_act["date"] = df_act["date"].astype(str).str.strip()

    # 1. Prepare Sleep Data
    if sleep_path.exists():
        df_sleep = safe_read_csv(sleep_path)
        df_sleep["participant_id"] = df_sleep["participant_id"].astype(str).str.strip()
        df_sleep["date"] = df_sleep["date"].astype(str).str.strip()
        df_sleep = df_sleep[[
            "participant_id", "date", "total_minutes_asleep", "sleep_hours", "sleep_efficiency"
        ]].rename(columns={"total_minutes_asleep": "sleep_minutes"})
    else:
        df_sleep = pd.DataFrame(columns=["participant_id", "date", "sleep_minutes", "sleep_hours", "sleep_efficiency"])

    # 2. Prepare Weight Data (aggregate multiple logs per day if any)
    if weight_path.exists():
        df_weight_raw = safe_read_csv(weight_path)
        df_weight_raw["participant_id"] = df_weight_raw["participant_id"].astype(str).str.strip()
        df_weight_raw["date"] = df_weight_raw["date"].astype(str).str.strip()

        df_weight = df_weight_raw.groupby(["participant_id", "date"]).agg(
            weight=("weight_kg", "mean"),
            bmi=("bmi", "mean"),
            weight_log_count=("log_id", "count")
        ).reset_index()
    else:
        df_weight = pd.DataFrame(columns=["participant_id", "date", "weight", "bmi", "weight_log_count"])

    # 3. Prepare Heart Rate Data
    if hr_path.exists():
        df_hr = safe_read_csv(hr_path)
        df_hr["participant_id"] = df_hr["participant_id"].astype(str).str.strip()
        df_hr["date"] = df_hr["date"].astype(str).str.strip()
    else:
        df_hr = pd.DataFrame(columns=["participant_id", "date", "avg_heart_rate", "min_heart_rate", "max_heart_rate", "heart_rate_readings"])

    # Merge sequentially onto base daily_activity
    df_master = pd.merge(df_act, df_sleep, on=["participant_id", "date"], how="left")
    df_master = pd.merge(df_master, df_weight, on=["participant_id", "date"], how="left")
    df_master = pd.merge(df_master, df_hr, on=["participant_id", "date"], how="left")

    # Fill missing indicators cleanly without inventing values
    df_master["sleep_minutes"] = df_master["sleep_minutes"].fillna(0).astype(int)
    df_master["sleep_hours"] = df_master["sleep_hours"].fillna(0.0).round(2)
    df_master["sleep_efficiency"] = df_master["sleep_efficiency"].fillna(0.0).round(2)

    df_master["weight_log_count"] = df_master["weight_log_count"].fillna(0).astype(int)
    df_master["heart_rate_readings"] = df_master["heart_rate_readings"].fillna(0).astype(int)

    # Fill null weight/bmi/hr metrics with NaN (do NOT invent fake metrics)
    for col in ["weight", "bmi", "avg_heart_rate", "min_heart_rate", "max_heart_rate"]:
        df_master[col] = pd.to_numeric(df_master[col], errors='coerce')

    # Select & arrange standard master columns
    master_cols = [
        "participant_id", "date", "weekday", "weekday_num",
        "total_steps", "total_distance", "very_active_minutes", "fairly_active_minutes",
        "lightly_active_minutes", "sedentary_minutes", "calories",
        "sleep_hours", "sleep_minutes", "sleep_efficiency",
        "weight", "bmi", "weight_log_count",
        "avg_heart_rate", "min_heart_rate", "max_heart_rate", "heart_rate_readings"
    ]

    df_master = df_master[master_cols].sort_values(by=["participant_id", "date"]).reset_index(drop=True)

    # MANDATORY GRAIN UNIQUENESS VALIDATION
    logger.info("Validating daily_master logical grain uniqueness (participant_id + date)...")
    duplicate_check = df_master.groupby(["participant_id", "date"]).size()
    duplicate_count = (duplicate_check > 1).sum()

    if duplicate_count > 0:
        logger.error(f"CRITICAL ERROR: Found {duplicate_count} duplicate composite keys in daily_master!")
        raise ValueError("Grain uniqueness check failed!")

    logger.info("UNIQUENESS VALIDATION PASSED: 0 duplicate participant-day records found.")

    # Save to data/processed/daily_master.csv
    out_file = processed_dir / "daily_master.csv"
    df_master.to_csv(out_file, index=False)
    logger.info(f"Daily master dataset successfully saved to {out_file} ({len(df_master)} rows).")

    return df_master


def run_master_pipeline():
    """Execute complete master dataset integration pipeline."""
    df_hourly = build_hourly_master()
    df_daily = build_daily_master()
    return df_daily, df_hourly


if __name__ == "__main__":
    df_daily, df_hourly = run_master_pipeline()
    print("\nDaily Master Analytical Table Sample:")
    print(df_daily.head(10).to_string(index=False))
    print(f"\nTotal Daily Master Rows: {len(df_daily)} (Grain Unique: {df_daily[['participant_id', 'date']].duplicated().sum() == 0})")
