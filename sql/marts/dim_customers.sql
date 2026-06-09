CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per Olist customer_id.
CREATE OR REPLACE TABLE marts.dim_customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_prefix,
    customer_city,
    customer_state
FROM staging.stg_customers;
