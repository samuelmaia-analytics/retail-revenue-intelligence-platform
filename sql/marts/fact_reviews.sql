CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per review.
CREATE OR REPLACE TABLE marts.fact_reviews AS
SELECT
    r.review_id,
    r.order_id,
    r.review_score,
    r.has_review_comment,
    r.review_creation_date,
    r.review_answer_timestamp,
    o.order_date,
    o.is_late_delivery,
    o.customer_state
FROM staging.stg_order_reviews AS r
LEFT JOIN marts.fact_orders AS o
    ON r.order_id = o.order_id;
