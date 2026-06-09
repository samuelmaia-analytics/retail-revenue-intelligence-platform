-- Business question: What is the distribution of review scores and how are scores
-- associated with comments and late deliveries?
SELECT
    review_score,
    COUNT(*) AS total_reviews,
    COUNT(DISTINCT order_id) AS reviewed_orders,
    COUNT(*) FILTER (WHERE has_review_comment) AS reviews_with_comment,
    ROUND(
        COUNT(*) FILTER (WHERE has_review_comment)::DOUBLE
        / NULLIF(COUNT(*), 0),
        4
    ) AS review_comment_rate,
    COUNT(*) FILTER (WHERE is_late_delivery) AS late_delivery_reviews,
    ROUND(
        COUNT(*) FILTER (WHERE is_late_delivery)::DOUBLE
        / NULLIF(COUNT(*), 0),
        4
    ) AS late_delivery_share
FROM marts.fact_reviews
WHERE review_score IS NOT NULL
GROUP BY review_score
ORDER BY review_score;
