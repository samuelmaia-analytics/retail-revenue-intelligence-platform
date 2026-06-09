CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_products AS
SELECT
    CAST(product_id AS VARCHAR) AS product_id,
    LOWER(TRIM(CAST(product_category_name AS VARCHAR))) AS product_category_name,
    TRY_CAST(product_name_lenght AS INTEGER) AS product_name_length,
    TRY_CAST(product_description_lenght AS INTEGER) AS product_description_length,
    TRY_CAST(product_photos_qty AS INTEGER) AS product_photos_qty,
    TRY_CAST(product_weight_g AS INTEGER) AS product_weight_g,
    TRY_CAST(product_length_cm AS INTEGER) AS product_length_cm,
    TRY_CAST(product_height_cm AS INTEGER) AS product_height_cm,
    TRY_CAST(product_width_cm AS INTEGER) AS product_width_cm,
    TRY_CAST(product_length_cm AS BIGINT)
        * TRY_CAST(product_height_cm AS BIGINT)
        * TRY_CAST(product_width_cm AS BIGINT) AS product_volume_cm3
FROM raw.products;
