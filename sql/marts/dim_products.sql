CREATE SCHEMA IF NOT EXISTS marts;

-- Grain: one row per product_id.
CREATE OR REPLACE TABLE marts.dim_products AS
SELECT
    p.product_id,
    p.product_category_name,
    COALESCE(t.product_category_name_english, p.product_category_name) AS product_category_name_english,
    p.product_name_length,
    p.product_description_length,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    p.product_volume_cm3
FROM staging.stg_products AS p
LEFT JOIN staging.stg_product_category_translation AS t
    ON p.product_category_name = t.product_category_name;
