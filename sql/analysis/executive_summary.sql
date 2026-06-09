-- Business question: What are the main commercial, operational and customer
-- indicators for the complete period covered by the Olist dataset?
WITH order_metrics AS (
    SELECT
        COUNT(*) AS total_orders,
        SUM(gross_revenue) AS gross_revenue,
        SUM(freight_value) AS freight_revenue,
        SUM(total_payment_value) AS total_payment_value,
        SUM(total_items) AS total_items,
        AVG(gross_revenue) AS average_order_value,
        COUNT(*) FILTER (WHERE is_delivered) AS delivered_orders,
        COUNT(*) FILTER (WHERE is_cancelled) AS cancelled_orders,
        COUNT(*) FILTER (WHERE is_late_delivery) AS late_deliveries,
        AVG(delivery_days) FILTER (WHERE is_delivered) AS average_delivery_days
    FROM marts.fact_orders
),
review_metrics AS (
    SELECT AVG(review_score) AS average_review_score
    FROM marts.fact_reviews
),
customer_metrics AS (
    SELECT
        COUNT(*) AS unique_customers,
        COUNT(*) FILTER (WHERE total_orders >= 2) AS repeat_customers
    FROM marts.fact_customer_retention
)
SELECT
    om.total_orders,
    om.total_items,
    ROUND(om.gross_revenue, 2) AS gross_revenue,
    ROUND(om.freight_revenue, 2) AS freight_revenue,
    ROUND(om.total_payment_value, 2) AS total_payment_value,
    ROUND(om.average_order_value, 2) AS average_order_value,
    om.delivered_orders,
    om.cancelled_orders,
    ROUND(om.cancelled_orders::DOUBLE / NULLIF(om.total_orders, 0), 4)
        AS cancellation_rate,
    om.late_deliveries,
    ROUND(om.late_deliveries::DOUBLE / NULLIF(om.delivered_orders, 0), 4)
        AS late_delivery_rate,
    ROUND(om.average_delivery_days, 2) AS average_delivery_days,
    ROUND(rm.average_review_score, 2) AS average_review_score,
    cm.unique_customers,
    cm.repeat_customers,
    ROUND(cm.repeat_customers::DOUBLE / NULLIF(cm.unique_customers, 0), 4)
        AS repeat_purchase_rate
FROM order_metrics AS om
CROSS JOIN review_metrics AS rm
CROSS JOIN customer_metrics AS cm;
