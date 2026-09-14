# Reflection

**Candidate:** Jagmohan Singh  
**Role:** Data Engineer  
**Primary AI tool:** Cursor  
**Technology:** Python, PySpark, Spark SQL, Delta Lake, Databricks  
**Repository:** https://github.com/jagmohan6871/AI-Databricks-pipeline

---

# Part A — Required reflection template

## What I Built

- A Databricks medallion pipeline (Bronze → Silver → Gold → Dashboard) for synthetic e-commerce sales.
- Deterministic sample CSVs: 10,010 customers, 100,020 orders, 500 products, with the documented intentional quality issues.
- Bronze ingest with explicit schemas, metadata, and no cleaning.
- Silver quality checks (completeness, uniqueness, type validation, referential integrity, business logic) that **flag** bad rows instead of deleting them, plus `silver_quality_metrics`.
- Gold tables: sales by product, revenue by customer, daily/weekly trends, customer segmentation.
- Published Databricks SQL dashboard **Ecommerce Medallion — Sales** (top products bar, revenue histogram, segmentation pie).
- Tests, README, prompt history, design notes, and debugging notes in the same repository.

## How I Used AI (Across the Lifecycle)

- Used Cursor with persistent context (`.cursorrules`, spec, requirements, data-quality strategy).
- Worked one layer at a time: data generation → Bronze → Silver → Gold → dashboard → docs.
- Used AI for requirement analysis (contradictions in the brief), design (flag vs delete, Gold filters), code generation (PySpark/SQL), tests, debugging, and documentation.
- Did not send real PII, credentials, or production secrets to the tool.
- Recorded prompts, accepts, changes, and rejects in `ai-prompts/`.

## What AI Helped With Most

- Turning the brief’s conflicting “3 vs 4” lists into an explicit decision table.
- Boilerplate: schemas, Delta overwrite, metrics union, README structure.
- First-pass completeness and uniqueness window functions.
- Drafting Gold SQL and dashboard queries.

## What AI Got Wrong

- Treating “10 duplicate customer_id rows” as 10 uniqueness failures (misses the paired originals; actual uniqueness failures = 20).
- PostgreSQL `::date` in Spark SQL.
- A messy first draft of `_finalize` with dead flag logic.
- Occasional suggestions to drop quarantined rows before Gold.
- Suggesting extra libraries (`faker`) that were not needed.
- Python modules named `01_quality_*.py` that cannot be imported; Gold SQL skipped when files started with `--`.

## How I Validated AI Output

- Hand-traced uniqueness windows and RI joins against `DATA_GENERATION_NOTES.md`.
- Local `pytest` on CSVs (17 non-Spark tests passed).
- Static review of Gold filters (`quality_check_result = 'PASS'` and `order_status = 'Completed'`) and segmentation CASE order.
- Databricks run `20260912T191900Z_1a52ebe2`: Bronze/Silver/Gold counts matched expected defects (see `debugging-notes.md`).
- Compared Silver metrics to injected issues (50 null emails, 20 customer uniqueness rows, 300 order completeness, 40 order uniqueness, 80 orphans).
- Rejected suggestions that did not match the architecture.

## What I Would Improve Next

- Delta MERGE and a watermark for incremental daily loads instead of full overwrite.
- Append-only history for `silver_quality_metrics`.
- Dashboard tile for quarantine reasons (`quality_failure_reasons`).
- DLT expectations or a maintained DQ framework if the workspace supports it.
- Automated Spark/Delta tests in CI.
- Parameterized Gold thresholds and a table widget so tiny One-Time/Inactive pie slices are readable.

## Reusable Workflow

Spec → Cursor rules → one module per prompt → tests against known defect counts → record accept/reject in `ai-prompts/` → overwrite-rerun on Databricks → dashboard SQL last.

Production would also need CI/CD, observability, incremental processing, access control, and operational runbooks.

---

# Part B — Company form questions

## Your understanding of the medallion architecture problem

The e-commerce company receives daily CSV extracts from customer, order, and product systems. Stakeholders need trustworthy sales metrics and a dashboard while the original source data remains auditable. I implemented each medallion layer as a clear contract:

- **Bronze:** ingest all three CSVs into Delta tables with explicit schemas and ingestion metadata. No records are cleaned, filtered, or deduplicated.
- **Silver:** apply completeness, uniqueness, type validation, referential integrity, and additional business-logic checks. Invalid records are retained and flagged with check results and reason codes. Nothing is deleted.
- **Gold:** use only Silver rows that passed quality checks and represent Completed orders to create sales by product, revenue by customer, daily/weekly trends, and customer segmentation.
- **Dashboard:** expose business-friendly Databricks SQL visualizations for top products, customer revenue distribution, and customer segmentation.

I generated synthetic data with a fixed seed and intentional quality problems so that the Silver checks could be tested against known expected results.

## How you used AI across data generation, ingestion, validation, aggregation

I used Cursor throughout the lifecycle, but I did not ask it to generate one large notebook. I first created a specification, requirements analysis, data model, quality strategy, and persistent Cursor rules. I then gave Cursor focused prompts for one layer or module at a time.

- **Data generation:** Cursor helped draft the deterministic generator. I kept the Python standard library, seed 42, and non-overlapping slices for null keys, orphan keys, and duplicate rows.
- **Ingestion (Bronze):** Cursor helped draft the CSV reader, explicit casts, metadata columns, Delta writes, error handling, and ingestion log. I ensured Bronze did not perform business cleaning.
- **Validation (Silver):** Cursor helped draft the five check modules and metrics report. I corrected the final PASS logic, made null foreign keys belong to completeness rather than referential integrity, and used distinct parent keys to prevent join multiplication.
- **Aggregation (Gold):** Cursor helped draft the aggregation SQL. I reviewed the aggregation grain, kept inactive customers through a left join, and corrected SQL/runtime compatibility issues found during Databricks execution.
- **Dashboard:** Cursor helped write the SQL tiles and Databricks setup guide. I configured bar, histogram, and pie charts in the workspace UI and kept a screenshot in the repo.

## Key design and implementation decisions made through AI

| Decision | Why I kept or changed it |
| --- | --- |
| Implement five Silver modules and four Gold outputs | The brief contains inconsistent “three/four” wording. Cursor listed both; I followed the stricter required repository structure. |
| Flag and retain invalid Silver rows | Cursor sometimes suggested dropping failures. I rejected that. Silver flags; Gold filters to PASS. |
| Gold uses PASS and Completed orders | Business reporting should exclude invalid, cancelled, and pending transactions while Silver still retains them. |
| Null foreign keys fail completeness, not referential integrity | Cursor’s first RI check would have counted the same nulls twice. I skipped RI when the FK is null. |
| Flag every row sharing a duplicate key | Cursor treated “10 duplicate rows” as 10 failures. I corrected this: ten extra copies mean twenty uniqueness failures. |
| Overwrite curated layer tables for this exercise | Makes reruns deterministic and idempotent on the Databricks exercise environment. |
| Mutually exclusive segmentation order | Inactive → High-Value → Repeat → One-Time so each customer belongs to one segment. |
| No Faker / extra libraries | Cursor suggested Faker. I rejected it to stay standard-library and Community Edition friendly. |

## Your testing and validation approach

I combined local deterministic tests with an end-to-end Databricks run.

**Local:** `pytest` on generated CSVs. The suite validated row counts (10,010 / 100,020 / 500), exact intentional defects, non-overlapping issue sets, duplicate-key behavior, and Gold SQL contracts. Seventeen non-Spark tests passed.

**Databricks batch `20260912T191900Z_1a52ebe2`:** Bronze loaded 10,010 customers, 100,020 orders, and 500 products without dropping records. Silver reported the expected failures:

- Customers: 50 completeness failures and 20 uniqueness failures.
- Orders: 300 completeness failures, 40 uniqueness failures, and 80 referential-integrity failures.
- Products: all quality checks passed.
- Type-validation and business-logic checks passed 100% on generated rows.

Gold produced 500 product rows, 9,940 customer rows, 1,351 daily trend rows, 196 weekly trend rows, and four segmentation rows.

**Dashboard:** published **Ecommerce Medallion — Sales** with a top-products bar, revenue histogram, revenue buckets, and customer-segmentation pie. Screenshot: `src/dashboard/screenshots/ecommerce-medallion-sales.png`. Repeat (~55%) and High-Value (~45%) dominate because most valid customers have many completed orders.

## How you validated AI output

I treated AI output as a draft and reviewed logic before accepting it. I:

- Traced uniqueness windows and referential-integrity joins against known defect counts.
- Corrected the assumption that ten extra duplicate rows create only ten uniqueness failures.
- Replaced PostgreSQL-style `::date` syntax with a Spark-compatible `CAST(date_trunc(...) AS DATE)`.
- Renamed Python modules beginning with digits (`01_quality_*.py`) because they could not be imported on Databricks.
- Fixed Gold SQL parsing when leading comments caused statements to be skipped.
- Adjusted Gold table writes for the Databricks Unity Catalog runtime and verified every resulting table count.
- Compared the final Silver metrics to the intentional defects rather than checking only that tables contained data.
- Rejected suggestions that dropped quarantined rows or added unnecessary libraries.

The repository records real prompt summaries, accepted suggestions, corrections, and rejected suggestions under `ai-prompts/` and `debugging-notes.md`.

## What you'd improve next

- Use Delta MERGE and a watermark for incremental daily loads instead of full overwrite.
- Keep Silver quality metrics as append-only history for trend monitoring.
- Add a dashboard tile showing quarantine reasons (`quality_failure_reasons`) and quality trends by batch.
- Use DLT expectations or a maintained data-quality framework if the target workspace supports it.
- Add automated Spark/Delta integration tests to CI.
- Parameterize Gold business thresholds and customer segmentation rules.
- Add a small table widget next to the pie so One-Time and Inactive counts are easy to read.
