# FitLife Wellness Intelligence - Data Cleaning & Quality Documentation

This document records all data cleaning transformations, quality checks, deduplication strategies, outlier flagging rules, and date standardizations applied during **Phase 3 Data Cleaning**.

---

## 1. Executive Summary & Retention Metrics

* **Total Raw Rows Processed:** 1,420
* **Total Rows Retained:** 1,417
* **Data Retention Rate:** **99.79%**
* **Total Duplicates Removed:** 3
* **Total Invalid Values Corrected:** 0
* **Total Missing Values Analyzed:** 65 (concentrated in `weight_log` fat percentage column)
* **Outliers Flagged (IQR Rule):** 1 extreme step day (36,019 steps) flagged without deletion.

---

## 2. Dataset-by-Dataset Cleaning Summary

### 2.1 Daily Activity Dataset (`dailyActivity_merged.csv`)
* **Before Cleaning:** 940 rows, 15 columns
* **After Cleaning:** 940 rows, 20 columns (includes derived flags & weekday metrics)
* **Column Name Transformations:**
  - `Id` ➔ `participant_id`
  - `ActivityDate` ➔ `date`
  - All other columns standardized from PascalCase to clean `snake_case` (e.g., `TotalSteps` ➔ `total_steps`, `VeryActiveMinutes` ➔ `very_active_minutes`).
* **Date Transformations:** Parsed string date formats (`4/12/2016`) into standard ISO format (`2016-04-12`). Added `weekday` and `weekday_num`.
* **Duplicates Removed:** 0 rows.
* **Missing Values:** 0 null values.
* **Invalid Value Detection:** No negative values found. Verified numeric non-negativity across steps, distances, active minutes, and calories.
* **Zero Activity Flag:** Identified 77 participant-day records where `total_steps` == 0 and `total_distance` == 0 (sensor non-wear days). Preserved and flagged via `is_zero_activity = True`.
* **Outlier Strategy:** Computed 3×IQR bounds for `total_steps` and `calories`. 1 day (>36,000 steps) was flagged as an extreme valid activity day (`steps_outlier_flag = True`). No rows were deleted.

---

### 2.2 Sleep Dataset (`sleepDay_merged.csv`)
* **Before Cleaning:** 413 rows, 5 columns
* **After Cleaning:** 410 rows, 7 columns
* **Column Name Transformations:**
  - `Id` ➔ `participant_id`
  - `SleepDay` ➔ `date`
  - `TotalSleepRecords` ➔ `total_sleep_records`
  - `TotalMinutesAsleep` ➔ `total_minutes_asleep`
  - `TotalTimeInBed` ➔ `total_time_in_bed`
* **Date Transformations:** Converted timestamp strings (`4/12/2016 12:00:00 AM`) to clean ISO date format (`2016-04-12`).
* **Duplicates Removed:** **3 duplicate rows** removed based on unique key `(participant_id, date)`.
* **Missing Values:** 0 null values.
* **Derived Quality Metrics:**
  - `sleep_efficiency` = `(total_minutes_asleep / total_time_in_bed) * 100` (%)
  - `sleep_hours` = `total_minutes_asleep / 60.0` (hours)

---

### 2.3 Weight Log Dataset (`weightLogInfo_merged.csv`)
* **Before Cleaning:** 67 rows, 8 columns
* **After Cleaning:** 67 rows, 9 columns
* **Column Name Transformations:** Standardized to `participant_id`, `date`, `datetime`, `weight_kg`, `weight_pounds`, `fat`, `bmi`, `is_manual_report`, `log_id`.
* **Date Transformations:** Formatted `Date` to `datetime` (`YYYY-MM-DD HH:MM:SS`) and `date` (`YYYY-MM-DD`).
* **Duplicates Removed:** 0 rows.
* **Missing Value Analysis:** 65 missing values in `fat` column (97% missingness).
  - *Strategy:* The missing values reflect user opt-out on smart-scale body fat measurement. In accordance with data integrity guidelines, missing values were preserved as NaN and documented rather than imputed with dummy figures.

---

## 3. Data Cleaning Verification Matrix

| Metric | Daily Activity | Sleep Daily | Weight Log | Total / Combined |
| :--- | :---: | :---: | :---: | :---: |
| **Raw Input Rows** | 940 | 413 | 67 | **1,420** |
| **Clean Output Rows** | 940 | 410 | 67 | **1,417** |
| **Duplicates Removed** | 0 | 3 | 0 | **3** |
| **Missing Values** | 0 | 0 | 65 | **65** |
| **Invalid Values Fixed** | 0 | 0 | 0 | **0** |
| **Outliers Flagged** | 1 | 0 | 0 | **1** |
| **Zero-Activity Days** | 77 | 0 | 0 | **77** |
| **Retention Rate** | 100.0% | 99.27% | 100.0% | **99.79%** |

---

## 4. Generated Artifact Files
* Processed Dataset Files:
  - `data/processed/daily_activity.csv`
  - `data/processed/sleep_day.csv`
  - `data/processed/weight_log.csv`
* Cleaning & Quality Reports:
  - `outputs/data_cleaning_report.csv`
  - `outputs/data_quality_summary.csv`
