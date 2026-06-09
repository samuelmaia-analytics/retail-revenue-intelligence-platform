CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_sellers AS
SELECT
    CAST(seller_id AS VARCHAR) AS seller_id,
    CAST(seller_zip_code_prefix AS VARCHAR) AS seller_zip_prefix,
    LOWER(TRIM(CAST(seller_city AS VARCHAR))) AS seller_city,
    UPPER(TRIM(CAST(seller_state AS VARCHAR))) AS seller_state
FROM raw.sellers;
