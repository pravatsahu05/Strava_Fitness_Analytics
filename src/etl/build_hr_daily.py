"""
Heart Rate Aggregation Engine
Processes second-by-second heart rate records (2.48+ million rows) using chunk processing.
Aggregates BPM metrics to participant-date grain:
- participant_id
- date
- avg_heart_rate
- min_heart_rate
- max_heart_rate
- heart_rate_readings

Outputs:
data/processed/heart_rate_daily.csv
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.etl.utils import logger


def aggregate_heart_rate_daily(raw_dir: Path = RAW_DATA_DIR, processed_dir: Path = PROCESSED_DATA_DIR) -> pd.DataFrame:
    """Read large second-level heart rate CSV in chunks and aggregate to daily grain."""
    hr_csv = raw_dir / "heartrate_seconds_merged.csv"
    if not hr_csv.exists():
        logger.warning(f"Heart rate CSV not found at {hr_csv}")
        return pd.DataFrame()

    logger.info(f"Processing large heart rate file in chunks: {hr_csv.name}...")

    chunk_size = 500000
    chunk_summaries = []
    total_processed_rows = 0

    for chunk in pd.read_csv(hr_csv, chunksize=chunk_size):
        total_processed_rows += len(chunk)

        # Standardize column names
        chunk.columns = [c.strip().lower() for c in chunk.columns]
        chunk = chunk.rename(columns={"id": "participant_id", "time": "raw_time", "value": "bpm"})

        chunk["participant_id"] = chunk["participant_id"].astype(str).str.strip()

        # Fast explicit date parsing
        dt_parsed = pd.to_datetime(chunk["raw_time"], format="%m/%d/%Y %I:%M:%S %p", errors='coerce')
        chunk["date"] = dt_parsed.dt.strftime('%Y-%m-%d')

        chunk["bpm"] = pd.to_numeric(chunk["bpm"], errors='coerce')
        chunk = chunk.dropna(subset=["date", "bpm"])

        # Group by participant_id + date within chunk
        grp = chunk.groupby(["participant_id", "date"]).agg(
            bpm_sum=("bpm", "sum"),
            bpm_min=("bpm", "min"),
            bpm_max=("bpm", "max"),
            bpm_count=("bpm", "count")
        ).reset_index()

        chunk_summaries.append(grp)

    logger.info(f"Finished processing {total_processed_rows:,} raw heart rate rows across all chunks.")

    # Combine chunk summaries
    all_chunks = pd.concat(chunk_summaries, ignore_index=True)

    # Final aggregation across all chunks
    final_hr_daily = all_chunks.groupby(["participant_id", "date"]).agg(
        total_bpm_sum=("bpm_sum", "sum"),
        min_heart_rate=("bpm_min", "min"),
        max_heart_rate=("bpm_max", "max"),
        heart_rate_readings=("bpm_count", "sum")
    ).reset_index()

    # Compute weighted average heart rate
    final_hr_daily["avg_heart_rate"] = (
        final_hr_daily["total_bpm_sum"] / final_hr_daily["heart_rate_readings"]
    ).round(2)

    # Reorder columns
    final_hr_daily = final_hr_daily[[
        "participant_id", "date", "avg_heart_rate", "min_heart_rate", "max_heart_rate", "heart_rate_readings"
    ]].sort_values(by=["participant_id", "date"]).reset_index(drop=True)

    # Save to data/processed/heart_rate_daily.csv
    processed_dir.mkdir(parents=True, exist_ok=True)
    out_file = processed_dir / "heart_rate_daily.csv"
    final_hr_daily.to_csv(out_file, index=False)

    logger.info(f"Aggregated daily heart rate saved to {out_file} ({len(final_hr_daily)} participant-day rows).")
    return final_hr_daily


if __name__ == "__main__":
    df_hr = aggregate_heart_rate_daily()
    print("\nDaily Heart Rate Aggregation Sample:")
    print(df_hr.head(10).to_string(index=False))
