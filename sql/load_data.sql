-- Creates the posts table with the right data types, then loads the cleaned CSV.
-- Run with: sqlite3 outputs/facebook_metrics.db < sql/load_data.sql
CREATE TABLE posts (
    page_likes INTEGER, format TEXT, category TEXT, month INTEGER, weekday INTEGER,
    hour INTEGER, paid TEXT, reach INTEGER, impressions INTEGER, likes INTEGER,
    comments INTEGER, shares INTEGER, total_interactions INTEGER,
    flag_low_reach TEXT, flag_reach_gt_impr TEXT, flag_any TEXT,
    interactions INTEGER, engagement_rate REAL, time_block TEXT, page_size_quartile TEXT
);
.import --csv --skip 1 data/cleaned/facebook_metrics_cleaned.csv posts
