CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_customers AS
SELECT
    CAST(customer_id AS VARCHAR) AS customer_id,
    CAST(customer_unique_id AS VARCHAR) AS customer_unique_id,
    CAST(customer_zip_code_prefix AS VARCHAR) AS customer_zip_prefix,
    LOWER(TRIM(CAST(customer_city AS VARCHAR))) AS customer_city,
    UPPER(TRIM(CAST(customer_state AS VARCHAR))) AS customer_state
FROM raw.customers;
