CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per day, customer state and product category.
CREATE OR REPLACE TABLE marts.fact_revenue_daily AS
SELECT
    foi.order_date,
    foi.customer_state,
    foi.product_category_name_english,
    COUNT(DISTINCT foi.order_id) AS total_orders,
    COUNT(*) AS total_items,
    SUM(foi.item_price) AS gross_revenue,
    SUM(foi.freight_value) AS freight_value,
    CASE
        WHEN COUNT(DISTINCT foi.order_id) = 0 THEN 0
        ELSE SUM(foi.item_price) / COUNT(DISTINCT foi.order_id)
    END AS average_order_value,
    COUNT(DISTINCT CASE WHEN o.is_delivered THEN foi.order_id END) AS delivered_orders,
    COUNT(DISTINCT CASE WHEN o.is_cancelled THEN foi.order_id END) AS cancelled_orders,
    COUNT(DISTINCT CASE WHEN COALESCE(o.is_late_delivery, FALSE) THEN foi.order_id END) AS late_deliveries
FROM marts.fact_order_items AS foi
LEFT JOIN marts.fact_orders AS o
    ON foi.order_id = o.order_id
GROUP BY
    foi.order_date,
    foi.customer_state,
    foi.product_category_name_english;
