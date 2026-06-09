CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_orders AS
WITH typed_orders AS (
    SELECT
        CAST(order_id AS VARCHAR) AS order_id,
        CAST(customer_id AS VARCHAR) AS customer_id,
        LOWER(TRIM(CAST(order_status AS VARCHAR))) AS order_status,
        TRY_CAST(order_purchase_timestamp AS TIMESTAMP) AS order_purchase_timestamp,
        TRY_CAST(order_approved_at AS TIMESTAMP) AS order_approved_at,
        TRY_CAST(order_delivered_carrier_date AS TIMESTAMP) AS order_delivered_carrier_date,
        TRY_CAST(order_delivered_customer_date AS TIMESTAMP) AS order_delivered_customer_date,
        TRY_CAST(order_estimated_delivery_date AS TIMESTAMP) AS order_estimated_delivery_date
    FROM raw.orders
)
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    CAST(order_purchase_timestamp AS DATE) AS order_date,
    CAST(order_approved_at AS DATE) AS approved_date,
    CAST(order_delivered_customer_date AS DATE) AS delivered_customer_date,
    CAST(order_estimated_delivery_date AS DATE) AS estimated_delivery_date,
    order_status = 'delivered' AS is_delivered,
    order_status = 'canceled' AS is_cancelled,
    CASE
        WHEN order_delivered_customer_date IS NULL OR order_estimated_delivery_date IS NULL THEN NULL
        ELSE order_delivered_customer_date > order_estimated_delivery_date
    END AS is_late_delivery,
    CASE
        WHEN order_purchase_timestamp IS NULL OR order_delivered_customer_date IS NULL THEN NULL
        ELSE DATE_DIFF('day', CAST(order_purchase_timestamp AS DATE), CAST(order_delivered_customer_date AS DATE))
    END AS delivery_days,
    CASE
        WHEN order_purchase_timestamp IS NULL OR order_estimated_delivery_date IS NULL THEN NULL
        ELSE DATE_DIFF('day', CAST(order_purchase_timestamp AS DATE), CAST(order_estimated_delivery_date AS DATE))
    END AS estimated_delivery_days
FROM typed_orders;
