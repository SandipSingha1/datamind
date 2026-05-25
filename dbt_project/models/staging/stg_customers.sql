-- Model: stg_customers
-- Purpose: Cleaned customers from raw source
-- Owner: analytics-team
WITH source AS (
    SELECT * FROM {{ source('raw', 'CUSTOMERS') }}
),
renamed AS (
    SELECT
        CUSTOMER_ID                         AS customer_id,
        FIRST_NAME || ' ' || LAST_NAME      AS full_name,
        LOWER(EMAIL)                        AS email,
        SEGMENT                             AS segment,
        COUNTRY                             AS country,
        CREATED_AT                          AS created_at
    FROM source
)
SELECT * FROM renamed