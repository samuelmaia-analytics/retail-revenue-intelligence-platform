-- Business question: Which product categories drive merchandise revenue, item
-- volume and order frequency?
SELECT
    COALESCE(product_category_name_english, 'unknown') AS product_category,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(item_price), 2) AS gross_revenue,
    ROUND(SUM(freight_value), 2) AS freight_revenue,
    ROUND(SUM(item_price) / NULLIF(COUNT(DISTINCT order_id), 0), 2)
        AS average_order_value_in_category,
    ROUND(AVG(item_price), 2) AS average_item_price,
    ROUND(
        SUM(item_price) / NULLIF(SUM(SUM(item_price)) OVER (), 0),
        4
    ) AS revenue_share
FROM marts.fact_order_items
GROUP BY 1
ORDER BY gross_revenue DESC;
