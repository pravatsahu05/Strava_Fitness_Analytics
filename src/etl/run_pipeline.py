"""
End-to-End ETL Pipeline Runner
Executes the full data extraction, inspection, cleaning, pre-aggregation,
and master integration pipeline in one automated script.

Execution Sequence:
1. Run Data Inventory Audit (src/etl/data_inventory.py)
2. Run Data Cleaning & Quality Engine (src/etl/data_cleaning.py)
3. Run Daily Heart Rate Aggregation (src/etl/build_hr_daily.py)
4. Run Daily & Hourly Master Integration (src/etl/build_master_dataset.py)
"""

import sys
import time
from pathlib import Path

# Add src to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.data_inventory import generate_data_inventory
from src.etl.data_cleaning import run_data_cleaning_pipeline
from src.etl.build_hr_daily import aggregate_heart_rate_daily
from src.etl.build_master_dataset import run_master_pipeline
from src.etl.utils import logger


def run_full_etl_pipeline():
    """Run all ETL steps sequentially and log timing metrics."""
    start_time = time.time()
    logger.info("==================================================")
    logger.info("  STARTING FITLIFE WELLNESS INTELLIGENCE ETL PIPELINE")
    logger.info("==================================================")

    # Step 1: Dataset Inventory Audit
    logger.info("\n--- STEP 1: Dataset Inventory Audit ---")
    df_inv = generate_data_inventory()
    logger.info(f"Inventory complete across {len(df_inv)} raw CSV files.")

    # Step 2: Data Cleaning & Quality Report
    logger.info("\n--- STEP 2: Data Cleaning & Quality Audit ---")
    df_report, df_summary = run_data_cleaning_pipeline()
    logger.info(f"Data cleaning complete. Retention Rate: {df_summary['data_retention_rate_pct'].iloc[0]}%")

    # Step 3: Heart Rate Chunk Processing & Daily Aggregation
    logger.info("\n--- STEP 3: Heart Rate Chunk Aggregation ---")
    df_hr = aggregate_heart_rate_daily()
    logger.info(f"Heart rate daily aggregation complete ({len(df_hr)} participant-days).")

    # Step 4: Master Analytical Datasets Integration
    logger.info("\n--- STEP 4: Daily & Hourly Master Dataset Integration ---")
    df_daily, df_hourly = run_master_pipeline()
    logger.info(f"Master datasets ready: daily_master ({len(df_daily)} rows), hourly_master ({len(df_hourly)} rows).")

    elapsed_time = round(time.time() - start_time, 2)
    logger.info("==================================================")
    logger.info(f"  ETL PIPELINE COMPLETED SUCCESSFULLY IN {elapsed_time} SECONDS")
    logger.info("==================================================")

    return {
        "status": "SUCCESS",
        "elapsed_seconds": elapsed_time,
        "daily_master_rows": len(df_daily),
        "hourly_master_rows": len(df_hourly),
        "retention_rate_pct": float(df_summary["data_retention_rate_pct"].iloc[0])
    }


if __name__ == "__main__":
    result = run_full_etl_pipeline()
    print("\nETL Pipeline Execution Result Summary:")
    for k, v in result.items():
        print(f"  - {k}: {v}")
