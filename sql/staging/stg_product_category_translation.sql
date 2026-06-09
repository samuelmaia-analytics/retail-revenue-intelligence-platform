CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_product_category_translation AS
SELECT
    LOWER(TRIM(CAST(product_category_name AS VARCHAR))) AS product_category_name,
    LOWER(TRIM(CAST(product_category_name_english AS VARCHAR))) AS product_category_name_english
FROM raw.product_category_translation;
