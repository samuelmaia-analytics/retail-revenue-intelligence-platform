-- Business question: Which customer states generate the most revenue and how do
-- their order value, cancellation and delivery performance compare?
SELECT
    COALESCE(customer_state, 'unknown') AS customer_state,
    COUNT(*) AS total_orders,
    SUM(total_items) AS total_items,
    ROUND(SUM(gross_revenue), 2) AS gross_revenue,
    ROUND(SUM(freight_value), 2) AS freight_revenue,
    ROUND(AVG(gross_revenue), 2) AS average_order_value,
    COUNT(*) FILTER (WHERE is_cancelled) AS cancelled_orders,
    ROUND(
        COUNT(*) FILTER (WHERE is_cancelled)::DOUBLE / NULLIF(COUNT(*), 0),
        4
    ) AS cancellation_rate,
    COUNT(*) FILTER (WHERE is_late_delivery) AS late_deliveries,
    ROUND(
        COUNT(*) FILTER (WHERE is_late_delivery)::DOUBLE
        / NULLIF(COUNT(*) FILTER (WHERE is_delivered), 0),
        4
    ) AS late_delivery_rate
FROM marts.fact_orders
GROUP BY 1
ORDER BY gross_revenue DESC;
