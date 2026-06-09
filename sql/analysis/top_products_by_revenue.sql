-- Business question: Which individual products generate the most merchandise
-- revenue and item volume?
WITH product_performance AS (
    SELECT
        product_id,
        COALESCE(product_category_name_english, 'unknown') AS product_category,
        COUNT(DISTINCT order_id) AS total_orders,
        COUNT(*) AS total_items,
        SUM(item_price) AS gross_revenue,
        SUM(freight_value) AS freight_revenue,
        AVG(item_price) AS average_item_price
    FROM marts.fact_order_items
    GROUP BY product_id, product_category
)
SELECT
    ROW_NUMBER() OVER (ORDER BY gross_revenue DESC, product_id) AS revenue_rank,
    product_id,
    product_category,
    total_orders,
    total_items,
    ROUND(gross_revenue, 2) AS gross_revenue,
    ROUND(freight_revenue, 2) AS freight_revenue,
    ROUND(average_item_price, 2) AS average_item_price
FROM product_performance
ORDER BY revenue_rank
LIMIT 100;
