CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per order_id.
-- In Olist, item_price represents merchandise value. payment_value can include freight
-- and can appear in multiple rows when an order has split payments.
CREATE OR REPLACE TABLE marts.fact_orders AS
WITH item_totals AS (
    SELECT
        order_id,
        SUM(item_price) AS gross_revenue,
        SUM(freight_value) AS freight_value,
        COUNT(*) AS total_items
    FROM staging.stg_order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment_value
    FROM staging.stg_order_payments
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    c.customer_city,
    o.order_status,
    o.order_date,
    o.approved_date,
    o.delivered_customer_date,
    o.estimated_delivery_date,
    o.is_delivered,
    o.is_cancelled,
    o.is_late_delivery,
    o.delivery_days,
    COALESCE(i.gross_revenue, 0) AS gross_revenue,
    COALESCE(i.freight_value, 0) AS freight_value,
    COALESCE(p.total_payment_value, 0) AS total_payment_value,
    COALESCE(i.total_items, 0) AS total_items
FROM staging.stg_orders AS o
LEFT JOIN staging.stg_customers AS c
    ON o.customer_id = c.customer_id
LEFT JOIN item_totals AS i
    ON o.order_id = i.order_id
LEFT JOIN payment_totals AS p
    ON o.order_id = p.order_id;
