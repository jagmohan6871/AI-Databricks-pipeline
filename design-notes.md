# Design Notes

## Architecture Overview

```text
CSV extracts (customers, orders, products)
        │
        ▼
   Bronze Delta          raw columns + ingest metadata
        │
        ▼
   Silver Delta          same grain + quality flags + quarantine views
        │
        ▼
   Gold Delta            product sales, customer revenue, trends, segments
        │
        ▼
 Databricks SQL Dashboard
```

Each layer is a separate set of scripts so the medallion contract stays visible. A thin `config` module supplies database name, input path, and a batch id.

Reruns use `overwrite` for curated tables. That is simpler than merge-on-keys on Community Edition and keeps the sample pipeline idempotent.

## Data Model & Schema

See `data-model.md`. Grain:

- Bronze/Silver customers: one row per CSV row (duplicates retained).
- Bronze/Silver orders: one row per CSV row.
- Bronze/Silver products: one row per product extract row.
- Gold sales by product: one row per `product_id`.
- Gold revenue by customer: one row per `customer_id` that exists in Silver customers (valid customer rows; duplicate customer keys excluded via uniqueness).
- Gold trends: one row per order date and per week start date.
- Gold segmentation: one row per `segment_type`.

## Bronze Layer Design

- Explicit StructType schemas; CSV read with `header=true`, `mode=PERMISSIVE`, `dateFormat=yyyy-MM-dd`.
- No filters, no imputing, no dropping duplicates.
- Added technical columns: `_source_file`, `_ingested_at`, `_batch_id`, `_input_row_count`.
- Ingestion log table `bronze_ingestion_log` stores table name, path, row count, timestamp, batch id, status.
- Fail fast if the path is missing or required columns are absent.

## Silver Layer Design

Silver copies Bronze business columns and adds:

- `completeness_pass` (boolean)
- `uniqueness_pass`
- `type_validation_pass`
- `referential_integrity_pass`
- `business_logic_pass`
- `quality_failure_reasons` (semicolon-separated codes)
- `quality_check_result` (`PASS` / `FAIL`)

Quarantine is a view (or table) of `quality_check_result = 'FAIL'`. Valid is the complement. Nothing is deleted.

Quality metrics land in `silver_quality_metrics` with checked/passed/failed counts and pass percentage per check per table.

## Gold Layer Design

Gold reads `silver_orders` where `quality_check_result = 'PASS'` and `order_status = 'Completed'`, joined to passing customers and products.

- **Sales by product:** counts and revenue at product grain.
- **Revenue by customer:** orders, revenue, average order value, actual lifetime value.
- **Daily / weekly trends:** order_count, revenue, AOV by day and ISO week.
- **Customer segmentation:** mutually exclusive buckets (see `data-model.md`).

## Data Quality Validation Strategy

Documented in `data-quality-strategy.md`. Tests assert the injected defect counts in the CSVs and that Silver SQL predicates would classify those rows as failures.

## Debugging Approach

1. Reproduce with the deterministic CSVs.
2. Count rows at each layer and compare to the generation notes.
3. Isolate the failing check with the quality metrics table and `quality_failure_reasons`.
4. Fix the code, rerun the single layer, then a full overwrite run.
5. Record the incident in `debugging-notes.md`.
