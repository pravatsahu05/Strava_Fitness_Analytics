# Phase 0: Project Audit Report
**Project Name:** FitLife Wellness Intelligence (Bellabeat Smart-Device Fitness Analytics)  
**Date:** September 23, 2026  
**Auditor:** Senior Technical Mentor & Lead Data Engineer  

---

## 1. Executive Summary & PPT Requirements Checklist

Based on the analyzed presentation (`STRAVA FITNESS APP.pptx` located in Downloads / local environment) and the uploaded Fitabase smart-device dataset:

* **Framing & Case Study Background:** The project implements the Bellabeat smart-device case study (Urška Sršen & Sando Mur). Bellabeat is a high-tech wellness company manufacturing health-focused smart products for women (e.g., Leaf, Time, Spring).
* **Business Objective:** Analyze consumer smart-device usage trends (activity, sleep, heart rate, hourly patterns) to uncover growth opportunities and formulate data-driven high-level marketing recommendations for Bellabeat.
* **Branding Strategy:** Neutral, professional product branding **FitLife Wellness Intelligence**, preserving Bellabeat case-study framing while referencing the Strava/Fitness analytics portfolio context in documentation.
* **Technical Scope:**
  - Full ETL pipeline (Ingestion, Inspection, Cleaning, Quality Scoring, Integration, Aggregation)
  - SQLite Relational Database (`database/fitness.db`) with normalized schemas and indexes
  - SQL validation and analytical query execution
  - Exploratory Data Analysis (EDA) notebooks and metric derivation
  - Interactive multi-page Streamlit web dashboard with Plotly visual analytics
  - Glassmorphic modern dark-navy UI with responsive sidebar filters
  - Export capabilities (CSV downloads of filtered data & query results)
  - Portfolio-ready documentation, tests, presentation & viva guides

---

## 2. Dataset Inventory & Inspection

The dataset was located in `data/raw/fitabase.zip/Fitabase Data 4.12.16-5.12.16`. Below is the complete empirical breakdown of all 18 raw CSV files discovered:

| Filename | Total Rows | Total Columns | Logical Key / Grain | Primary Metrics / Key Columns |
| :--- | :---: | :---: | :--- | :--- |
| **dailyActivity_merged.csv** | 940 | 15 | `Id` + `ActivityDate` | Steps, Distance, Active/Sedentary Minutes, Calories |
| **dailyCalories_merged.csv** | 940 | 3 | `Id` + `ActivityDay` | Calories |
| **dailyIntensities_merged.csv** | 940 | 10 | `Id` + `ActivityDay` | Very/Fairly/Lightly Active & Sedentary Mins/Distance |
| **dailySteps_merged.csv** | 940 | 3 | `Id` + `ActivityDay` | StepTotal |
| **sleepDay_merged.csv** | 413 | 5 | `Id` + `SleepDay` | TotalMinutesAsleep, TotalTimeInBed, TotalSleepRecords |
| **weightLogInfo_merged.csv** | 67 | 8 | `Id` + `Date` | WeightKg, WeightPounds, Fat, BMI, IsManualReport |
| **heartrate_seconds_merged.csv** | 2,483,658 | 3 | `Id` + `Time` (Second) | Heart Rate (Value in BPM) |
| **hourlyCalories_merged.csv** | 22,099 | 3 | `Id` + `ActivityHour` | Hourly Calories |
| **hourlyIntensities_merged.csv** | 22,099 | 4 | `Id` + `ActivityHour` | TotalIntensity, AverageIntensity |
| **hourlySteps_merged.csv** | 22,099 | 3 | `Id` + `ActivityHour` | Hourly Step Total |
| **minuteCaloriesNarrow_merged.csv** | 1,325,580 | 3 | `Id` + `ActivityMinute` | Minute Calories |
| **minuteCaloriesWide_merged.csv** | 21,645 | 62 | `Id` + `ActivityHour` | 60 minute columns (Calories00..59) |
| **minuteIntensitiesNarrow_merged.csv** | 1,325,580 | 3 | `Id` + `ActivityMinute` | Minute Intensity (0-3) |
| **minuteIntensitiesWide_merged.csv** | 21,645 | 62 | `Id` + `ActivityHour` | 60 minute columns (Intensity00..59) |
| **minuteMETsNarrow_merged.csv** | 1,325,580 | 3 | `Id` + `ActivityMinute` | METs |
| **minuteSleep_merged.csv** | 188,521 | 4 | `Id` + `date` (Minute) | Sleep state value, logId |
| **minuteStepsNarrow_merged.csv** | 1,325,580 | 3 | `Id` + `ActivityMinute` | Minute Steps |
| **minuteStepsWide_merged.csv** | 21,645 | 62 | `Id` + `ActivityHour` | 60 minute columns (Steps00..59) |

---

## 3. Dataset Grain & Duplicate Risk Analysis

Merging raw datasets without grain alignment creates **row multiplication fan-out defects**:
1. **Daily Master Table Grain:** Exactly **1 Row per Participant (`participant_id`) per Date (`date`)**.
2. **Fan-Out Prevention:** `dailyActivity`, `dailyCalories`, `dailyIntensities`, and `dailySteps` share the same daily grain (940 rows across 33 participants). However, `sleepDay` only covers 24 participants across 413 participant-days, and `weightLogInfo` covers only 8 participants across 67 logs.
3. **High-Frequency Aggregation:** `heartrate_seconds` (2.48 million rows) and minute-level data MUST be aggregated to daily (`participant_id`, `date`) and hourly (`participant_id`, `date`, `hour`) summary tables *before* joining into analytical tables.

---

## 4. Current Workspace Audit

* **Existing Datasets:** Found raw dataset in `data/raw/fitabase.zip/Fitabase Data 4.12.16-5.12.16`.
* **Existing Project Code:** None yet (Clean slate).
* **Missing Components to Build:**
  - Project configuration & virtual environment setup (`requirements.txt`, `.gitignore`, `.env.example`)
  - Automated dataset inventory script (`src/etl/data_inventory.py`) & dictionary (`data/DATA_DICTIONARY.md`)
  - Robust data cleaning module (`src/etl/data_cleaning.py`) & report generation
  - Data grain documentation (`data/DATA_GRAIN_DOCUMENTATION.md`)
  - Daily & Hourly Master Integration ETL (`src/etl/build_master_dataset.py`, `src/etl/build_hr_daily.py`)
  - SQLite database initializer (`database/fitness.db`, `sql/schema.sql`)
  - SQL validation & analytical query suites (`sql/*.sql`)
  - Exploratory Data Analysis notebooks (`notebooks/01_..04_.ipynb`)
  - Analytics & Visual engine (`src/analytics/`, `src/visualization/`)
  - Streamlit multi-page web application (`app.py`, `pages/1_..7_.py`, `assets/style.css`)
  - Automated unit test suite (`tests/`)
  - Documentation, Viva guide, Demo scripts (`README.md`, `VIVA_QUESTIONS.md`, `PRESENTATION_SCRIPT.md`)

---

## 5. Recommended 22-Phase Implementation Roadmap

1. **Phase 0:** Project Audit (Completed)
2. **Phase 1:** Environment & Virtualenv Setup
3. **Phase 2:** Automated Dataset Inventory & Dictionary
4. **Phase 3:** Data Cleaning Engine & Quality Report
5. **Phase 4:** Data Grain & Architectural Mapping
6. **Phase 5:** Daily Master Integration (`daily_master.csv`)
7. **Phase 6:** Heart Rate, Hourly & Minute Level Aggregations
8. **Phase 7:** SQLite Relational Database Creation
9. **Phase 8:** SQL Cleaning & Data Quality Validation
10. **Phase 9:** SQL Business Analytics Query Suite
11. **Phase 10:** Exploratory Data Analysis (EDA Notebooks)
12. **Phase 11:** Analytics Metrics Module
13. **Phase 12:** Interactive Plotly Charting Engine
14. **Phase 13:** Streamlit Core App & Shared Utilities
15. **Phase 14:** Modern Dark-Navy Glassmorphism CSS Theme
16. **Phase 15:** Dashboard Pages (Executive, Activity, Sleep, Heart Rate, Hourly, Explorer, SQL, Quality)
17. **Phase 16:** Dynamic Business Insights & Marketing Recommendations
18. **Phase 17:** Test Suite Execution (`pytest`)
19. **Phase 18:** Comprehensive Documentation & Readme
20. **Phase 19:** GitHub Repository Readiness
21. **Phase 20:** Streamlit Deployment Preparation
22. **Phase 21:** Presentation, Viva & Demo Scripts
