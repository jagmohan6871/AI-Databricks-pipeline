# Databricks Medallion Pipeline — E-commerce Sales

AI-assisted Bronze → Silver → Gold → Dashboard pipeline for the data-engineering capability exercise. Data is **synthetic**. The repository includes the pipeline **and** the lifecycle artifacts the evaluation asks for (requirements, design, prompt history, tests, debugging, reflection).

## What you get

| Layer | Output |
| --- | --- |
| Sample data | `data/customers.csv` (10,010), `data/orders.csv` (100,020), `data/products.csv` (500) with intentional quality issues |
| Bronze | `bronze_customers`, `bronze_orders`, `bronze_products`, `bronze_ingestion_log` |
| Silver | Flagged copies of all rows, quarantine/valid views, `silver_quality_metrics` |
| Gold | Product sales, customer revenue, daily/weekly trends, customer segmentation |
| Dashboard | SQL for 3+ Databricks visualizations |

## Prerequisites

- Python 3.9+ (local data generation and CSV tests)
- Databricks Community Edition cluster (Spark + Delta) for Bronze/Silver/Gold and the SQL dashboard
- This Git repository cloned with your **ttn email** identity (submission requirement)

You do **not** need Unity Catalog. Default database: `medallion_ecommerce`.

## Local: generate data and run tests

From the repo root:

```bash
python3 src/data_generation/generate_sample_data.py
python3 -m pip install -r requirements.txt
python3 -m pytest tests/test_data_generation.py tests/test_quality_expectations.py -q
```

Expected: **15 passed**. Spark tests in `tests/test_spark_quality.py` skip unless PySpark is installed; they are intended for Databricks or a local Spark install.

## Databricks: end-to-end run

1. Import this repo into Databricks Repos (clone with your ttn Git identity).
2. Upload the three CSVs to DBFS:

   ```
   /FileStore/medallion/raw/customers.csv
   /FileStore/medallion/raw/orders.csv
   /FileStore/medallion/raw/products.csv
   ```

3. On a cluster, in a Python notebook:

   ```python
   import os, sys
   os.environ["MEDALLION_DATABASE"] = "medallion_ecommerce"
   os.environ["MEDALLION_RAW_PATH"] = "/FileStore/medallion/raw"
   sys.path.append("/Workspace/Repos/<your-ttn-email>/<repo-name>")
   from src.run_pipeline import main
   main()
   ```

   Or run in order: `src/bronze/ingest_all.py` → `src/silver/create_silver_tables.py` → `src/gold/create_gold_tables.py`.

4. Validation queries:

   ```sql
   SELECT table_name, check_name, rows_failed, pass_percentage
   FROM medallion_ecommerce.silver_quality_metrics
   ORDER BY table_name, check_name;

   SELECT COUNT(*) FROM medallion_ecommerce.bronze_orders;          -- 100020
   SELECT COUNT(*) FROM medallion_ecommerce.silver_orders;          -- 100020 (nothing deleted)
   SELECT COUNT(*) FROM medallion_ecommerce.silver_orders_quarantine;
   SELECT * FROM medallion_ecommerce.gold_customer_segmentation;
   ```

   Expected Silver highlights (orders):

   | Check | Failed rows (approx) |
   | --- | --- |
   | completeness | 300 |
   | uniqueness | 40 |
   | referential_integrity | 80 |
   | type_validation | 0 |
   | business_logic | 0 |

   Customers: 50 completeness (null email), 20 uniqueness (10 keys × 2 rows).

5. Dashboard: follow `src/dashboard/DASHBOARD_GUIDE.md` using `src/dashboard/dashboard_queries.sql`.

Reruns overwrite curated Delta tables (idempotent). `bronze_ingestion_log` appends.

## Repository map

See the evaluation’s required layout. Extra files that still belong:

- `src/common/` — config and Spark helpers
- `src/bronze/ingest_common.py`, `schemas.py` — shared ingest
- `src/run_pipeline.py` — one-shot orchestrator
- `tests/` — CSV defect tests + optional Spark tests
- `tool-specific/cursor-workflow/` — Cursor evidence
- `.cursorrules` — persistent agent instructions

## Design choices (short)

- Silver **flags** bad rows; Gold uses `quality_check_result = 'PASS'` and `order_status = 'Completed'`.
- Null foreign keys fail **completeness**, not referential integrity.
- Duplicate extras mean uniqueness failures = 2 × extra rows.
- Four Gold outputs including daily/weekly trends (stricter reading of the brief).

Details: `requirements-analysis.md`, `design-notes.md`, `data-quality-strategy.md`.
