CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.stg_geolocation AS
SELECT
    CAST(geolocation_zip_code_prefix AS VARCHAR) AS zip_prefix,
    AVG(TRY_CAST(geolocation_lat AS DOUBLE)) AS latitude,
    AVG(TRY_CAST(geolocation_lng AS DOUBLE)) AS longitude,
    LOWER(TRIM(CAST(geolocation_city AS VARCHAR))) AS city,
    UPPER(TRIM(CAST(geolocation_state AS VARCHAR))) AS state
FROM raw.geolocation
GROUP BY
    CAST(geolocation_zip_code_prefix AS VARCHAR),
    LOWER(TRIM(CAST(geolocation_city AS VARCHAR))),
    UPPER(TRIM(CAST(geolocation_state AS VARCHAR)));
