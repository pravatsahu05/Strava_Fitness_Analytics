-- 04_sleep_analysis.sql
-- Sleep Duration, Efficiency & Wellness Correlation Queries

-- 1. Overall Sleep & Bed Duration Averages
SELECT 
    COUNT(*) AS total_sleep_days,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep_hours,
    ROUND(AVG(sleep_minutes), 0) AS avg_sleep_minutes,
    ROUND(AVG(sleep_efficiency), 2) AS avg_sleep_efficiency_pct
FROM daily_master
WHERE sleep_minutes > 0;

-- 2. Sleep Duration and Efficiency by Weekday
SELECT 
    weekday,
    weekday_num,
    COUNT(*) AS sleep_log_count,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep_hours,
    ROUND(AVG(sleep_efficiency), 2) AS avg_sleep_efficiency_pct
FROM daily_master
WHERE sleep_minutes > 0
GROUP BY weekday, weekday_num
ORDER BY weekday_num ASC;

-- 3. Sleep vs Sedentary Behavior Relationship
SELECT 
    CASE 
        WHEN sedentary_minutes >= 1000 THEN 'High Sedentary (>= 16.6 hrs)'
        WHEN sedentary_minutes >= 700 THEN 'Moderate Sedentary (11.6 - 16.6 hrs)'
        ELSE 'Low Sedentary (< 11.6 hrs)'
    END AS sedentary_tier,
    COUNT(*) AS total_days,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep_hours,
    ROUND(AVG(sleep_efficiency), 2) AS avg_efficiency_pct
FROM daily_master
WHERE sleep_minutes > 0
GROUP BY sedentary_tier
ORDER BY avg_sleep_hours DESC;
