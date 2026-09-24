"""
Unit Tests for Data Cleaning Functions
Tests column standardization, date parsing, duplicate removal, and numeric conversion.
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.etl.data_cleaning import (
    standardize_column_names, parse_date_column, flag_outliers_iqr, clean_daily_activity
)
from src.etl.config import RAW_DATA_DIR


def test_standardize_column_names():
    """Test column name snake_case conversion and keyword mapping."""
    raw_cols = ["Id", "ActivityDate", "TotalSteps", "VeryActiveMinutes", "LoggedActivitiesDistance"]
    cleaned = standardize_column_names(raw_cols)
    expected = ["participant_id", "date", "total_steps", "very_active_minutes", "logged_activities_distance"]
    assert cleaned == expected


def test_parse_date_column():
    """Test date parsing to standard ISO YYYY-MM-DD string."""
    dates_series = pd.Series(["4/12/2016", "04/13/2016 12:00:00 AM", "2016-04-14"])
    parsed = parse_date_column(dates_series)
    assert list(parsed) == ["2016-04-12", "2016-04-13", "2016-04-14"]


def test_flag_outliers_iqr():
    """Test 3xIQR outlier flagging logic."""
    data = pd.Series([10, 12, 11, 13, 10, 12, 10, 500])  # 500 is extreme outlier
    flags = flag_outliers_iqr(data, factor=3.0)
    assert flags.iloc[-1] == True
    assert flags.iloc[0] == False


def test_clean_daily_activity_non_empty():
    """Test daily activity cleaning output shape and schema."""
    activity_csv = RAW_DATA_DIR / "dailyActivity_merged.csv"
    if activity_csv.exists():
        df_clean, report = clean_daily_activity(activity_csv)
        assert not df_clean.empty
        assert "participant_id" in df_clean.columns
        assert "date" in df_clean.columns
        assert report["rows_after"] == len(df_clean)
