-- 05_heart_rate_analysis.sql
-- Optical Sensor Heart Rate & Cardio Intensity Analytics Queries

-- 1. Global Heart Rate Statistics
SELECT 
    COUNT(DISTINCT participant_id) AS hr_monitored_users,
    COUNT(*) AS total_hr_days,
    ROUND(AVG(avg_heart_rate), 2) AS overall_avg_bpm,
    ROUND(MIN(min_heart_rate), 0) AS lowest_resting_bpm_recorded,
    ROUND(MAX(max_heart_rate), 0) AS highest_peak_bpm_recorded,
    SUM(heart_rate_readings) AS total_second_readings
FROM daily_master
WHERE avg_heart_rate IS NOT NULL;

-- 2. Participant Heart Rate Summary Profile
SELECT 
    participant_id,
    COUNT(*) AS active_hr_days,
    ROUND(AVG(avg_heart_rate), 1) AS avg_bpm,
    ROUND(MIN(min_heart_rate), 0) AS min_bpm,
    ROUND(MAX(max_heart_rate), 0) AS max_bpm
FROM daily_master
WHERE avg_heart_rate IS NOT NULL
GROUP BY participant_id
ORDER BY avg_bpm DESC;
