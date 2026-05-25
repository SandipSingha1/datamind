-- Model: stg_products
-- Purpose: Cleaned products from raw source
-- Owner: analytics-team
WITH source AS (
    SELECT * FROM {{ source('raw', 'PRODUCTS') }}
),
renamed AS (
    SELECT
        PRODUCT_ID                          AS product_id,
        PRODUCT_NAME                        AS product_name,
        CATEGORY                            AS category,
        UNIT_PRICE                          AS unit_price,
        CREATED_AT                          AS created_at
    FROM source
)
SELECT * FROM renamed