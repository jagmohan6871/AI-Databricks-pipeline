# Reflection

## What I built

A Databricks-oriented medallion pipeline for synthetic e-commerce sales: deterministic CSV generation with ~700-class quality issues, Bronze ingest with metadata, Silver flag-and-retain quality checks plus a metrics table, four Gold aggregations, dashboard SQL, and CSV-level tests. Lifecycle docs and prompt history sit next to the code.

## How I used AI (across the lifecycle)

Cursor drafted repository layout, PySpark helpers, quality-check modules, Gold SQL, and documentation skeletons against a written spec (`.cursorrules`, `requirements-analysis.md`, `data-quality-strategy.md`). I specified file paths and invariants per task rather than asking for one giant notebook. I rejected extra libraries (`faker`) and Unity Catalog-only APIs.

## What AI helped with most

- Turning the brief’s conflicting “3 vs 4” lists into an explicit decision table.
- Boilerplate: schemas, Delta overwrite, metrics union.
- First-pass completeness/uniqueness window functions.

## What AI got wrong

- Treating “10 duplicate customer_id rows” as 10 uniqueness failures (misses the paired originals).
- PostgreSQL `::date` in Spark SQL.
- A messy first draft of `_finalize` with dead flag logic that had to be deleted.
- Occasional suggestions to drop quarantined rows before Gold, which violates the brief.

## How I validated AI output

- Hand-traced uniqueness and RI predicates.
- `pytest` on generated CSVs (15 tests passed locally).
- Static review of Gold filters (`PASS` + `Completed`) and segmentation CASE order.
- Remaining validation is a clean Databricks Community Edition run (Spark/Delta/dashboard), which cannot be faked from this laptop without PySpark.

## What I would improve next

- Delta `MERGE` for incremental daily loads instead of full overwrite.
- Quarantine reason dashboard tile driven by `quality_failure_reasons`.
- Great Expectations or DLT expectations if the workspace supports them.
- Store quality metrics as append-only history rather than overwrite.

## Reusable workflow

Spec → Cursor rules → one module per prompt → tests against known defect counts → record accept/reject in `ai-prompts/` → overwrite-rerun on Databricks → dashboard SQL last.
