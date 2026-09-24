"""
Unit Tests for Analytics Metrics Engine
Tests KPI calculations, segmentation, and metrics validation functions.
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analytics.metrics import get_executive_kpis, get_participant_segmentation
from src.analytics.validation import validate_daily_master
from src.etl.config import PROCESSED_DATA_DIR
from src.etl.utils import safe_read_csv


def test_get_executive_kpis():
    """Test executive KPI dictionary output format and calculation logic."""
    sample_data = pd.DataFrame([
        {
            "participant_id": "1", "date": "2016-04-12", "total_steps": 10000,
            "calories": 2000, "very_active_minutes": 30, "fairly_active_minutes": 15,
            "lightly_active_minutes": 200, "sedentary_minutes": 700,
            "sleep_hours": 7.0, "sleep_minutes": 420, "sleep_efficiency": 90.0,
            "avg_heart_rate": 75.0
        },
        {
            "participant_id": "1", "date": "2016-04-13", "total_steps": 5000,
            "calories": 1500, "very_active_minutes": 10, "fairly_active_minutes": 10,
            "lightly_active_minutes": 150, "sedentary_minutes": 800,
            "sleep_hours": 6.0, "sleep_minutes": 360, "sleep_efficiency": 85.0,
            "avg_heart_rate": 80.0
        }
    ])
    kpis = get_executive_kpis(sample_data)
    assert kpis["total_participants"] == 1
    assert kpis["total_monitored_days"] == 2
    assert kpis["avg_daily_steps"] == 7500
    assert kpis["avg_daily_calories"] == 1750


def test_validate_daily_master_success():
    """Test validation module passes on clean processed daily_master data."""
    master_csv = PROCESSED_DATA_DIR / "daily_master.csv"
    if master_csv.exists():
        df_master = safe_read_csv(master_csv)
        res = validate_daily_master(df_master)
        assert res["valid"] == True
        assert len(res["errors"]) == 0
        assert res["rows"] == 940
