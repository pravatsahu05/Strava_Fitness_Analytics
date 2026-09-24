"""
Data Inventory Module
Scans every CSV file in the Fitabase raw dataset, extracts schema metadata,
data types, row/column counts, missing values, duplicates, column names,
and inferred logical grains, then saves the result to outputs/data_inventory.csv.
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import RAW_DATA_DIR, OUTPUTS_DIR
from src.etl.utils import get_csv_files, safe_read_csv, logger


def infer_dataset_grain(file_name: str, cols: list) -> str:
    """Infer logical grain based on filename and schema columns."""
    cols_lower = [c.lower() for c in cols]
    
    if "daily" in file_name.lower() or file_name.startswith("sleepDay"):
        if "id" in cols_lower and any(d in cols_lower for d in ["activitydate", "activityday", "sleepday", "date"]):
            return "Participant + Date"
    elif "hourly" in file_name.lower() or "wide" in file_name.lower():
        if "id" in cols_lower and "activityhour" in cols_lower:
            return "Participant + Date + Hour"
    elif "minute" in file_name.lower():
        if "id" in cols_lower and any(m in cols_lower for m in ["activityminute", "date"]):
            return "Participant + Date + Minute"
    elif "heartrate" in file_name.lower():
        if "id" in cols_lower and "time" in cols_lower:
            return "Participant + Timestamp (Second)"
    elif "weight" in file_name.lower():
        if "id" in cols_lower and "date" in cols_lower:
            return "Participant + Timestamp/Date"
    
    return "Unknown / Unclassified"


def generate_data_inventory(raw_dir: Path = RAW_DATA_DIR, output_dir: Path = OUTPUTS_DIR) -> pd.DataFrame:
    """Scan raw CSV files and generate schema & metadata inventory report."""
    csv_files = get_csv_files(raw_dir)
    if not csv_files:
        logger.error(f"No CSV files found in {raw_dir}")
        return pd.DataFrame()
    
    logger.info(f"Beginning dataset inventory audit across {len(csv_files)} files...")
    inventory_records = []
    
    for csv_file in csv_files:
        file_name = csv_file.name
        logger.info(f"Auditing {file_name}...")
        
        # Load full dataframe for thorough statistics
        df = safe_read_csv(csv_file)
        if df.empty:
            continue
            
        num_rows = len(df)
        num_cols = len(df.columns)
        column_names = list(df.columns)
        
        # Datatypes summary
        dtypes_summary = {str(k): int(v) for k, v in df.dtypes.value_counts().to_dict().items()}
        
        # Null values analysis
        null_count = int(df.isnull().sum().sum())
        cols_with_nulls = [col for col in df.columns if df[col].isnull().sum() > 0]
        
        # Duplicate rows analysis
        duplicate_rows = int(df.duplicated().sum())
        
        # Column categorization
        id_cols = [col for col in df.columns if "id" in col.lower()]
        date_time_cols = [
            col for col in df.columns 
            if any(term in col.lower() for term in ["date", "time", "day", "hour", "minute"])
        ]
        numeric_cols = list(df.select_dtypes(include=["number"]).columns)
        categorical_cols = list(df.select_dtypes(include=["object", "category"]).columns)
        
        # Logical grain inference
        approx_grain = infer_dataset_grain(file_name, column_names)
        
        inventory_records.append({
            "Filename": file_name,
            "Total_Rows": num_rows,
            "Total_Columns": num_cols,
            "Approximate_Grain": approx_grain,
            "ID_Columns": ", ".join(id_cols),
            "DateTime_Columns": ", ".join(date_time_cols),
            "Numeric_Columns_Count": len(numeric_cols),
            "Categorical_Columns_Count": len(categorical_cols),
            "Missing_Values_Total": null_count,
            "Columns_With_Missing": ", ".join(cols_with_nulls) if cols_with_nulls else "None",
            "Duplicate_Rows": duplicate_rows,
            "All_Column_Names": ", ".join(column_names)
        })
    
    inventory_df = pd.DataFrame(inventory_records)
    
    # Save output to outputs/data_inventory.csv
    output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = output_dir / "data_inventory.csv"
    inventory_df.to_csv(out_csv, index=False)
    logger.info(f"Successfully generated data inventory report at: {out_csv}")
    
    return inventory_df


if __name__ == "__main__":
    df_inv = generate_data_inventory()
    print("\nData Inventory Summary:")
    print(df_inv[["Filename", "Total_Rows", "Total_Columns", "Approximate_Grain", "Missing_Values_Total", "Duplicate_Rows"]].to_string())
