-- Business question: Which product categories have the greatest freight burden
-- relative to merchandise revenue?
SELECT
    COALESCE(product_category_name_english, 'unknown') AS product_category,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(item_price), 2) AS gross_revenue,
    ROUND(SUM(freight_value), 2) AS freight_revenue,
    ROUND(AVG(freight_value), 2) AS average_freight_per_item,
    ROUND(
        SUM(freight_value) / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_freight_per_order,
    ROUND(
        SUM(freight_value) / NULLIF(SUM(item_price), 0),
        4
    ) AS freight_to_revenue_ratio
FROM marts.fact_order_items
GROUP BY 1
ORDER BY freight_to_revenue_ratio DESC, gross_revenue DESC;
