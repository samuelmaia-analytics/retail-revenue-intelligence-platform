-- Business question: Which sellers lead revenue and volume, and what operational
-- indicators should be considered alongside their commercial performance?
SELECT
    ROW_NUMBER() OVER (ORDER BY gross_revenue DESC, seller_id) AS revenue_rank,
    seller_id,
    seller_state,
    total_orders,
    total_items,
    ROUND(gross_revenue, 2) AS gross_revenue,
    ROUND(freight_value, 2) AS freight_revenue,
    ROUND(average_item_price, 2) AS average_item_price,
    unique_products,
    unique_customers,
    late_deliveries,
    ROUND(late_delivery_rate, 4) AS late_delivery_rate,
    ROUND(average_review_score, 2) AS average_review_score
FROM marts.fact_seller_performance
ORDER BY revenue_rank
LIMIT 100;
