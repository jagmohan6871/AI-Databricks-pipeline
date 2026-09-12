-- Gold: revenue by customer

CREATE OR REPLACE TABLE ${DATABASE}.gold_revenue_by_customer
USING DELTA AS
SELECT
  c.customer_id,
  c.customer_name,
  c.customer_segment,
  COALESCE(COUNT(DISTINCT o.order_id), 0) AS total_orders,
  CAST(COALESCE(SUM(o.total_amount), 0) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(
    CASE
      WHEN COUNT(DISTINCT o.order_id) = 0 THEN NULL
      ELSE SUM(o.total_amount) / COUNT(DISTINCT o.order_id)
    END AS DECIMAL(18, 2)
  ) AS avg_order_value,
  CAST(COALESCE(SUM(o.total_amount), 0) AS DECIMAL(18, 2)) AS lifetime_value_actual
FROM ${DATABASE}.silver_customers c
LEFT JOIN ${DATABASE}.silver_orders o
  ON c.customer_id = o.customer_id
 AND o.quality_check_result = 'PASS'
 AND o.order_status = 'Completed'
WHERE c.quality_check_result = 'PASS'
GROUP BY c.customer_id, c.customer_name, c.customer_segment;
