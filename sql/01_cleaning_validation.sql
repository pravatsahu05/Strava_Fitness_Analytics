-- 01_cleaning_validation.sql
-- Data Cleaning & Schema Validation Queries for SQLite database (fitness.db)

-- 1. Duplicate Detection Check on daily_master
SELECT participant_id, date, COUNT(*) AS duplicate_count
FROM daily_master
GROUP BY participant_id, date
HAVING COUNT(*) > 1;

-- 2. Missing Values Audit across Daily Master Metrics
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN participant_id IS NULL THEN 1 ELSE 0 END) AS missing_participant_id,
    SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) AS missing_date,
    SUM(CASE WHEN total_steps IS NULL THEN 1 ELSE 0 END) AS missing_steps,
    SUM(CASE WHEN calories IS NULL THEN 1 ELSE 0 END) AS missing_calories,
    SUM(CASE WHEN weight IS NULL THEN 1 ELSE 0 END) AS missing_weight,
    SUM(CASE WHEN avg_heart_rate IS NULL THEN 1 ELSE 0 END) AS missing_heart_rate
FROM daily_master;

-- 3. Invalid Numeric Values Detection (Negative Values)
SELECT *
FROM daily_master
WHERE total_steps < 0 
   OR calories < 0 
   OR total_distance < 0 
   OR sedentary_minutes < 0 
   OR very_active_minutes < 0;

-- 4. Date Range & Span Audit
SELECT 
    MIN(date) AS start_date,
    MAX(date) AS end_date,
    COUNT(DISTINCT date) AS total_distinct_days
FROM daily_master;

-- 5. Participant Coverage & Activity Log Counts
SELECT 
    participant_id,
    COUNT(date) AS total_days_logged,
    MIN(date) AS first_logged_date,
    MAX(date) AS last_logged_date
FROM daily_master
GROUP BY participant_id
ORDER BY total_days_logged DESC;

-- 6. Daily Completeness Summary (Non-Zero Sensor Days)
SELECT 
    COUNT(*) AS total_records,
    SUM(CASE WHEN total_steps > 0 THEN 1 ELSE 0 END) AS active_wear_days,
    SUM(CASE WHEN total_steps = 0 AND total_distance = 0 THEN 1 ELSE 0 END) AS zero_activity_days,
    ROUND(SUM(CASE WHEN total_steps > 0 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS wear_compliance_pct
FROM daily_master;
