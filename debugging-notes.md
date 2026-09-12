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

## What was not executed here

Full Spark/Delta overwrite and the Databricks SQL dashboard **must be executed on Databricks**. Local evidence is CSV tests (15 passed) plus static review of SQL/Python. Record warehouse query results and dashboard screenshots in this file after the CE run.

## Code review notes

Reviewed before submission:

- Bronze does not filter or drop rows.
- Silver finalize requires **all five** flags true for PASS.
- Gold CTAS filters PASS + Completed.
- Segmentation CASE order matches `data-model.md` (Inactive first).
- No secrets in repo; emails are `@example.com` / `.test` / `.dev`.
- `bronze_ingestion_log` is append-only; curated tables overwrite (rerun-safe).
