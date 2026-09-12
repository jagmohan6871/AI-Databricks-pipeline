-- Medallion schema for Databricks Community Edition / Hive metastore.
-- Python ingest creates the same objects with USING DELTA; this file documents
-- the contract and can be run in a SQL warehouse before the first pipeline run.

CREATE DATABASE IF NOT EXISTS medallion_ecommerce;
USE medallion_ecommerce;

-- Bronze (raw)
CREATE TABLE IF NOT EXISTS bronze_customers (
  customer_id INT,
  customer_name STRING,
  email STRING,
  country STRING,
  signup_date DATE,
  customer_segment STRING,
  lifetime_value DECIMAL(12,2),
  _source_file STRING,
  _ingested_at TIMESTAMP,
  _batch_id STRING,
  _input_row_count BIGINT
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_orders (
  order_id INT,
  customer_id INT,
  order_date DATE,
  product_id INT,
  quantity INT,
  unit_price DECIMAL(12,2),
  total_amount DECIMAL(12,2),
  order_status STRING,
  payment_date DATE,
  _source_file STRING,
  _ingested_at TIMESTAMP,
  _batch_id STRING,
  _input_row_count BIGINT
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_products (
  product_id INT,
  product_name STRING,
  category STRING,
  price DECIMAL(12,2),
  cost DECIMAL(12,2),
  stock_quantity INT,
  reorder_level INT,
  _source_file STRING,
  _ingested_at TIMESTAMP,
  _batch_id STRING,
  _input_row_count BIGINT
) USING DELTA;

CREATE TABLE IF NOT EXISTS bronze_ingestion_log (
  table_name STRING,
  source_path STRING,
  row_count BIGINT,
  batch_id STRING,
  status STRING,
  message STRING,
  ingested_at STRING
) USING DELTA;

-- Silver quality metrics (row tables are created by PySpark with extra flag columns)
CREATE TABLE IF NOT EXISTS silver_quality_metrics (
  table_name STRING,
  check_name STRING,
  rows_checked BIGINT,
  rows_passed BIGINT,
  rows_failed BIGINT,
  pass_percentage DOUBLE,
  batch_id STRING,
  computed_at TIMESTAMP
) USING DELTA;

-- Gold
CREATE TABLE IF NOT EXISTS gold_sales_by_product (
  product_id INT,
  product_name STRING,
  category STRING,
  total_orders BIGINT,
  total_revenue DECIMAL(18,2),
  avg_order_value DECIMAL(18,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_revenue_by_customer (
  customer_id INT,
  customer_name STRING,
  customer_segment STRING,
  total_orders BIGINT,
  total_revenue DECIMAL(18,2),
  avg_order_value DECIMAL(18,2),
  lifetime_value_actual DECIMAL(18,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_daily_trends (
  order_date DATE,
  total_orders BIGINT,
  total_revenue DECIMAL(18,2),
  avg_order_value DECIMAL(18,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_weekly_trends (
  week_start_date DATE,
  iso_year INT,
  iso_week INT,
  total_orders BIGINT,
  total_revenue DECIMAL(18,2),
  avg_order_value DECIMAL(18,2)
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold_customer_segmentation (
  segment_type STRING,
  customer_count BIGINT,
  avg_revenue DECIMAL(18,2),
  total_revenue DECIMAL(18,2)
) USING DELTA;
