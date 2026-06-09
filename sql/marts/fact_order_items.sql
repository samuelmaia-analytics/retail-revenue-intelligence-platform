CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per order item.
CREATE OR REPLACE TABLE marts.fact_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    o.customer_id,
    o.order_date,
    oi.item_price,
    oi.freight_value,
    p.product_category_name_english,
    s.seller_state,
    c.customer_state
FROM staging.stg_order_items AS oi
LEFT JOIN staging.stg_orders AS o
    ON oi.order_id = o.order_id
LEFT JOIN marts.dim_customers AS c
    ON o.customer_id = c.customer_id
LEFT JOIN marts.dim_products AS p
    ON oi.product_id = p.product_id
LEFT JOIN marts.dim_sellers AS s
    ON oi.seller_id = s.seller_id;
