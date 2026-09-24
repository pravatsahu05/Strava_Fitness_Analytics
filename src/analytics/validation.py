"""
Data & Metrics Validation Module
Provides validation checks for dataset completeness, schema compliance,
and mathematical consistency.
"""

import sys
from pathlib import Path
import pandas as pd

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import PROCESSED_DATA_DIR
from src.etl.utils import safe_read_csv, logger


def validate_daily_master(df_daily: pd.DataFrame) -> dict:
    """Validate daily_master dataset schema, non-emptiness, and metric logic."""
    errors = []
    warnings = []

    if df_daily.empty:
        return {"valid": False, "errors": ["daily_master is empty!"], "warnings": []}

    # Required columns check
    required_cols = [
        "participant_id", "date", "total_steps", "total_distance",
        "very_active_minutes", "fairly_active_minutes", "lightly_active_minutes",
        "sedentary_minutes", "calories", "sleep_hours", "sleep_efficiency"
    ]
    missing_cols = [col for col in required_cols if col not in df_daily.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    # Uniqueness check on (participant_id, date)
    dups = df_daily.duplicated(subset=["participant_id", "date"]).sum()
    if dups > 0:
        errors.append(f"Found {dups} duplicate composite keys in daily_master!")

    # Mathematical sanity checks
    if (df_daily["total_steps"] < 0).sum() > 0:
        errors.append("Negative step counts detected!")
    if (df_daily["calories"] < 0).sum() > 0:
        errors.append("Negative calorie values detected!")

    is_valid = len(errors) == 0
    return {
        "valid": is_valid,
        "rows": len(df_daily),
        "participants": df_daily["participant_id"].nunique(),
        "errors": errors,
        "warnings": warnings
    }


if __name__ == "__main__":
    df_daily = safe_read_csv(PROCESSED_DATA_DIR / "daily_master.csv")
    res = validate_daily_master(df_daily)
    print("\nDataset Metric Validation Results:")
    for k, v in res.items():
        print(f"  - {k}: {v}")
