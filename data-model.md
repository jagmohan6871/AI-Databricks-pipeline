# Data Model

## Databases and tables

Default database: `medallion_ecommerce`

| Layer | Table / view | Grain |
| --- | --- | --- |
| Bronze | `bronze_customers` | CSV row |
| Bronze | `bronze_orders` | CSV row |
| Bronze | `bronze_products` | CSV row |
| Bronze | `bronze_ingestion_log` | ingest event |
| Silver | `silver_customers` | CSV row + flags |
| Silver | `silver_orders` | CSV row + flags |
| Silver | `silver_products` | CSV row + flags |
| Silver | `silver_quality_metrics` | table × check × batch |
| Silver | `silver_orders_valid` (view) | passing orders |
| Silver | `silver_orders_quarantine` (view) | failing orders |
| Gold | `gold_sales_by_product` | product_id |
| Gold | `gold_revenue_by_customer` | customer_id |
| Gold | `gold_daily_trends` | order_date |
| Gold | `gold_weekly_trends` | week_start_date |
| Gold | `gold_customer_segmentation` | segment_type |

## Source columns

### customers

| Column | Type | Notes |
| --- | --- | --- |
| customer_id | INT | business key; duplicates injected |
| customer_name | STRING | |
| email | STRING | 50 nulls injected |
| country | STRING | |
| signup_date | DATE | 2020-01-01 .. 2026-09-12 |
| customer_segment | STRING | Premium / Standard / Basic |
| lifetime_value | DECIMAL(12,2) | source-system LTV |

### orders

| Column | Type | Notes |
| --- | --- | --- |
| order_id | INT | business key; duplicates injected |
| customer_id | INT | FK to customers; nulls and orphans injected |
| order_date | DATE | |
| product_id | INT | FK to products; nulls and orphans injected |
| quantity | INT | |
| unit_price | DECIMAL(12,2) | |
| total_amount | DECIMAL(12,2) | quantity × unit_price |
| order_status | STRING | Pending / Completed / Cancelled |
| payment_date | DATE | null for non-completed |

### products

| Column | Type | Notes |
| --- | --- | --- |
| product_id | INT | PK |
| product_name | STRING | |
| category | STRING | |
| price | DECIMAL(12,2) | list price |
| cost | DECIMAL(12,2) | |
| stock_quantity | INT | |
| reorder_level | INT | |

## Technical columns (Bronze+)

`_source_file`, `_ingested_at`, `_batch_id`

## Quality columns (Silver)

Boolean pass flags for five checks, `quality_failure_reasons`, `quality_check_result`.

## Gold measures

- `total_orders`: count of distinct passing completed `order_id`
- `total_revenue`: sum of `total_amount`
- `avg_order_value`: `total_revenue / total_orders` (null if no orders)
- `lifetime_value_actual`: same as `total_revenue` for that customer in this dataset

### Customer segment_type (mutually exclusive, first match)

1. **Inactive** — zero completed passing orders
2. **High-Value** — completed revenue ≥ 5000 **or** completed order count ≥ 15
3. **Repeat** — completed order count ≥ 2
4. **One-Time** — exactly one completed order
