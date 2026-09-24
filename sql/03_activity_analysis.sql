-- 03_activity_analysis.sql
-- Physical Activity Metrics & Weekday Behavior Queries

-- 1. Executive Activity Summary Metrics
SELECT 
    ROUND(AVG(total_steps), 0) AS avg_daily_steps,
    ROUND(AVG(total_distance), 2) AS avg_daily_distance_km,
    ROUND(AVG(calories), 0) AS avg_daily_calories,
    ROUND(AVG(very_active_minutes), 1) AS avg_very_active_mins,
    ROUND(AVG(fairly_active_minutes), 1) AS avg_fairly_active_mins,
    ROUND(AVG(lightly_active_minutes), 1) AS avg_lightly_active_mins,
    ROUND(AVG(sedentary_minutes), 1) AS avg_sedentary_mins
FROM daily_master
WHERE total_steps > 0;

-- 2. Activity Breakdown by Day of the Week
SELECT 
    weekday,
    weekday_num,
    COUNT(*) AS total_records,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories,
    ROUND(AVG(very_active_minutes + fairly_active_minutes + lightly_active_minutes), 1) AS avg_total_active_mins,
    ROUND(AVG(sedentary_minutes), 1) AS avg_sedentary_mins
FROM daily_master
WHERE total_steps > 0
GROUP BY weekday, weekday_num
ORDER BY weekday_num ASC;

-- 3. Step Goal Segmentation Analysis (CDC Benchmark: 10,000 steps)
SELECT 
    CASE 
        WHEN total_steps >= 10000 THEN '3. Highly Active (>=10k steps)'
        WHEN total_steps >= 7500 THEN '2. Moderately Active (7.5k-10k steps)'
        WHEN total_steps >= 5000 THEN '1. Low Active (5k-7.5k steps)'
        ELSE '0. Sedentary (<5k steps)'
    END AS step_category,
    COUNT(*) AS record_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM daily_master WHERE total_steps > 0), 2) AS percentage_of_days,
    ROUND(AVG(calories), 0) AS avg_calories
FROM daily_master
WHERE total_steps > 0
GROUP BY step_category
ORDER BY step_category DESC;
