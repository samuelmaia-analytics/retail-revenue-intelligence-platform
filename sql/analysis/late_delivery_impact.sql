-- Business question: How does late delivery affect customer review scores and
-- delivery duration among delivered orders?
WITH order_reviews AS (
    SELECT
        order_id,
        AVG(review_score) AS average_review_score,
        COUNT(*) AS review_count
    FROM marts.fact_reviews
    WHERE review_score IS NOT NULL
    GROUP BY order_id
)
SELECT
    CASE
        WHEN orders.is_late_delivery THEN 'late'
        ELSE 'on_time'
    END AS delivery_status,
    COUNT(*) AS delivered_orders,
    COUNT(reviews.order_id) AS reviewed_orders,
    ROUND(AVG(orders.delivery_days), 2) AS average_delivery_days,
    ROUND(AVG(reviews.average_review_score), 2) AS average_review_score,
    ROUND(
        COUNT(reviews.order_id)::DOUBLE / NULLIF(COUNT(*), 0),
        4
    ) AS reviewed_order_rate,
    ROUND(SUM(orders.gross_revenue), 2) AS gross_revenue
FROM marts.fact_orders AS orders
LEFT JOIN order_reviews AS reviews
    ON orders.order_id = reviews.order_id
WHERE orders.is_delivered
GROUP BY 1
ORDER BY delivery_status;
