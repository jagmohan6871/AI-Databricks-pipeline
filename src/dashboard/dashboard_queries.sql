-- Databricks SQL dashboard queries
-- Bind :segment and :start_date / :end_date as dashboard widgets when supported.

-- Tile 1: Top 10 products by revenue (bar)
SELECT
  product_name,
  category,
  total_revenue,
  total_orders,
  avg_order_value
FROM medallion_ecommerce.gold_sales_by_product
ORDER BY total_revenue DESC
LIMIT 10;

-- Tile 2: Customer revenue distribution (histogram)
-- Use total_revenue as the histogram numeric column in the visualization UI.
SELECT
  customer_id,
  customer_name,
  customer_segment,
  total_revenue
FROM medallion_ecommerce.gold_revenue_by_customer
WHERE total_orders > 0;

-- Tile 3: Customer segmentation (pie)
-- Color = segment_type, Angle = customer_count
SELECT
  segment_type,
  customer_count,
  total_revenue,
  avg_revenue
FROM workspace.medallion_ecommerce.gold_customer_segmentation
ORDER BY customer_count DESC;

-- Tile 3b (optional table): makes tiny One-Time / Inactive counts readable
SELECT
  segment_type,
  customer_count,
  total_revenue,
  avg_revenue
FROM workspace.medallion_ecommerce.gold_customer_segmentation
ORDER BY customer_count DESC;

-- Tile 4 (extra): Daily revenue trend (line)
SELECT
  order_date,
  total_orders,
  total_revenue,
  avg_order_value
FROM medallion_ecommerce.gold_daily_trends
WHERE order_date BETWEEN COALESCE(:start_date, DATE '2023-01-01') AND COALESCE(:end_date, DATE '2026-09-12')
ORDER BY order_date;

-- Optional filter query: revenue by declared customer_segment (not Gold segment_type)
SELECT
  customer_segment,
  COUNT(*) AS customers,
  CAST(SUM(total_revenue) AS DECIMAL(18, 2)) AS total_revenue
FROM medallion_ecommerce.gold_revenue_by_customer
WHERE customer_segment = COALESCE(:segment, customer_segment)
GROUP BY customer_segment
ORDER BY total_revenue DESC;
