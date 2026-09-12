# Databricks SQL Dashboard Guide

This guide is written for Databricks Community Edition SQL. Exact menu labels vary slightly by runtime, but the tiles below are the acceptance set.

## Prerequisites

- Gold tables exist in `medallion_ecommerce` (`python src/gold/create_gold_tables.py` or the equivalent notebook).
- You can query them in a SQL editor:

  ```sql
  SELECT COUNT(*) FROM medallion_ecommerce.gold_sales_by_product;
  SELECT * FROM medallion_ecommerce.gold_customer_segmentation;
  ```

## Create the dashboard

1. Open **SQL Editor** (or **Dashboards** if your CE workspace has the newer dashboard experience).
2. Create a dashboard named `Ecommerce Medallion — Sales`.
3. Add parameters if available: `segment` (string), `start_date` (date), `end_date` (date).
4. Add at least three visualizations from `src/dashboard/dashboard_queries.sql`.

## Tiles (required)

| Tile | Query | Visualization | Notes |
| --- | --- | --- | --- |
| Top 10 products by revenue | First query (LIMIT 10) | Bar: X = `product_name`, Y = `total_revenue` | Sort desc already in SQL |
| Customer revenue distribution | Second query | Histogram on `total_revenue` | If histogram is missing, use a bar of revenue buckets via `width_bucket` |
| Customer segmentation | Third query | Pie: slice = `segment_type`, value = `customer_count` | |

## Extra tiles (recommended)

- Daily revenue line chart from `gold_daily_trends`.
- Filter bar: Premium / Standard / Basic from `gold_revenue_by_customer.customer_segment`.

## Filters

- Date range on the daily trend tile (`order_date`).
- Segment dropdown on the customer-segment attribute (source system), independent of Gold `segment_type`.

## Evidence for submission

Published workspace dashboard: **Ecommerce Medallion — Sales**.

Screenshot in-repo: `src/dashboard/screenshots/ecommerce-medallion-sales.png` (2026-09-12).

After the dashboard renders:

1. Export or screenshot the three required tiles.
2. Note the screenshot path in `debugging-notes.md` / reflection.
3. If CE cannot persist dashboards, keep the SQL files and a screenshot of query results as the fallback and say so honestly in `reflection.md`.

## Histogram fallback SQL

```sql
SELECT
  CASE
    WHEN total_revenue < 100 THEN '0-99'
    WHEN total_revenue < 500 THEN '100-499'
    WHEN total_revenue < 2000 THEN '500-1999'
    WHEN total_revenue < 5000 THEN '2000-4999'
    ELSE '5000+'
  END AS revenue_bucket,
  COUNT(*) AS customers
FROM medallion_ecommerce.gold_revenue_by_customer
WHERE total_orders > 0
GROUP BY 1
ORDER BY 1;
```
