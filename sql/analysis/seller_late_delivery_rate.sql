-- Business question: Which sellers have the highest late-delivery exposure after
-- accounting for their order volume?
SELECT
    seller_id,
    seller_state,
    total_orders,
    late_deliveries,
    ROUND(late_delivery_rate, 4) AS late_delivery_rate,
    ROUND(gross_revenue, 2) AS gross_revenue,
    ROUND(average_review_score, 2) AS average_review_score
FROM marts.fact_seller_performance
WHERE total_orders >= 10
ORDER BY late_delivery_rate DESC, total_orders DESC, seller_id;
