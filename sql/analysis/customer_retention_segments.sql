-- Business question: How large and valuable is each customer retention segment?
SELECT
    customer_segment,
    COUNT(*) AS total_customers,
    SUM(total_orders) AS total_orders,
    SUM(total_items) AS total_items,
    ROUND(SUM(gross_revenue), 2) AS gross_revenue,
    ROUND(AVG(gross_revenue), 2) AS average_revenue_per_customer,
    ROUND(AVG(total_orders), 2) AS average_orders_per_customer,
    ROUND(AVG(days_since_last_order), 2) AS average_days_since_last_order,
    ROUND(
        COUNT(*)::DOUBLE / NULLIF(SUM(COUNT(*)) OVER (), 0),
        4
    ) AS customer_share
FROM marts.fact_customer_retention
GROUP BY customer_segment
ORDER BY gross_revenue DESC;
