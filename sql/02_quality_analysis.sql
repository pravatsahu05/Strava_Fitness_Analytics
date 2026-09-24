-- 02_quality_analysis.sql
-- Data Quality Metrics & Table Coverage Statistics

-- 1. Table Row Counts & Participant Coverage Overview
SELECT 'daily_master' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT participant_id) AS distinct_participants FROM daily_master
UNION ALL
SELECT 'daily_activity' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT participant_id) AS distinct_participants FROM daily_activity
UNION ALL
SELECT 'sleep_daily' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT participant_id) AS distinct_participants FROM sleep_daily
UNION ALL
SELECT 'weight_daily' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT participant_id) AS distinct_participants FROM weight_daily
UNION ALL
SELECT 'heart_rate_daily' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT participant_id) AS distinct_participants FROM heart_rate_daily
UNION ALL
SELECT 'hourly_master' AS table_name, COUNT(*) AS row_count, COUNT(DISTINCT participant_id) AS distinct_participants FROM hourly_master;

-- 2. Data Availability Matrix Across Key Wellness Domains
SELECT 
    COUNT(*) AS total_daily_records,
    SUM(CASE WHEN sleep_minutes > 0 THEN 1 ELSE 0 END) AS sleep_records_count,
    ROUND(SUM(CASE WHEN sleep_minutes > 0 THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS sleep_coverage_pct,
    SUM(CASE WHEN avg_heart_rate IS NOT NULL THEN 1 ELSE 0 END) AS heart_rate_records_count,
    ROUND(SUM(CASE WHEN avg_heart_rate IS NOT NULL THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS hr_coverage_pct,
    SUM(CASE WHEN weight IS NOT NULL THEN 1 ELSE 0 END) AS weight_records_count,
    ROUND(SUM(CASE WHEN weight IS NOT NULL THEN 1.0 ELSE 0.0 END) / COUNT(*) * 100, 2) AS weight_coverage_pct
FROM daily_master;
