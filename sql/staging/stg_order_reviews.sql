CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_order_reviews AS
SELECT
    CAST(review_id AS VARCHAR) AS review_id,
    CAST(order_id AS VARCHAR) AS order_id,
    TRY_CAST(review_score AS INTEGER) AS review_score,
    NULLIF(TRIM(CAST(review_comment_title AS VARCHAR)), '') AS review_comment_title,
    NULLIF(TRIM(CAST(review_comment_message AS VARCHAR)), '') AS review_comment_message,
    TRY_CAST(review_creation_date AS TIMESTAMP) AS review_creation_timestamp,
    CAST(TRY_CAST(review_creation_date AS TIMESTAMP) AS DATE) AS review_creation_date,
    TRY_CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_timestamp,
    COALESCE(
        NULLIF(TRIM(CAST(review_comment_title AS VARCHAR)), '') IS NOT NULL
        OR NULLIF(TRIM(CAST(review_comment_message AS VARCHAR)), '') IS NOT NULL,
        FALSE
    ) AS has_review_comment
FROM raw.order_reviews;
