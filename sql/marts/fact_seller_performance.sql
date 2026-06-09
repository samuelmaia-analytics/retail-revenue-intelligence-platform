CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per seller_id.
CREATE OR REPLACE TABLE marts.fact_seller_performance AS
WITH seller_orders AS (
    SELECT
        i.seller_id,
        i.order_id,
        o.customer_id,
        i.product_id,
        i.item_price,
        i.freight_value,
        COALESCE(o.is_late_delivery, FALSE) AS is_late_delivery
    FROM marts.fact_order_items AS i
    LEFT JOIN marts.fact_orders AS o
        ON i.order_id = o.order_id
),
seller_order_reviews AS (
    -- A seller/order/review is counted once, regardless of how many items the seller
    -- supplied in that order, avoiding item-count weighting in the review average.
    SELECT DISTINCT
        i.seller_id,
        r.order_id,
        r.review_id,
        r.review_score
    FROM marts.fact_order_items AS i
    INNER JOIN marts.fact_reviews AS r
        ON i.order_id = r.order_id
    WHERE r.review_score IS NOT NULL
),
review_scores AS (
    SELECT
        seller_id,
        AVG(review_score) AS average_review_score
    FROM seller_order_reviews
    GROUP BY seller_id
)
SELECT
    so.seller_id,
    s.seller_state,
    COUNT(DISTINCT so.order_id) AS total_orders,
    COUNT(*) AS total_items,
    SUM(so.item_price) AS gross_revenue,
    SUM(so.freight_value) AS freight_value,
    AVG(so.item_price) AS average_item_price,
    COUNT(DISTINCT so.product_id) AS unique_products,
    COUNT(DISTINCT so.customer_id) AS unique_customers,
    COUNT(DISTINCT CASE WHEN so.is_late_delivery THEN so.order_id END) AS late_deliveries,
    CASE
        WHEN COUNT(DISTINCT so.order_id) = 0 THEN 0
        ELSE COUNT(DISTINCT CASE WHEN so.is_late_delivery THEN so.order_id END)::DOUBLE
            / COUNT(DISTINCT so.order_id)
    END AS late_delivery_rate,
    rs.average_review_score
FROM seller_orders AS so
LEFT JOIN marts.dim_sellers AS s
    ON so.seller_id = s.seller_id
LEFT JOIN review_scores AS rs
    ON so.seller_id = rs.seller_id
GROUP BY
    so.seller_id,
    s.seller_state,
    rs.average_review_score;
