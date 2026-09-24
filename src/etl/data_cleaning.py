"""
Data Cleaning & Quality Module
Provides modular, reusable data cleaning functions for:
- Column standardization (snake_case, lower, strip)
- Whitespace stripping
- Date & Datetime parsing to standard ISO format
- Numeric type conversion & validation
- Duplicate row detection & removal
- Invalid value detection (e.g. negative steps/calories/durations)
- Outlier flagging (IQR / Z-score rule based without deletion)
- Quality summary and cleaning report generation
"""

import sys
import os
import re
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, OUTPUTS_DIR
from src.etl.utils import get_csv_files, safe_read_csv, logger


def standardize_column_names(cols: list) -> list:
    """
    Convert column names to clean snake_case:
    - Strip whitespace
    - Insert underscore before capital letters
    - Replace special chars/spaces with underscore
    - Convert to lowercase
    """
    cleaned_cols = []
    for col in cols:
        s = col.strip()
        if s.lower() in ["id", "participantid", "participant_id"]:
            cleaned_cols.append("participant_id")
            continue
        if s.lower() in ["activitydate", "activityday", "sleepday"]:
            cleaned_cols.append("date")
            continue
        
        s = re.sub(r'(?<=[a-z0-9])([A-Z])', r'_\1', s)
        s = re.sub(r'[^a-zA-Z0-9_]', '_', s)
        s = re.sub(r'_+', '_', s).strip('_').lower()
        cleaned_cols.append(s)
        
    return cleaned_cols


def parse_date_column(series: pd.Series) -> pd.Series:
    """Parse mixed date/datetime strings to standard ISO date (YYYY-MM-DD)."""
    str_series = series.astype(str).str.strip()
    parsed = pd.to_datetime(str_series, format='mixed', errors='coerce')
    return parsed.dt.strftime('%Y-%m-%d')


def parse_datetime_column(series: pd.Series) -> pd.Series:
    """Parse date/datetime strings to standard ISO datetime (YYYY-MM-DD HH:MM:SS)."""
    str_series = series.astype(str).str.strip()
    parsed = pd.to_datetime(str_series, format='mixed', errors='coerce')
    return parsed.dt.strftime('%Y-%m-%d %H:%M:%S')


def flag_outliers_iqr(series: pd.Series, factor: float = 3.0) -> pd.Series:
    """Flag extreme outliers using IQR rule (True if > Q3 + 3*IQR or < Q1 - 3*IQR)."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - factor * iqr
    upper_bound = q3 + factor * iqr
    return (series < lower_bound) | (series > upper_bound)


def clean_daily_activity(file_path: Path) -> tuple[pd.DataFrame, dict]:
    """Clean and validate dailyActivity_merged.csv."""
    df_raw = safe_read_csv(file_path)
    rows_before = len(df_raw)
    
    df = df_raw.copy()
    df.columns = standardize_column_names(df.columns)
    
    df["participant_id"] = df["participant_id"].astype(str).str.strip()
    df["date"] = parse_date_column(df["date"])
    
    dups_removed = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    
    num_cols = [
        "total_steps", "total_distance", "tracker_distance", "logged_activities_distance",
        "very_active_distance", "moderately_active_distance", "light_active_distance", "sedentary_active_distance",
        "very_active_minutes", "fairly_active_minutes", "lightly_active_minutes", "sedentary_minutes", "calories"
    ]
    
    invalid_rows = 0
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            neg_mask = df[col] < 0
            if neg_mask.sum() > 0:
                invalid_rows += int(neg_mask.sum())
                df.loc[neg_mask, col] = 0
                
    df["is_zero_activity"] = (df["total_steps"] == 0) & (df["total_distance"] == 0)
    df["steps_outlier_flag"] = flag_outliers_iqr(df["total_steps"])
    df["calories_outlier_flag"] = flag_outliers_iqr(df["calories"])
    
    dt_series = pd.to_datetime(df["date"])
    df["weekday"] = dt_series.dt.day_name()
    df["weekday_num"] = dt_series.dt.weekday
    
    report = {
        "dataset_name": "daily_activity",
        "rows_before": rows_before,
        "rows_after": len(df),
        "duplicates_removed": dups_removed,
        "missing_values": int(df.isnull().sum().sum()),
        "invalid_values_corrected": invalid_rows,
        "outliers_flagged": int(df["steps_outlier_flag"].sum()),
        "zero_activity_days": int(df["is_zero_activity"].sum())
    }
    
    return df, report


def clean_sleep_daily(file_path: Path) -> tuple[pd.DataFrame, dict]:
    """Clean and validate sleepDay_merged.csv."""
    df_raw = safe_read_csv(file_path)
    rows_before = len(df_raw)
    
    df = df_raw.copy()
    df.columns = standardize_column_names(df.columns)
    
    df["participant_id"] = df["participant_id"].astype(str).str.strip()
    df["date"] = parse_date_column(df["date"])
    
    dups_removed = int(df.duplicated(subset=["participant_id", "date"]).sum())
    df = df.drop_duplicates(subset=["participant_id", "date"]).reset_index(drop=True)
    
    num_cols = ["total_sleep_records", "total_minutes_asleep", "total_time_in_bed"]
    invalid_rows = 0
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            neg_mask = df[col] < 0
            if neg_mask.sum() > 0:
                invalid_rows += int(neg_mask.sum())
                df.loc[neg_mask, col] = 0
                
    df["sleep_efficiency"] = np.where(
        df["total_time_in_bed"] > 0,
        (df["total_minutes_asleep"] / df["total_time_in_bed"]) * 100,
        0
    )
    df["sleep_efficiency"] = df["sleep_efficiency"].round(2)
    df["sleep_hours"] = (df["total_minutes_asleep"] / 60.0).round(2)
    
    report = {
        "dataset_name": "sleep_daily",
        "rows_before": rows_before,
        "rows_after": len(df),
        "duplicates_removed": dups_removed,
        "missing_values": int(df.isnull().sum().sum()),
        "invalid_values_corrected": invalid_rows,
        "outliers_flagged": int(flag_outliers_iqr(df["total_minutes_asleep"]).sum()),
        "zero_activity_days": 0
    }
    
    return df, report


def clean_weight_daily(file_path: Path) -> tuple[pd.DataFrame, dict]:
    """Clean and validate weightLogInfo_merged.csv."""
    df_raw = safe_read_csv(file_path)
    rows_before = len(df_raw)
    
    df = df_raw.copy()
    df.columns = standardize_column_names(df.columns)
    
    df["participant_id"] = df["participant_id"].astype(str).str.strip()
    df["datetime"] = parse_datetime_column(df["date"])
    df["date"] = parse_date_column(df["date"])
    
    dups_removed = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    
    null_count = int(df.isnull().sum().sum())
    
    for col in ["weight_kg", "weight_pounds", "bmi", "fat"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    report = {
        "dataset_name": "weight_daily",
        "rows_before": rows_before,
        "rows_after": len(df),
        "duplicates_removed": dups_removed,
        "missing_values": null_count,
        "invalid_values_corrected": 0,
        "outliers_flagged": 0,
        "zero_activity_days": 0
    }
    
    return df, report


def run_data_cleaning_pipeline(raw_dir: Path = RAW_DATA_DIR, processed_dir: Path = PROCESSED_DATA_DIR, output_dir: Path = OUTPUTS_DIR):
    """Run full data cleaning pipeline and produce quality reports."""
    logger.info("Executing Phase 3 Data Cleaning Pipeline...")
    reports = []
    
    activity_path = raw_dir / "dailyActivity_merged.csv"
    if activity_path.exists():
        df_act, rep_act = clean_daily_activity(activity_path)
        df_act.to_csv(processed_dir / "daily_activity.csv", index=False)
        reports.append(rep_act)
        
    sleep_path = raw_dir / "sleepDay_merged.csv"
    if sleep_path.exists():
        df_sleep, rep_sleep = clean_sleep_daily(sleep_path)
        df_sleep.to_csv(processed_dir / "sleep_day.csv", index=False)
        reports.append(rep_sleep)
        
    weight_path = raw_dir / "weightLogInfo_merged.csv"
    if weight_path.exists():
        df_weight, rep_weight = clean_weight_daily(weight_path)
        df_weight.to_csv(processed_dir / "weight_log.csv", index=False)
        reports.append(rep_weight)
        
    df_report = pd.DataFrame(reports)
    output_dir.mkdir(parents=True, exist_ok=True)
    report_csv = output_dir / "data_cleaning_report.csv"
    summary_csv = output_dir / "data_quality_summary.csv"
    
    df_report.to_csv(report_csv, index=False)
    
    quality_summary = pd.DataFrame([{
        "total_datasets_cleaned": len(reports),
        "total_rows_processed": int(df_report["rows_before"].sum()),
        "total_rows_retained": int(df_report["rows_after"].sum()),
        "total_duplicates_removed": int(df_report["duplicates_removed"].sum()),
        "total_missing_values": int(df_report["missing_values"].sum()),
        "total_invalid_values_corrected": int(df_report["invalid_values_corrected"].sum()),
        "total_outliers_flagged": int(df_report["outliers_flagged"].sum()),
        "data_retention_rate_pct": round((df_report["rows_after"].sum() / df_report["rows_before"].sum()) * 100, 2)
    }])
    quality_summary.to_csv(summary_csv, index=False)
    
    return df_report, quality_summary
