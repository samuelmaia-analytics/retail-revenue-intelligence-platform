-- Business question: Where and when are cancellations concentrated, and how much
-- merchandise value is associated with cancelled orders?
SELECT
    DATE_TRUNC('month', order_date)::DATE AS order_month,
    COALESCE(customer_state, 'unknown') AS customer_state,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE is_cancelled) AS cancelled_orders,
    ROUND(
        COUNT(*) FILTER (WHERE is_cancelled)::DOUBLE / NULLIF(COUNT(*), 0),
        4
    ) AS cancellation_rate,
    ROUND(
        SUM(gross_revenue) FILTER (WHERE is_cancelled),
        2
    ) AS cancelled_gross_revenue,
    ROUND(
        SUM(total_payment_value) FILTER (WHERE is_cancelled),
        2
    ) AS cancelled_payment_value
FROM marts.fact_orders
WHERE order_date IS NOT NULL
GROUP BY 1, 2
ORDER BY order_month, cancellation_rate DESC, customer_state;
