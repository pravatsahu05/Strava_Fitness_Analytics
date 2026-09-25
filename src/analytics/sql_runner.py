"""
SQL Runner & Database Engine Module
Manages SQLite database creation (database/fitness.db), schema execution (sql/schema.sql),
data ingestion from processed CSVs, and safe read-only SQL query execution.
"""

import sys
import sqlite3
import re
from pathlib import Path
import pandas as pd

# Add src to python path for standalone execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.etl.config import BASE_DIR, DATABASE_PATH, PROCESSED_DATA_DIR
from src.etl.utils import logger, safe_read_csv

SCHEMA_SQL_PATH = BASE_DIR / "sql" / "schema.sql"


def get_db_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(db_path: Path = DATABASE_PATH, schema_path: Path = SCHEMA_SQL_PATH) -> bool:
    """Execute schema DDL file to create database tables and indexes."""
    if not schema_path.exists():
        logger.error(f"Schema SQL file not found at {schema_path}")
        return False

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_ddl = f.read()

    conn = get_db_connection(db_path)
    try:
        conn.executescript(schema_ddl)
        conn.commit()
        logger.info(f"Database schema initialized successfully at {db_path.name}.")
        return True
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        return False
    finally:
        conn.close()


def populate_database_tables(db_path: Path = DATABASE_PATH, processed_dir: Path = PROCESSED_DATA_DIR):
    """Load cleaned CSV datasets from data/processed/ into SQLite database tables."""
    initialize_database(db_path)

    conn = get_db_connection(db_path)

    table_mappings = {
        "daily_master": processed_dir / "daily_master.csv",
        "daily_activity": processed_dir / "daily_activity.csv",
        "sleep_daily": processed_dir / "sleep_day.csv",
        "weight_daily": processed_dir / "weight_log.csv",
        "heart_rate_daily": processed_dir / "heart_rate_daily.csv",
        "hourly_master": processed_dir / "hourly_master.csv"
    }

    for table_name, csv_path in table_mappings.items():
        if not csv_path.exists():
            logger.warning(f"CSV for table {table_name} missing at {csv_path}")
            continue

        df = safe_read_csv(csv_path)
        if df.empty:
            continue

        # Write data replacing existing table contents
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        logger.info(f"Populated table '{table_name}' with {len(df):,} records.")

    conn.close()
    logger.info("Database population complete.")


def is_safe_read_only_query(query: str) -> tuple[bool, str]:
    """
    Validate that a SQL query contains ONLY safe read-only SELECT or WITH statements.
    Rejects DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, REPLACE.
    """
    clean_query = query.strip()
    
    # Remove single-line and multi-line comments
    clean_query = re.sub(r'--.*$', '', clean_query, flags=re.MULTILINE)
    clean_query = re.sub(r'/\*.*?\*/', '', clean_query, flags=re.DOTALL).strip()

    forbidden_keywords = [
        r'\bDROP\b', r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b',
        r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bREPLACE\b', r'\bEXEC\b'
    ]

    for pattern in forbidden_keywords:
        if re.search(pattern, clean_query, re.IGNORECASE):
            match_kw = re.search(pattern, clean_query, re.IGNORECASE).group(0)
            return False, f"Unsafe SQL Operation Detected: '{match_kw.upper()}'. Only SELECT statements are permitted."

    if not (clean_query.upper().startswith("SELECT") or clean_query.upper().startswith("WITH") or clean_query.upper().startswith("EXPLAIN")):
        return False, "Query must begin with SELECT or WITH."

    return True, "Safe"


def run_sql_query(query: str, db_path: Path = DATABASE_PATH) -> tuple[pd.DataFrame, str]:
    """
    Execute a read-only SQL query against the SQLite database and return a tuple of (df, error_message).
    """
    is_safe, msg = is_safe_read_only_query(query)
    if not is_safe:
        return pd.DataFrame(), msg

    if not db_path.exists():
        if (PROCESSED_DATA_DIR / "daily_master.csv").exists():
            populate_database_tables(db_path)
        else:
            return pd.DataFrame(), f"Database not found at {db_path}. Please run src/etl/run_pipeline.py first."

    conn = get_db_connection(db_path)
    try:
        df = pd.read_sql_query(query, conn)
        return df, ""
    except Exception as e:
        return pd.DataFrame(), f"SQL Execution Error: {str(e)}"
    finally:
        conn.close()


if __name__ == "__main__":
    populate_database_tables()
    df_test, err = run_sql_query("SELECT COUNT(*) AS total_records, COUNT(DISTINCT participant_id) AS total_users FROM daily_master;")
    if err:
        print(f"Error: {err}")
    else:
        print("\nDatabase Execution Test Result:")
        print(df_test.to_string(index=False))
