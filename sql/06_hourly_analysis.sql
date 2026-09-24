-- 06_hourly_analysis.sql
-- Hourly Activity Dynamics & Peak Hour Identification Queries

-- 1. Hourly Average Activity & Intensity Across All Participants
SELECT 
    hour,
    ROUND(AVG(steps), 0) AS avg_hourly_steps,
    ROUND(AVG(calories), 1) AS avg_hourly_calories,
    ROUND(AVG(total_intensity), 1) AS avg_total_intensity,
    ROUND(AVG(average_intensity), 4) AS avg_intensity_score
FROM hourly_master
GROUP BY hour
ORDER BY hour ASC;

-- 2. Identification of Peak Activity Hours
SELECT 
    hour,
    ROUND(AVG(steps), 0) AS avg_steps,
    ROUND(AVG(calories), 1) AS avg_calories
FROM hourly_master
GROUP BY hour
ORDER BY avg_steps DESC
LIMIT 5;

-- 3. Identification of Lowest Activity Hours (Excluding Night Sleep Windows)
SELECT 
    hour,
    ROUND(AVG(steps), 0) AS avg_steps,
    ROUND(AVG(calories), 1) AS avg_calories
FROM hourly_master
WHERE hour BETWEEN 7 AND 22
GROUP BY hour
ORDER BY avg_steps ASC
LIMIT 5;
