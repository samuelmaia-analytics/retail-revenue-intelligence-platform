CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per payment event in an order.
CREATE OR REPLACE TABLE marts.fact_payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value
FROM staging.stg_order_payments;
