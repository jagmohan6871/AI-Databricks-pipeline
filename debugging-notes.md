# Debugging notes

## Environment

- Local: Python 3.9, no PySpark installed. CSV generator and pytest used here.
- Target runtime: Databricks Community Edition for Delta, Spark SQL, dashboard.

## Incident 1 — Duplicate extras vs uniqueness counts

**Symptom (design, caught in review):** A naive test expected “10 uniqueness failures” because the brief said “10 rows with duplicate customer_id”.

**Root cause:** Extra rows copy existing keys. The uniqueness window flags **every** row with that key, so 10 extra customer rows → 20 failed rows (and 20 extra order rows → 40 failed rows).

**Fix:** Documented in `DATA_GENERATION_NOTES.md` and asserted in `tests/test_quality_expectations.py`. Did not change the generator to “overwrite in place,” because extra physical rows match extract-duplication better.

## Incident 2 — Null FKs would be counted twice

**Symptom:** If RI is `NOT IN parent`, null `customer_id` also fails RI, so completeness 100 + RI 100 for the same rows.

**Fix:** RI predicate is “null **or** parent exists.” Completeness owns nulls. Tests expect 80 RI failures (50 + 30 orphans only).

## Incident 3 — Spark SQL `::date` cast

**Symptom:** Draft weekly SQL used `date_trunc(...)::date`, which is PostgreSQL-style and can fail on Spark.

**Fix:** `CAST(date_trunc('WEEK', o.order_date) AS DATE)` in `src/gold/03_daily_weekly_trends.sql`.

## Incident 4 — pytest missing locally

**Symptom:** `python3 -m pytest` → no module named pytest.

**Fix:** `pip install -r requirements.txt`. Pipeline runtime still does not depend on pytest.

## Incident 5 — Path probe for Bronze

**Symptom:** Community Edition uses `/FileStore/...`; local dev uses `data/`.

**Fix:** `ingest_common._ingest` tries `MEDALLION_RAW_PATH` first, then repo `data/<file>` if the Spark read fails. Missing both raises `FileNotFoundError` with both paths.

## Incident 6 — Customer-key join explosion

**Risk:** Joining orders to `bronze_customers` on `customer_id` without `distinct` would duplicate orders for the 10 duplicated customer keys.

**Mitigation:** RI uses `select(customer_id).distinct()` (and the same for products).

## Incident 7 — Invalid Python module names (`01_quality_*.py`)

**Symptom:** `SyntaxError: invalid decimal literal` on `create_silver_tables.py` line 17 when importing on Databricks.

**Root cause:** Python cannot import modules whose names start with a digit (`from src.silver.01_quality_completeness import ...`).

**Fix:** Renamed Silver check modules to `q01_quality_completeness.py` … `q05_quality_business_logic.py` and updated imports in `create_silver_tables.py`.

## Incident 8 — Gold SQL skipped when file starts with `--`

**Symptom:** Pipeline prints `Applied 01_sales_by_product.sql` but fails with `TABLE_OR_VIEW_NOT_FOUND` for `gold_sales_by_product`.

**Root cause:** `create_gold_tables._statements()` dropped any SQL chunk whose text started with a header comment (`-- Gold: ...`), so most `CREATE OR REPLACE TABLE` statements never ran.

**Fix:** Remove the `not startswith("--")` filter on semicolon splits; comment lines are already stripped inside each chunk.

## Incident 9 — Gold CTAS via `spark.sql` on Free Edition UC

**Symptom:** After the parser fix, logs still show `Applied ...` but `gold_sales_by_product` is missing.

**Root cause:** On Free Edition Unity Catalog, `CREATE OR REPLACE TABLE ... USING DELTA AS` via `spark.sql` may not register tables where `saveAsTable` does (same path Bronze/Silver use). The runner also printed `Applied` even when zero statements parsed.

**Fix:** Gold now parses each CTAS `SELECT`, then writes with `write_delta_overwrite` (three-part `catalog.schema.table` names). Fails loudly if a SQL file parses zero statements.

## Databricks run evidence

**When:** 2026-09-12 19:19 UTC  
**Batch id:** `20260912T191900Z_1a52ebe2`  
**Command:** `src.run_pipeline.main()` on Databricks (Unity Catalog `workspace.medallion_ecommerce`)

Bronze ingest matched the generated CSVs (nothing dropped):

```text
Bronze: {
  "batch_id": "20260912T191900Z_1a52ebe2",
  "customers": 10010,
  "orders": 100020,
  "products": 500
}
```

Silver quality metrics (same batch). Failures match the injected defects: 50 null emails, 20 customer uniqueness rows, 300 order completeness rows, 40 order uniqueness rows, 80 orphan FKs. Type and business-logic checks passed 100%.

```text
Silver tables written batch_id=20260912T191900Z_1a52ebe2
+----------------+---------------------+------------+-----------+-----------+---------------+-------------------------+--------------------------+
|table_name      |check_name           |rows_checked|rows_passed|rows_failed|pass_percentage|batch_id                 |computed_at               |
+----------------+---------------------+------------+-----------+-----------+---------------+-------------------------+--------------------------+
|silver_customers|completeness         |10010       |9960       |50         |99.5005        |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_customers|uniqueness           |10010       |9990       |20         |99.8002        |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_customers|type_validation      |10010       |10010      |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_customers|referential_integrity|10010       |10010      |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_customers|business_logic       |10010       |10010      |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_products |completeness         |500         |500        |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_products |uniqueness           |500         |500        |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_products |type_validation      |500         |500        |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_products |referential_integrity|500         |500        |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_products |business_logic       |500         |500        |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_orders   |completeness         |100020      |99720      |300        |99.7001        |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_orders   |uniqueness           |100020      |99980      |40         |99.96          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_orders   |type_validation      |100020      |100020     |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_orders   |referential_integrity|100020      |99940      |80         |99.92          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
|silver_orders   |business_logic       |100020      |100020     |0          |100.0          |20260912T191900Z_1a52ebe2|2026-09-12 19:19:59.041041|
+----------------+---------------------+------------+-----------+-----------+---------------+-------------------------+--------------------------+
```

Gold write log and row counts:

```text
Silver batch: 20260912T191900Z_1a52ebe2
  wrote workspace.medallion_ecommerce.gold_sales_by_product
Applied 01_sales_by_product.sql (1 statement(s))
  wrote workspace.medallion_ecommerce.gold_revenue_by_customer
Applied 02_revenue_by_customer.sql (1 statement(s))
  wrote workspace.medallion_ecommerce.gold_daily_trends
  wrote workspace.medallion_ecommerce.gold_weekly_trends
Applied 03_daily_weekly_trends.sql (2 statement(s))
  wrote workspace.medallion_ecommerce.gold_customer_segmentation
Applied 04_customer_segmentation.sql (1 statement(s))
Gold tables:
  workspace.medallion_ecommerce.gold_sales_by_product: 500 rows
  workspace.medallion_ecommerce.gold_revenue_by_customer: 9940 rows
  workspace.medallion_ecommerce.gold_daily_trends: 1351 rows
  workspace.medallion_ecommerce.gold_weekly_trends: 196 rows
  workspace.medallion_ecommerce.gold_customer_segmentation: 4 rows
Pipeline complete.
```

**Read of the Gold counts:** `gold_revenue_by_customer` = 9,940 = 10,010 Silver customers minus 50 completeness failures minus 20 uniqueness failures (those sets do not overlap). Product sales has 500 rows (all products). Segmentation has 4 rows (Inactive / High-Value / Repeat / One-Time).

**Still open:** Databricks SQL dashboard tiles (screenshots) if not already saved. Pipeline Bronze → Silver → Gold is confirmed on the workspace.

## Code review notes

Reviewed before submission:

- Bronze does not filter or drop rows.
- Silver finalize requires **all five** flags true for PASS.
- Gold CTAS filters PASS + Completed.
- Segmentation CASE order matches `data-model.md` (Inactive first).
- No secrets in repo; emails are `@example.com` / `.test` / `.dev`.
- `bronze_ingestion_log` is append-only; curated tables overwrite (rerun-safe).
