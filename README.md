# ⚡ FitLife Wellness Intelligence — Smart-Device Fitness Analytics Platform

> **Portfolio Case Study Project:** Bellabeat Smart-Device Consumer Fitness Analytics  
> **Built with:** Python 3.10+, Pandas, NumPy, Plotly, SQLite, Streamlit, Glassmorphic CSS, Pytest  
> **Developer & Data Analyst:** Pravat (BCA Senior Project Portfolio)  

---

## 📖 Executive Summary & Project Overview

**FitLife Wellness Intelligence** is an end-to-end data engineering, analytics, and interactive web application built on consumer smart-device data from the **Fitabase dataset** (Bellabeat Case Study).

### 🎯 Business Objective & Context
Bellabeat co-founders **Urška Sršen** and **Sando Mur** developed health-focused smart hardware for women (e.g., Leaf, Time, Ivy). This project analyzes consumer fitness tracker usage patterns (daily steps, calorie expenditure, active/sedentary intensity duration, sleep efficiency, and second-by-second optical heart rate) to discover growth opportunities and formulate high-level strategic marketing recommendations for executive leadership.

---

## 🏗️ System Architecture & Data Flow

```text
                               FITABASE RAW DATA
                                       │
                                       ▼
                            1. DATA INVENTORY AUDIT
                             (src/etl/data_inventory.py)
                                       │
                                       ▼
                            2. DATA CLEANING ENGINE
                             (src/etl/data_cleaning.py)
                                       │
             ┌─────────────────────────┼─────────────────────────┐
             ▼                         ▼                         ▼
     Daily Activity Data       Daily Sleep Data          Heart Rate Seconds (2.48M)
             │                         │                         │
             │                         │              (src/etl/build_hr_daily.py)
             │                         │                         │
             └─────────────────────────┼─────────────────────────┘
                                       ▼
                         3. MASTER DATASET INTEGRATION
                          (src/etl/build_master_dataset.py)
                                       │
                    ┌──────────────────┴──────────────────┐
                    ▼                                     ▼
      data/processed/daily_master.csv       data/processed/hourly_master.csv
        (1 Participant + 1 Date = 1 Row)       (Participant + Date + Hour)
                    │                                     │
                    └──────────────────┬──────────────────┘
                                       ▼
                            4. RELATIONAL SQLITE DB
                             (database/fitness.db)
                                       │
             ┌─────────────────────────┼─────────────────────────┐
             ▼                         ▼                         ▼
      SQL Query Engine         Analytics Engine          Plotly Charts
   (sql/analysis_queries.sql) (src/analytics/metrics.py) (src/visualization/)
             │                         │                         │
             └─────────────────────────┼─────────────────────────┘
                                       ▼
                        5. STREAMLIT MULTI-PAGE WEB APP
                                   (app.py)
                                       │
      ┌────────────────────────────────┼────────────────────────────────┐
      ▼                                ▼                                ▼
🏠 Executive Dashboard        📊 Interactive Dashboards       💡 Business Recommendations
```

---

## 🛠️ Technology Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Programming** | Python 3.10+ | Core ETL logic, data processing, and application backend |
| **Data Engineering** | Pandas, NumPy | Data cleaning, type parsing, chunk aggregation, deduplication |
| **Relational Database** | SQLite, sqlite3 / SQLAlchemy | Embedded SQL database storage (`fitness.db`) and query execution |
| **Visualization** | Plotly Express & Graph Objects | Glassmorphic interactive charts (hover, zoom, pan, legend toggles) |
| **Web Application** | Streamlit | Multi-page web app framework and dashboard layout |
| **Custom Styling** | Vanilla CSS (`assets/style.css`) | Modern dark-navy glassmorphism UI design system |
| **Testing** | Pytest | Automated unit & integration testing suite |

---

## 📁 Required Project Structure

```text
Strava_Fitness_Analytics/
│
├── app.py                      # Main Streamlit application entry point (Executive Dashboard)
├── app_utils.py                # Cached data loaders, CSS injection & sidebar filters
├── requirements.txt            # Python dependencies
├── README.md                   # Complete project documentation
├── PROJECT_AUDIT.md            # Phase 0 Audit report
├── .gitignore                  # Git exclusion rules (venv, db, raw datasets)
├── .env.example                # Environment variables template
│
├── data/
│   ├── README.md               # Data directory guide
│   ├── DATA_DICTIONARY.md      # Data dictionary for all 18 CSV datasets
│   ├── DATA_CLEANING_DOCUMENTATION.md # Technical cleaning report
│   ├── DATA_GRAIN_DOCUMENTATION.md    # Grain mapping & join protection rules
│   │
│   ├── raw/
│   │   └── fitabase.zip/Fitabase Data 4.12.16-5.12.16/  # 18 raw Fitabase CSV files
│   │
│   └── processed/
│       ├── daily_master.csv    # Integrated daily fact table (1 Participant + 1 Date = 1 Row)
│       ├── hourly_master.csv   # Hourly activity table (Participant + Date + Hour)
│       ├── daily_activity.csv  # Cleansed daily activity
│       ├── sleep_day.csv       # Cleansed daily sleep
│       ├── weight_log.csv      # Cleansed weight records
│       └── heart_rate_daily.csv# Aggregated daily heart rate metrics
│
├── database/
│   └── fitness.db              # SQLite relational database containing 6 indexed tables
│
├── sql/
│   ├── schema.sql              # DDL schema definition with primary keys & indexes
│   ├── 01_cleaning_validation.sql # SQL duplicate & null audit queries
│   ├── 02_quality_analysis.sql # Table coverage & dataset health queries
│   ├── 03_activity_analysis.sql# Activity & step tier queries
│   ├── 04_sleep_analysis.sql   # Sleep duration & efficiency queries
│   ├── 05_heart_rate_analysis.sql # Cardio BPM profile queries
│   ├── 06_hourly_analysis.sql  # Hourly dynamics & peak hour queries
│   └── analysis_queries.sql    # 18 Master Business Analytics queries
│
├── src/
│   ├── __init__.py
│   │
│   ├── etl/                    # Extraction, Transformation & Loading
│   │   ├── __init__.py
│   │   ├── config.py           # Centralized base paths & setup
│   │   ├── utils.py            # Logging & file helpers
│   │   ├── data_inventory.py   # Automated raw dataset metadata scanner
│   │   ├── data_cleaning.py    # Reusable data cleaning pipeline
│   │   ├── build_hr_daily.py   # Chunk-based 2.48M heart-rate aggregator
│   │   ├── build_master_dataset.py # Daily & hourly master dataset integrator
│   │   └── run_pipeline.py     # Master end-to-end pipeline runner
│   │
│   ├── analytics/              # Analytics & Engine Modules
│   │   ├── __init__.py
│   │   ├── metrics.py          # Executive KPIs & user segmentation engine
│   │   ├── sql_runner.py       # Safe read-only SQL query runner
│   │   ├── insights.py         # Dynamic business insights generator
│   │   └── validation.py       # Schema & non-emptiness validator
│   │
│   └── visualization/          # Plotly Charting Engine
│       ├── __init__.py
│       ├── theme.py            # Custom dark-navy layout template & color palette
│       └── charts.py           # 26 Plotly interactive chart functions
│
├── pages/                      # Multi-Page Navigation Suite
│   ├── 1_SQL_Analysis.py       # SQL Query Playground & Preset Runner
│   ├── 2_Data_Quality.py       # Data Quality Dashboard & Composite Score
│   ├── 3_Activity_Analytics.py # Physical Activity & Movement Dashboard
│   ├── 4_Sleep_Wellness.py     # Sleep Duration & Efficiency Dashboard
│   ├── 5_Heart_Rate.py         # Optical Heart Rate & Cardio Dashboard
│   ├── 6_Hourly_Behavior.py    # Hourly Step Dynamics & Activity Heatmap
│   ├── 7_Participant_Explorer.py # Individual Participant Profile Deep-Dive
│   └── 8_Business_Insights.py  # Strategic Marketing Recommendations & CSV Export
│
├── assets/
│   └── style.css               # Glassmorphism modern dark-navy CSS theme
│
├── notebooks/                  # Exploratory Analysis Jupyter Notebooks
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda.ipynb
│   └── 04_insights.ipynb
│
├── outputs/                    # Exported Reports & Summaries
│   ├── data_inventory.csv
│   ├── data_cleaning_report.csv
│   └── data_quality_summary.csv
│
└── tests/                      # Pytest Automated Test Suite
    ├── test_cleaning.py
    ├── test_metrics.py
    └── test_pipeline.py
```

---

## ⚡ Quick Start & Installation Guide

### 1. Environment Setup & Virtualenv
Open your terminal in the project root directory:

```powershell
# Create Python Virtual Environment
python -m venv venv

# Activate Virtual Environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Upgrade Pip & Install Required Packages
pip install -r requirements.txt
```

### 2. Execute Complete ETL Pipeline & Database Build
Run the master end-to-end pipeline script to clean datasets, aggregate heart-rate records, build master CSVs, and populate SQLite database:

```powershell
python src/etl/run_pipeline.py
python src/analytics/sql_runner.py
```

### 3. Run Automated Pytest Test Suite
Verify that all unit and integration tests pass:

```powershell
pytest -v
```

### 4. Launch Streamlit Web Application
Start the multi-page interactive web application:

```powershell
streamlit run app.py
```

The web application will open automatically at **`http://localhost:8501`**.

---

## 📊 Dashboard Pages & Application Features

1. **🏠 Executive Dashboard (`app.py`):** Executive KPI cards (Users, Avg Steps, Calories, Active Mins, Sedentary Hrs, Sleep), daily step/calorie trends, activity intensity donuts, and sleep overview.
2. **🧮 SQL Analysis Page (`pages/1_SQL_Analysis.py`):** Predefined query presets, read-only SQL query editor, safety AST filters, and query result CSV export.
3. **🧹 Data Quality Page (`pages/2_Data_Quality.py`):** Composite Data Quality Score (99.79/100), missing value distribution charts, participant compliance logs, and cleaning audit logs.
4. **📊 Activity Analytics Page (`pages/3_Activity_Analytics.py`):** Step distributions, calories vs steps scatter plots, weekday step comparisons, and CDC user segmentations.
5. **😴 Sleep & Wellness Page (`pages/4_Sleep_Wellness.py`):** Sleep duration histograms, sleep efficiency by weekday, and sleep vs sedentary time scatter plots.
6. **❤️ Heart Rate Page (`pages/5_Heart_Rate.py`):** Second-level optical BPM trends, heart rate histograms, resting/peak BPM boxplots, and medical disclaimers.
7. **⏰ Hourly Behavior Page (`pages/6_Hourly_Behavior.py`):** Hourly step dynamics, calorie expenditure, and Weekday × Hour activity heatmaps.
8. **👤 Participant Explorer (`pages/7_Participant_Explorer.py`):** Dropdown selector to deep-dive into individual participant profiles, daily trends, and sleep/cardio charts.
9. **💡 Business Insights Page (`pages/8_Business_Insights.py`):** Categorized strategic marketing recommendations for Bellabeat leadership with CSV report export.

---

## 💡 Key Analytical Findings & Business Recommendations

1. **Activity Slumps & Sunday Recovery:** Step volume peaks on **Tuesdays (8,319 steps)** and drops on **Sundays (6,500 steps)**. Only 21.2% of participant-days achieve the recommended 10,000 steps.
   * *Recommendation:* Launch Bellabeat app **"Weekend Warrior"** gamified challenges with gentle Sunday movement push notifications.
2. **High Sedentary Duration:** Sedentary behavior accounts for **81.3% of total tracked daily time** (16.5 hours/day).
   * *Recommendation:* Introduce Bellabeat **Haptic Move Reminders** vibrating gently after 50 minutes of continuous desk sitting to encourage short micro-walks.
3. **Overnight Wear Compliance:** Monitored sleep averages 6.99 hours with 91.6% efficiency, but 27% of users do not wear smartwatches to bed.
   * *Recommendation:* Position Bellabeat's lightweight jewelry line (**Leaf & Ivy**) as ultra-comfortable, non-intrusive 24/7 sleep and cycle trackers.
4. **Peak Diurnal Window:** Peak physical activity occurs between **5:00 PM and 7:00 PM** (averaging 563 steps/hour).
   * *Recommendation:* Schedule Bellabeat hydration alerts and workout marketing campaigns around 4:30 PM daily.

---

## 🔒 Security & Data Privacy Practices

* **Raw Data Exclusion:** Raw Fitabase CSV datasets are excluded from Git via `.gitignore` to prevent repository bloat and respect dataset distribution terms.
* **Safe Read-Only SQL Engine:** The SQL query runner regex-audits all input SQL queries, permitting ONLY `SELECT` or `WITH` queries and strictly blocking destructive statements (`DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `CREATE`).

---

## 📜 License & Credits

* **Case Study Framework:** Bellabeat Smart-Device Consumer Case Study (Urška Sršen & Sando Mur).
* **Dataset:** Fitabase Public Smart-Device Fitness Dataset (33 Participants).
* **Developed By:** Pravat (BCA Senior Data Analytics Portfolio Project, 2026).
