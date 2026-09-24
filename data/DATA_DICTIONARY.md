# FitLife Wellness Intelligence - Data Dictionary

This document serves as the comprehensive data dictionary for all 18 raw CSV datasets contained in the Fitabase smart-device dataset (`data/raw/fitabase.zip/Fitabase Data 4.12.16-5.12.16`).

---

## 1. Daily Level Datasets

### 1.1 `dailyActivity_merged.csv`
* **Purpose:** Core daily aggregate table combining daily steps, activity distance, intensity durations, and calorie burn per participant.
* **Grain:** One row per `Id` per `ActivityDate` (1 Participant + 1 Date = 1 Row).
* **Primary Key:** `(Id, ActivityDate)`
* **Date/Time Column:** `ActivityDate` (Format: `M/D/YYYY`)
* **Important Columns:**
  - `Id` (numeric ID, 10 digits)
  - `TotalSteps` (integer)
  - `TotalDistance`, `TrackerDistance`, `LoggedActivitiesDistance` (floats)
  - `VeryActiveDistance`, `ModeratelyActiveDistance`, `LightActiveDistance`, `SedentaryActiveDistance` (floats)
  - `VeryActiveMinutes`, `FairlyActiveMinutes`, `LightlyActiveMinutes`, `SedentaryMinutes` (integers)
  - `Calories` (integer)
* **Potential Relationships:** Parent fact table for daily analytical metrics. Matches `dailyCalories`, `dailyIntensities`, `dailySteps`.
* **Potential Duplicate Risks:** Zero duplicate rows detected in raw data.

### 1.2 `dailyCalories_merged.csv`
* **Purpose:** Daily total energy expenditure in kilocalories per participant.
* **Grain:** One row per `Id` per `ActivityDay`.
* **Primary Key:** `(Id, ActivityDay)`
* **Date/Time Column:** `ActivityDay`
* **Important Columns:** `Id`, `ActivityDay`, `Calories`
* **Potential Relationships:** Redundant subset of `dailyActivity_merged.csv`.

### 1.3 `dailyIntensities_merged.csv`
* **Purpose:** Daily minute counts and distances stratified by activity intensity zones.
* **Grain:** One row per `Id` per `ActivityDay`.
* **Primary Key:** `(Id, ActivityDay)`
* **Date/Time Column:** `ActivityDay`
* **Important Columns:** `SedentaryMinutes`, `LightlyActiveMinutes`, `FairlyActiveMinutes`, `VeryActiveMinutes`
* **Potential Relationships:** Redundant subset of `dailyActivity_merged.csv`.

### 1.4 `dailySteps_merged.csv`
* **Purpose:** Daily total step count recorded per participant.
* **Grain:** One row per `Id` per `ActivityDay`.
* **Primary Key:** `(Id, ActivityDay)`
* **Date/Time Column:** `ActivityDay`
* **Important Columns:** `Id`, `ActivityDay`, `StepTotal`
* **Potential Relationships:** Redundant subset of `dailyActivity_merged.csv`.

---

## 2. Sleep Datasets

### 2.1 `sleepDay_merged.csv`
* **Purpose:** Daily sleep monitoring records, including sleep sessions, actual minutes asleep, and total time spent in bed.
* **Grain:** One row per `Id` per `SleepDay`.
* **Primary Key:** `(Id, SleepDay)`
* **Date/Time Column:** `SleepDay` (Format: `M/D/YYYY 12:00:00 AM`)
* **Important Columns:**
  - `TotalSleepRecords` (integer - count of sleep logs in the day)
  - `TotalMinutesAsleep` (integer)
  - `TotalTimeInBed` (integer)
* **Derived Metrics:** `SleepEfficiency` = `(TotalMinutesAsleep / TotalTimeInBed) * 100`
* **Potential Duplicate Risks:** Contains **3 duplicate rows** in raw file that must be deduplicated.

### 2.2 `minuteSleep_merged.csv`
* **Purpose:** High-resolution minute-by-minute sleep state tracking (1 = asleep, 2 = restless, 3 = awake).
* **Grain:** One row per `Id` per `date` (minute timestamp).
* **Primary Key:** `(Id, date)`
* **Date/Time Column:** `date` (Format: `M/D/YYYY H:MM:SS AM/PM`)
* **Important Columns:** `value` (sleep state), `logId` (session identifier)
* **Potential Duplicate Risks:** Contains **543 duplicate rows** in raw file.

---

## 3. Weight & Body Composition Dataset

### 3.1 `weightLogInfo_merged.csv`
* **Purpose:** Body weight, BMI, and fat logs entered manually or via smart scale.
* **Grain:** One row per `Id` per `Date` timestamp.
* **Primary Key:** `(Id, Date)`
* **Date/Time Column:** `Date` (Format: `M/D/YYYY H:MM:SS AM/PM`)
* **Important Columns:**
  - `WeightKg`, `WeightPounds` (floats)
  - `BMI` (float)
  - `Fat` (float - contains 65 missing values out of 67 rows)
  - `IsManualReport` (boolean string)
  - `LogId` (numeric identifier)
* **Potential Duplicate Risks:** Only 8 participants logged weight. Extreme sparsity requires explicit handling (no dummy value invention).

---

## 4. Heart Rate Dataset

### 4.1 `heartrate_seconds_merged.csv`
* **Purpose:** Second-by-second optical heart rate sensor readings (BPM).
* **Grain:** One row per `Id` per `Time` (second).
* **Primary Key:** `(Id, Time)`
* **Date/Time Column:** `Time` (Format: `M/D/YYYY H:MM:SS AM/PM`)
* **Important Columns:** `Value` (Heart rate in beats per minute, integer).
* **Dimensions:** **2,483,658 records** across 14 active participants.
* **Aggregation Strategy:** Must be aggregated to daily metrics (`avg_heart_rate`, `min_heart_rate`, `max_heart_rate`, `reading_count`) and hourly metrics before joining with daily master tables.

---

## 5. Hourly Datasets

### 5.1 `hourlyCalories_merged.csv`
* **Purpose:** Total calories burned during each 60-minute window.
* **Grain:** One row per `Id` per `ActivityHour`.
* **Primary Key:** `(Id, ActivityHour)`

### 5.2 `hourlyIntensities_merged.csv`
* **Purpose:** Activity intensity totals and averages for each 60-minute window.
* **Grain:** One row per `Id` per `ActivityHour`.
* **Primary Key:** `(Id, ActivityHour)`

### 5.3 `hourlySteps_merged.csv`
* **Purpose:** Step counts accumulated in each 60-minute window.
* **Grain:** One row per `Id` per `ActivityHour`.
* **Primary Key:** `(Id, ActivityHour)`

---

## 6. Minute-Level Datasets (Narrow & Wide Format)

* `minuteCaloriesNarrow_merged.csv`, `minuteIntensitiesNarrow_merged.csv`, `minuteMETsNarrow_merged.csv`, `minuteStepsNarrow_merged.csv`
  - **Grain:** `Id` + `ActivityMinute` (1,325,580 rows per file).
* `minuteCaloriesWide_merged.csv`, `minuteIntensitiesWide_merged.csv`, `minuteStepsWide_merged.csv`
  - **Grain:** `Id` + `ActivityHour` with 60 minute columns (`00` to `59`).
