CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per seller_id.
CREATE OR REPLACE TABLE marts.dim_sellers AS
SELECT
    seller_id,
    seller_zip_prefix,
    seller_city,
    seller_state
FROM staging.stg_sellers;
