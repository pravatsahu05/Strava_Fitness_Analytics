"""
Integration Tests for ETL Pipeline & SQLite Database
Tests logical grain uniqueness, SQLite database existence, and table schema integrity.
"""

import sys
import sqlite3
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.etl.config import PROCESSED_DATA_DIR, DATABASE_PATH
from src.etl.utils import safe_read_csv
from src.analytics.sql_runner import get_db_connection


def test_daily_master_grain_uniqueness():
    """
    CRITICAL MANDATORY TEST:
    participant_id + date MUST be unique in daily_master (0 duplicate keys).
    """
    master_csv = PROCESSED_DATA_DIR / "daily_master.csv"
    assert master_csv.exists(), "daily_master.csv does not exist! Run pipeline first."

    df_master = safe_read_csv(master_csv)
    assert not df_master.empty, "daily_master.csv is empty!"

    # Uniqueness assertion on (participant_id, date)
    duplicate_count = df_master.duplicated(subset=["participant_id", "date"]).sum()
    assert duplicate_count == 0, f"FAILED: Found {duplicate_count} duplicate participant-day composite keys!"


def test_sqlite_database_and_tables_exist():
    """Test that fitness.db exists and contains all 6 required relational tables."""
    assert DATABASE_PATH.exists(), f"SQLite database not found at {DATABASE_PATH}!"

    conn = get_db_connection(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    required_tables = ["daily_master", "daily_activity", "sleep_daily", "weight_daily", "heart_rate_daily", "hourly_master"]
    for tbl in required_tables:
        assert tbl in tables, f"Required SQLite table '{tbl}' missing from database!"


def test_daily_master_schema_columns():
    """Test that daily_master table contains all required schema columns."""
    master_csv = PROCESSED_DATA_DIR / "daily_master.csv"
    df_master = safe_read_csv(master_csv)

    expected_cols = [
        "participant_id", "date", "weekday", "weekday_num",
        "total_steps", "total_distance", "very_active_minutes", "fairly_active_minutes",
        "lightly_active_minutes", "sedentary_minutes", "calories",
        "sleep_hours", "sleep_minutes", "sleep_efficiency",
        "weight", "bmi", "weight_log_count",
        "avg_heart_rate", "min_heart_rate", "max_heart_rate", "heart_rate_readings"
    ]
    for col in expected_cols:
        assert col in df_master.columns, f"Expected column '{col}' missing from daily_master!"
