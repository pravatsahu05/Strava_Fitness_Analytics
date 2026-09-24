-- FitLife Wellness Intelligence - Relational Database Schema DDL
-- Target Database: SQLite (database/fitness.db)

-- 1. Table: daily_master (Primary Daily Fact Table)
CREATE TABLE IF NOT EXISTS daily_master (
    participant_id TEXT NOT NULL,
    date TEXT NOT NULL,
    weekday TEXT,
    weekday_num INTEGER,
    total_steps INTEGER,
    total_distance REAL,
    very_active_minutes INTEGER,
    fairly_active_minutes INTEGER,
    lightly_active_minutes INTEGER,
    sedentary_minutes INTEGER,
    calories INTEGER,
    sleep_hours REAL,
    sleep_minutes INTEGER,
    sleep_efficiency REAL,
    weight REAL,
    bmi REAL,
    weight_log_count INTEGER,
    avg_heart_rate REAL,
    min_heart_rate REAL,
    max_heart_rate REAL,
    heart_rate_readings INTEGER,
    PRIMARY KEY (participant_id, date)
);

-- 2. Table: daily_activity
CREATE TABLE IF NOT EXISTS daily_activity (
    participant_id TEXT NOT NULL,
    date TEXT NOT NULL,
    total_steps INTEGER,
    total_distance REAL,
    tracker_distance REAL,
    logged_activities_distance REAL,
    very_active_distance REAL,
    moderately_active_distance REAL,
    light_active_distance REAL,
    sedentary_active_distance REAL,
    very_active_minutes INTEGER,
    fairly_active_minutes INTEGER,
    lightly_active_minutes INTEGER,
    sedentary_minutes INTEGER,
    calories INTEGER,
    is_zero_activity INTEGER,
    steps_outlier_flag INTEGER,
    calories_outlier_flag INTEGER,
    weekday TEXT,
    weekday_num INTEGER,
    PRIMARY KEY (participant_id, date)
);

-- 3. Table: sleep_daily
CREATE TABLE IF NOT EXISTS sleep_daily (
    participant_id TEXT NOT NULL,
    date TEXT NOT NULL,
    total_sleep_records INTEGER,
    total_minutes_asleep INTEGER,
    total_time_in_bed INTEGER,
    sleep_efficiency REAL,
    sleep_hours REAL,
    PRIMARY KEY (participant_id, date)
);

-- 4. Table: weight_daily
CREATE TABLE IF NOT EXISTS weight_daily (
    participant_id TEXT NOT NULL,
    date TEXT NOT NULL,
    datetime TEXT,
    weight_kg REAL,
    weight_pounds REAL,
    fat REAL,
    bmi REAL,
    is_manual_report TEXT,
    log_id INTEGER
);

-- 5. Table: heart_rate_daily
CREATE TABLE IF NOT EXISTS heart_rate_daily (
    participant_id TEXT NOT NULL,
    date TEXT NOT NULL,
    avg_heart_rate REAL,
    min_heart_rate REAL,
    max_heart_rate REAL,
    heart_rate_readings INTEGER,
    PRIMARY KEY (participant_id, date)
);

-- 6. Table: hourly_master
CREATE TABLE IF NOT EXISTS hourly_master (
    participant_id TEXT NOT NULL,
    date TEXT NOT NULL,
    hour INTEGER NOT NULL,
    weekday TEXT,
    weekday_num INTEGER,
    steps INTEGER,
    calories INTEGER,
    total_intensity INTEGER,
    average_intensity REAL,
    PRIMARY KEY (participant_id, date, hour)
);

-- PERFORMANCE INDEXES
CREATE INDEX IF NOT EXISTS idx_daily_master_participant ON daily_master(participant_id);
CREATE INDEX IF NOT EXISTS idx_daily_master_date ON daily_master(date);
CREATE INDEX IF NOT EXISTS idx_daily_activity_date ON daily_activity(date);
CREATE INDEX IF NOT EXISTS idx_sleep_daily_date ON sleep_daily(date);
CREATE INDEX IF NOT EXISTS idx_hourly_master_lookup ON hourly_master(participant_id, date, hour);
