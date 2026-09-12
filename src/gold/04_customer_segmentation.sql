-- Gold: mutually exclusive customer segments
-- Inactive → High-Value → Repeat → One-Time

CREATE OR REPLACE TABLE ${DATABASE}.gold_customer_segmentation
USING DELTA AS
WITH scored AS (
  SELECT
    customer_id,
    total_orders,
    total_revenue,
    CASE
      WHEN total_orders = 0 THEN 'Inactive'
      WHEN total_revenue >= 5000 OR total_orders >= 15 THEN 'High-Value'
      WHEN total_orders >= 2 THEN 'Repeat'
      ELSE 'One-Time'
    END AS segment_type
  FROM ${DATABASE}.gold_revenue_by_customer
)
SELECT
  segment_type,
  COUNT(*) AS customer_count,
  CAST(AVG(total_revenue) AS DECIMAL(18, 2)) AS avg_revenue,
  CAST(SUM(total_revenue) AS DECIMAL(18, 2)) AS total_revenue
FROM scored
GROUP BY segment_type;
