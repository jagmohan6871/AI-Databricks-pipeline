-- Gold: daily and weekly sales trends

CREATE OR REPLACE TABLE ${DATABASE}.gold_daily_trends
USING DELTA AS
SELECT
  o.order_date,
  COUNT(DISTINCT o.order_id) AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(SUM(o.total_amount) / COUNT(DISTINCT o.order_id) AS DECIMAL(18, 2)) AS avg_order_value
FROM ${DATABASE}.silver_orders o
WHERE o.quality_check_result = 'PASS'
  AND o.order_status = 'Completed'
GROUP BY o.order_date;

CREATE OR REPLACE TABLE ${DATABASE}.gold_weekly_trends
USING DELTA AS
SELECT
  CAST(date_trunc('WEEK', o.order_date) AS DATE) AS week_start_date,
  YEAR(o.order_date) AS iso_year,
  WEEKOFYEAR(o.order_date) AS iso_week,
  COUNT(DISTINCT o.order_id) AS total_orders,
  CAST(SUM(o.total_amount) AS DECIMAL(18, 2)) AS total_revenue,
  CAST(SUM(o.total_amount) / COUNT(DISTINCT o.order_id) AS DECIMAL(18, 2)) AS avg_order_value
FROM ${DATABASE}.silver_orders o
WHERE o.quality_check_result = 'PASS'
  AND o.order_status = 'Completed'
GROUP BY
  CAST(date_trunc('WEEK', o.order_date) AS DATE),
  YEAR(o.order_date),
  WEEKOFYEAR(o.order_date);
