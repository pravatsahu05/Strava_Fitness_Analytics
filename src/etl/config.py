"""
ETL Configuration Module
Centralized constants, file paths, and dataset schema definitions.
"""

from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw" / "fitabase.zip" / "Fitabase Data 4.12.16-5.12.16"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "fitness.db"
OUTPUTS_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
EXPORTS_DIR = OUTPUTS_DIR / "exports"
FIGURES_DIR = OUTPUTS_DIR / "figures"

# Ensure essential directories exist
for directory in [PROCESSED_DATA_DIR, DATABASE_DIR, OUTPUTS_DIR, REPORTS_DIR, EXPORTS_DIR, FIGURES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
