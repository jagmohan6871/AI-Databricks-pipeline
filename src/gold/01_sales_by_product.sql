-- Gold: sales by product (Completed + Silver PASS orders only)

CREATE OR REPLACE TABLE ${DATABASE}.gold_sales_by_product
USING DELTA AS
SELECT
  p.product_id,
  p.product_name,
  p.category,
  COUNT(DISTINCT o.order_id) AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(SUM(o.total_amount) / COUNT(DISTINCT o.order_id) AS DECIMAL(18, 2)) AS avg_order_value
FROM ${DATABASE}.silver_orders o
INNER JOIN ${DATABASE}.silver_products p
  ON o.product_id = p.product_id
WHERE o.quality_check_result = 'PASS'
  AND p.quality_check_result = 'PASS'
  AND o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category;
