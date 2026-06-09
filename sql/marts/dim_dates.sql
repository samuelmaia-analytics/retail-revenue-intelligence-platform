CREATE SCHEMA IF NOT EXISTS marts;

-- Calendar is bounded by the actual order period available in the Olist dataset.
CREATE OR REPLACE TABLE marts.dim_dates AS
WITH date_bounds AS (
    SELECT
        MIN(order_date) AS min_date,
        MAX(order_date) AS max_date
    FROM staging.stg_orders
    WHERE order_date IS NOT NULL
),
calendar AS (
    SELECT CAST(date_day AS DATE) AS full_date
    FROM date_bounds,
    GENERATE_SERIES(min_date, max_date, INTERVAL 1 DAY) AS generated_dates(date_day)
)
SELECT
    CAST(STRFTIME(full_date, '%Y%m%d') AS INTEGER) AS date_id,
    full_date,
    EXTRACT(YEAR FROM full_date) AS year,
    EXTRACT(QUARTER FROM full_date) AS quarter,
    EXTRACT(MONTH FROM full_date) AS month,
    STRFTIME(full_date, '%B') AS month_name,
    EXTRACT(WEEK FROM full_date) AS week,
    EXTRACT(DAY FROM full_date) AS day,
    EXTRACT(DAYOFWEEK FROM full_date) AS day_of_week,
    STRFTIME(full_date, '%A') AS day_name,
    EXTRACT(DAYOFWEEK FROM full_date) IN (0, 6) AS is_weekend
FROM calendar;
