-- Model: stg_orders
-- Purpose: Cleaned and typed orders from raw source
-- Owner: analytics-team
WITH source AS (
    SELECT * FROM {{ source('raw', 'ORDERS') }}
),
renamed AS (
    SELECT
        ORDER_ID                            AS order_id,
        CUSTOMER_ID                         AS customer_id,
        PRODUCT_ID                          AS product_id,
        ORDER_DATE                          AS order_date,
        UPPER(STATUS)                       AS status,
        TOTAL_AMOUNT                        AS total_amount,
        REGION                              AS region,
        QUANTITY                            AS quantity,
        CREATED_AT                          AS created_at
    FROM source
)
SELECT * FROM renamed