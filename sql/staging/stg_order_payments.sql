CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_order_payments AS
SELECT
    CAST(order_id AS VARCHAR) AS order_id,
    TRY_CAST(payment_sequential AS INTEGER) AS payment_sequential,
    LOWER(TRIM(CAST(payment_type AS VARCHAR))) AS payment_type,
    TRY_CAST(payment_installments AS INTEGER) AS payment_installments,
    TRY_CAST(payment_value AS DECIMAL(18, 2)) AS payment_value
FROM raw.order_payments;
