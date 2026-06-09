CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_order_items AS
SELECT
    CAST(order_id AS VARCHAR) AS order_id,
    TRY_CAST(order_item_id AS INTEGER) AS order_item_id,
    CAST(product_id AS VARCHAR) AS product_id,
    CAST(seller_id AS VARCHAR) AS seller_id,
    TRY_CAST(shipping_limit_date AS TIMESTAMP) AS shipping_limit_timestamp,
    CAST(TRY_CAST(shipping_limit_date AS TIMESTAMP) AS DATE) AS shipping_limit_date,
    TRY_CAST(price AS DECIMAL(18, 2)) AS item_price,
    TRY_CAST(freight_value AS DECIMAL(18, 2)) AS freight_value
FROM raw.order_items;
