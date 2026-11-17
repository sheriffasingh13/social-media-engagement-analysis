-- Capstone analysis outputs
-- Sheriffa Singh
-- Data: data/cleaned/facebook_metrics_cleaned.csv, loaded into SQLite with load_data.sql
-- Run from the main project folder:
--   sqlite3 outputs/facebook_metrics.db < sql/load_data.sql
--   sqlite3 outputs/facebook_metrics.db < sql/analysis_queries.sql
-- Engagement rate = (likes + comments + shares) / reach * 100
--
-- SQLite has no MEDIAN function, so each query numbers the posts in each group
-- from lowest to highest engagement rate (ROW_NUMBER) and takes the middle one.
-- If a group has an even number of posts, it averages the two middle ones.

.headers on
.mode column

-- ------------------------------------------------------------
-- Output 1: Median engagement rate by post format
-- (all posts, and with the 9 flagged posts removed)
-- ------------------------------------------------------------
.print
.print OUTPUT 1: Median engagement rate by format
WITH ranked AS (
    SELECT format, engagement_rate,
           ROW_NUMBER() OVER (PARTITION BY format ORDER BY engagement_rate) AS rn,
           COUNT(*)     OVER (PARTITION BY format) AS n
    FROM posts
),
ranked_unflagged AS (
    SELECT format, engagement_rate,
           ROW_NUMBER() OVER (PARTITION BY format ORDER BY engagement_rate) AS rn,
           COUNT(*)     OVER (PARTITION BY format) AS n
    FROM posts
    WHERE flag_any = 'False'
),
all_posts AS (
    SELECT format, n AS posts, ROUND(AVG(engagement_rate), 2) AS median_rate
    FROM ranked WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
    GROUP BY format
),
unflagged AS (
    SELECT format, n AS posts, ROUND(AVG(engagement_rate), 2) AS median_rate
    FROM ranked_unflagged WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
    GROUP BY format
),
reach AS (
    SELECT format, CAST(AVG(reach) AS INT) AS avg_reach FROM posts GROUP BY format
)
SELECT a.format,
       a.posts,
       a.median_rate        AS median_rate_pct,
       u.posts              AS posts_unflagged,
       u.median_rate        AS median_rate_unflagged_pct
FROM all_posts a
JOIN unflagged u ON a.format = u.format
ORDER BY a.median_rate DESC;

-- ------------------------------------------------------------
-- Output 2: Photo vs. non-photo posts within each category
-- ------------------------------------------------------------
.print
.print OUTPUT 2: Photo vs. non-photo within each category
WITH labeled AS (
    SELECT category,
           CASE WHEN format = 'Photo' THEN 'Photo' ELSE 'Non-photo' END AS format_group,
           engagement_rate
    FROM posts
),
ranked AS (
    SELECT category, format_group, engagement_rate,
           ROW_NUMBER() OVER (PARTITION BY category, format_group ORDER BY engagement_rate) AS rn,
           COUNT(*)     OVER (PARTITION BY category, format_group) AS n
    FROM labeled
)
SELECT category, format_group, n AS posts,
       ROUND(AVG(engagement_rate), 2) AS median_rate_pct
FROM ranked
WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
GROUP BY category, format_group
ORDER BY category, format_group DESC;

-- ------------------------------------------------------------
-- Output 3: Posting time block, photo vs. non-photo
-- ------------------------------------------------------------
.print
.print OUTPUT 3: Time block by photo vs. non-photo
WITH labeled AS (
    SELECT time_block,
           CASE WHEN format = 'Photo' THEN 'Photo' ELSE 'Non-photo' END AS format_group,
           engagement_rate
    FROM posts
),
ranked AS (
    SELECT time_block, format_group, engagement_rate,
           ROW_NUMBER() OVER (PARTITION BY time_block, format_group ORDER BY engagement_rate) AS rn,
           COUNT(*)     OVER (PARTITION BY time_block, format_group) AS n
    FROM labeled
)
SELECT time_block, format_group, n AS posts,
       ROUND(AVG(engagement_rate), 2) AS median_rate_pct
FROM ranked
WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
GROUP BY time_block, format_group
ORDER BY CASE time_block
            WHEN 'Overnight (12-5 AM)' THEN 1
            WHEN 'Morning (6-11 AM)'   THEN 2
            WHEN 'Afternoon (12-5 PM)' THEN 3
            ELSE 4 END,
         format_group DESC;

-- ------------------------------------------------------------
-- Output 4: Page-size quartile, with the months each one covers
-- ------------------------------------------------------------
.print
.print OUTPUT 4: Page-size quartile and time of year
WITH ranked AS (
    SELECT page_size_quartile, engagement_rate,
           ROW_NUMBER() OVER (PARTITION BY page_size_quartile ORDER BY engagement_rate) AS rn,
           COUNT(*)     OVER (PARTITION BY page_size_quartile) AS n
    FROM posts
),
medians AS (
    SELECT page_size_quartile, n AS posts, ROUND(AVG(engagement_rate), 2) AS median_rate_pct
    FROM ranked WHERE rn IN ((n + 1) / 2, (n + 2) / 2)
    GROUP BY page_size_quartile
),
ranges AS (
    SELECT page_size_quartile,
           MIN(page_likes) AS min_page_likes, MAX(page_likes) AS max_page_likes,
           MIN(month) AS first_month, MAX(month) AS last_month,
           ROUND(100.0 * SUM(format = 'Photo') / COUNT(*), 1) AS pct_photo,
           ROUND(100.0 * SUM(category = 'Action') / COUNT(*), 1) AS pct_action
    FROM posts GROUP BY page_size_quartile
)
SELECT m.page_size_quartile, m.posts, r.min_page_likes, r.max_page_likes,
       r.first_month, r.last_month, r.pct_photo, r.pct_action, m.median_rate_pct
FROM medians m JOIN ranges r ON m.page_size_quartile = r.page_size_quartile
ORDER BY m.page_size_quartile;
