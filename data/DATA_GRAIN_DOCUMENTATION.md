# FitLife Wellness Intelligence - Data Grain & Architectural Mapping

This document provides mandatory architectural guidelines on **dataset grain, relational joins, and prevention of row-multiplication (fan-out) defects** before building the integrated analytical master tables and SQLite database.

---

## 1. What Is Dataset Grain?

**Grain** defines what a single row in a table represents in the real world.

For example:
* **Daily Activity Grain:** 1 Row = 1 Participant on 1 Calendar Date.
* **Hourly Steps Grain:** 1 Row = 1 Participant on 1 Calendar Date during 1 Specific Hour (0–23).
* **Heart Rate Grain:** 1 Row = 1 Participant reading at 1 Exact Second.

---

## 2. Why Direct Merging Across Incompatible Grains Is Dangerous

Merging two datasets with different grains using a standard `JOIN` or `pd.merge()` without prior aggregation causes a severe database flaw called the **Fan-Out Defect (Row Multiplication)**.

### Example Scenario of Fan-Out Defect:
Suppose Participant `1503960366` has:
* **1 Daily Activity row** on `2016-04-12` (Total Steps = 13,162).
* **1,500 Heart Rate rows** recorded every few seconds on `2016-04-12`.

If you execute a direct join on `participant_id` + `date`:
```sql
-- INCORRECT MERGE (Causes Row Multiplication)
SELECT a.participant_id, a.date, a.total_steps, h.value AS heart_rate
FROM daily_activity a
JOIN heartrate_seconds h 
  ON a.participant_id = h.participant_id AND a.date = DATE(h.time);
```

### The Flaw:
The single daily row will be duplicated **1,500 times**!
If you subsequently query `SUM(total_steps)`, the step count will be multiplied by 1,500 ➔ calculating **19.7 Million steps** for a single day instead of 13,162 steps!

---

## 3. How Aggregation Prevents Duplication

To safely integrate datasets with lower-level grains (second, minute, hourly) into daily analytics, the high-frequency dataset MUST be aggregated to the target grain **first**.

### Correct Aggregation Workflow:
```text
RAW HEART RATE (2.48 Million Rows @ Second Grain)
                       │
                       ▼ Aggregate by (participant_id, date)
DAILY HEART RATE (940 Rows @ Daily Grain)
  - avg_heart_rate
  - min_heart_rate
  - max_heart_rate
  - heart_rate_readings
                       │
                       ▼ Safe 1-to-1 Join
DAILY MASTER TABLE (1 Participant + 1 Date = 1 Row)
```

---

## 4. Complete Grain Mapping Reference

| Table Name | Raw/Processed | Exact Logical Grain | Primary Key / Composite Key | Rows | Safe Integration Strategy |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `daily_activity` | Processed | Participant + Date | `(participant_id, date)` | 940 | Base Fact Table |
| `sleep_day` | Processed | Participant + Date | `(participant_id, date)` | 410 | LEFT JOIN on `(participant_id, date)` |
| `weight_log` | Processed | Participant + Date/Time | `(participant_id, datetime)` | 67 | Aggregate to daily mean before joining |
| `heartrate_daily` | Aggregated | Participant + Date | `(participant_id, date)` | 334 | Aggregate BPM (mean, min, max, count) before joining |
| `hourly_master` | Aggregated | Participant + Date + Hour | `(participant_id, date, hour)` | 22,099 | Powered separate hourly dashboard pages |
| `daily_master` | Final Fact | **Participant + Date** | `(participant_id, date)` | **940** | **Enforce Strict Uniqueness Constraint** |

---

## 5. Uniqueness Validation Rule for `daily_master`

Before any master analytical table is saved or loaded into SQLite, the system MUST execute the following uniqueness validation check:

```sql
SELECT participant_id, date, COUNT(*) AS row_count
FROM daily_master
GROUP BY participant_id, date
HAVING COUNT(*) > 1;
```

**Mandatory Rule:** This query **MUST return 0 rows**. If any composite key `(participant_id, date)` returns a `row_count > 1`, the pipeline will raise a data integrity error and halt execution immediately.
