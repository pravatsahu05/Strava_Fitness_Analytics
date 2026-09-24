-- analysis_queries.sql
-- Master Business & Analytical Query Suite for FitLife Wellness Intelligence

-- Query 1: Average Daily Steps
SELECT ROUND(AVG(total_steps), 0) AS avg_daily_steps FROM daily_master WHERE total_steps > 0;

-- Query 2: Average Daily Calories
SELECT ROUND(AVG(calories), 0) AS avg_daily_calories FROM daily_master WHERE calories > 0;

-- Query 3: Average Sedentary Minutes
SELECT ROUND(AVG(sedentary_minutes), 1) AS avg_sedentary_minutes, ROUND(AVG(sedentary_minutes)/60.0, 1) AS avg_sedentary_hours FROM daily_master;

-- Query 4: Average Active Minutes
SELECT 
    ROUND(AVG(very_active_minutes), 1) AS avg_very_active_mins,
    ROUND(AVG(fairly_active_minutes), 1) AS avg_fairly_active_mins,
    ROUND(AVG(lightly_active_minutes), 1) AS avg_lightly_active_mins,
    ROUND(AVG(very_active_minutes + fairly_active_minutes + lightly_active_minutes), 1) AS avg_total_active_mins
FROM daily_master;

-- Query 5: Activity by Weekday
SELECT 
    weekday,
    weekday_num,
    COUNT(*) AS total_days,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories
FROM daily_master
WHERE total_steps > 0
GROUP BY weekday, weekday_num
ORDER BY weekday_num ASC;

-- Query 6: Activity by Participant
SELECT 
    participant_id,
    COUNT(date) AS active_days,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories,
    ROUND(AVG(very_active_minutes), 1) AS avg_very_active_mins
FROM daily_master
GROUP BY participant_id
ORDER BY avg_steps DESC;

-- Query 7: Sleep by Weekday
SELECT 
    weekday,
    weekday_num,
    COUNT(*) AS sleep_logs,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep_hours,
    ROUND(AVG(sleep_efficiency), 2) AS avg_efficiency_pct
FROM daily_master
WHERE sleep_minutes > 0
GROUP BY weekday, weekday_num
ORDER BY weekday_num ASC;

-- Query 8: Sleep vs Steps Relationship
SELECT 
    CASE 
        WHEN total_steps >= 10000 THEN '10k+ Steps (High)'
        WHEN total_steps >= 5000 THEN '5k-10k Steps (Moderate)'
        ELSE '<5k Steps (Low)'
    END AS step_tier,
    COUNT(*) AS record_count,
    ROUND(AVG(sleep_hours), 2) AS avg_sleep_hours,
    ROUND(AVG(sleep_efficiency), 2) AS avg_sleep_efficiency
FROM daily_master
WHERE sleep_minutes > 0
GROUP BY step_tier
ORDER BY avg_sleep_hours DESC;

-- Query 9: Calories vs Steps Correlation Summary
SELECT 
    CASE 
        WHEN total_steps >= 12000 THEN '12k+ Steps'
        WHEN total_steps >= 8000 THEN '8k-12k Steps'
        WHEN total_steps >= 4000 THEN '4k-8k Steps'
        ELSE '<4k Steps'
    END AS step_bracket,
    COUNT(*) AS record_count,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories
FROM daily_master
WHERE total_steps > 0
GROUP BY step_bracket
ORDER BY avg_steps DESC;

-- Query 10: Sedentary Behavior Analysis
SELECT 
    ROUND(AVG(sedentary_minutes), 1) AS avg_sedentary_mins,
    ROUND(MAX(sedentary_minutes), 1) AS max_sedentary_mins,
    ROUND(MIN(sedentary_minutes), 1) AS min_sedentary_mins
FROM daily_master;

-- Query 11: Hourly Activity Trends
SELECT 
    hour,
    ROUND(AVG(steps), 0) AS avg_steps,
    ROUND(AVG(calories), 1) AS avg_calories
FROM hourly_master
GROUP BY hour
ORDER BY hour ASC;

-- Query 12: Most Active Participants (Top 5)
SELECT 
    participant_id,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories
FROM daily_master
GROUP BY participant_id
ORDER BY avg_steps DESC
LIMIT 5;

-- Query 13: Least Active Participants (Bottom 5)
SELECT 
    participant_id,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories
FROM daily_master
GROUP BY participant_id
HAVING AVG(total_steps) > 0
ORDER BY avg_steps ASC
LIMIT 5;

-- Query 14: Participant Coverage & Adherence
SELECT 
    participant_id,
    COUNT(date) AS total_logged_days,
    ROUND(COUNT(date) * 100.0 / 31.0, 1) AS adherence_pct
FROM daily_master
GROUP BY participant_id
ORDER BY total_logged_days DESC;

-- Query 15: Weekend vs Weekday Activity Comparison
SELECT 
    CASE WHEN weekday_num IN (5, 6) THEN 'Weekend (Sat-Sun)' ELSE 'Weekday (Mon-Fri)' END AS day_type,
    COUNT(*) AS total_days,
    ROUND(AVG(total_steps), 0) AS avg_steps,
    ROUND(AVG(calories), 0) AS avg_calories,
    ROUND(AVG(very_active_minutes), 1) AS avg_very_active_mins,
    ROUND(AVG(sedentary_minutes), 1) AS avg_sedentary_mins
FROM daily_master
WHERE total_steps > 0
GROUP BY day_type;

-- Query 16: Activity Intensity Distribution
SELECT 
    ROUND(SUM(very_active_minutes) * 100.0 / SUM(very_active_minutes + fairly_active_minutes + lightly_active_minutes + sedentary_minutes), 2) AS very_active_pct,
    ROUND(SUM(fairly_active_minutes) * 100.0 / SUM(very_active_minutes + fairly_active_minutes + lightly_active_minutes + sedentary_minutes), 2) AS fairly_active_pct,
    ROUND(SUM(lightly_active_minutes) * 100.0 / SUM(very_active_minutes + fairly_active_minutes + lightly_active_minutes + sedentary_minutes), 2) AS lightly_active_pct,
    ROUND(SUM(sedentary_minutes) * 100.0 / SUM(very_active_minutes + fairly_active_minutes + lightly_active_minutes + sedentary_minutes), 2) AS sedentary_pct
FROM daily_master;

-- Query 17: Heart-Rate Statistics
SELECT 
    COUNT(DISTINCT participant_id) AS hr_participants,
    ROUND(AVG(avg_heart_rate), 1) AS mean_heart_rate,
    ROUND(MIN(min_heart_rate), 0) AS min_resting_hr,
    ROUND(MAX(max_heart_rate), 0) AS max_peak_hr
FROM daily_master
WHERE avg_heart_rate IS NOT NULL;

-- Query 18: Weight/BMI Analysis
SELECT 
    COUNT(DISTINCT participant_id) AS weight_logging_participants,
    COUNT(*) AS total_weight_logs,
    ROUND(AVG(weight), 2) AS avg_weight_kg,
    ROUND(AVG(bmi), 2) AS avg_bmi
FROM daily_master
WHERE weight IS NOT NULL;
