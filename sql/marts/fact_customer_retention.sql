CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per customer_unique_id. This is the correct customer entity for retention.
CREATE OR REPLACE TABLE marts.fact_customer_retention AS
WITH dataset_reference AS (
    SELECT MAX(order_date) AS reference_date
    FROM marts.fact_orders
),
customer_orders AS (
    SELECT
        o.customer_unique_id,
        o.order_id,
        o.order_date,
        o.gross_revenue,
        o.total_items
    FROM marts.fact_orders AS o
    WHERE
        o.order_date IS NOT NULL
        AND o.customer_unique_id IS NOT NULL
),
customer_metrics AS (
    SELECT
        customer_unique_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(gross_revenue) AS gross_revenue,
        SUM(total_items) AS total_items
    FROM customer_orders
    GROUP BY customer_unique_id
)
SELECT
    cm.customer_unique_id,
    cm.first_order_date,
    cm.last_order_date,
    cm.total_orders,
    cm.gross_revenue,
    cm.total_items,
    DATE_DIFF('day', cm.first_order_date, cm.last_order_date) AS days_between_first_and_last_order,
    DATE_DIFF('day', cm.last_order_date, dr.reference_date) AS days_since_last_order,
    -- Inactivity takes precedence so the segment reflects current engagement.
    CASE
        WHEN DATE_DIFF('day', cm.last_order_date, dr.reference_date) > 180 THEN 'inactive_customer'
        WHEN cm.gross_revenue >= 1000 OR cm.total_orders >= 3 THEN 'high_value_customer'
        WHEN cm.total_orders >= 2 THEN 'repeat_buyer'
        ELSE 'one_time_buyer'
    END AS customer_segment
FROM customer_metrics AS cm
CROSS JOIN dataset_reference AS dr;
