-- Business question: How does repeat purchase rate vary by first-order cohort?
SELECT
    DATE_TRUNC('month', first_order_date)::DATE AS first_order_month,
    COUNT(*) AS total_customers,
    COUNT(*) FILTER (WHERE total_orders >= 2) AS repeat_customers,
    ROUND(
        COUNT(*) FILTER (WHERE total_orders >= 2)::DOUBLE
        / NULLIF(COUNT(*), 0),
        4
    ) AS repeat_purchase_rate,
    ROUND(AVG(total_orders), 2) AS average_orders_per_customer,
    ROUND(AVG(gross_revenue), 2) AS average_customer_revenue
FROM marts.fact_customer_retention
GROUP BY 1
ORDER BY first_order_month;
