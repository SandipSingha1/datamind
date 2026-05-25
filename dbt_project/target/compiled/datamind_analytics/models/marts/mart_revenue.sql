-- Model: mart_revenue
-- Purpose: Monthly revenue aggregated by region and customer segment
-- Owner: analytics-team
WITH orders AS (
    SELECT * FROM DATAMIND_DB.DBT_DEV.fct_orders
    WHERE status = 'COMPLETED'
),
final AS (
    SELECT
        DATE_TRUNC('month', order_date)     AS revenue_month,
        region,
        customer_segment,
        COUNT(DISTINCT order_id)            AS order_count,
        COUNT(DISTINCT customer_id)         AS unique_customers,
        SUM(total_amount)                   AS total_revenue,
        AVG(total_amount)                   AS avg_order_value
    FROM orders
    GROUP BY 1, 2, 3
)
SELECT * FROM final