"""
ETL Utility Helper Functions
Common helper methods for logging, file inspection, and type conversion.
"""

import sys
import logging
from pathlib import Path
import pandas as pd

# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ETL_Utils")


def get_csv_files(directory_path: Path):
    """Recursively search for and return a sorted list of CSV files in directory_path."""
    if not directory_path.exists():
        logger.error(f"Directory path does not exist: {directory_path}")
        return []
    return sorted(list(directory_path.glob("*.csv")))


def safe_read_csv(file_path: Path, **kwargs) -> pd.DataFrame:
    """Safely read a CSV file with error handling."""
    try:
        df = pd.read_csv(file_path, **kwargs)
        return df
    except Exception as e:
        logger.error(f"Error reading CSV file {file_path.name}: {e}")
        return pd.DataFrame()
