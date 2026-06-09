-- Business question: How are orders and merchandise revenue evolving month over
-- month, and where are growth or contraction periods?
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', order_date)::DATE AS order_month,
        COUNT(*) AS total_orders,
        SUM(total_items) AS total_items,
        SUM(gross_revenue) AS gross_revenue,
        SUM(freight_value) AS freight_revenue,
        AVG(gross_revenue) AS average_order_value
    FROM marts.fact_orders
    WHERE order_date IS NOT NULL
    GROUP BY 1
),
with_previous_month AS (
    SELECT
        *,
        LAG(gross_revenue) OVER (ORDER BY order_month) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    order_month,
    total_orders,
    total_items,
    ROUND(gross_revenue, 2) AS gross_revenue,
    ROUND(freight_revenue, 2) AS freight_revenue,
    ROUND(average_order_value, 2) AS average_order_value,
    ROUND(
        (gross_revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        4
    ) AS month_over_month_revenue_growth
FROM with_previous_month
ORDER BY order_month;
