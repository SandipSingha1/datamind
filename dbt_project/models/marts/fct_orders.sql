-- Model: fct_orders
-- Purpose: Order fact table — one row per order, joined with customer and product
-- Owner: analytics-team
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),
customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),
products AS (
    SELECT * FROM {{ ref('stg_products') }}
),
final AS (
    SELECT
        o.order_id,
        o.order_date,
        o.status,
        o.total_amount,
        o.quantity,
        o.region,
        c.customer_id,
        c.full_name                         AS customer_name,
        c.segment                           AS customer_segment,
        c.country,
        p.product_id,
        p.product_name,
        p.category                          AS product_category,
        p.unit_price,
        o.total_amount / NULLIF(o.quantity,0) AS avg_unit_price_paid
    FROM orders     o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN products  p ON o.product_id  = p.product_id
)
SELECT * FROM final