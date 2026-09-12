# Requirement Analysis

## Problem Statement

An e-commerce company lands daily extracts from three systems — customers, orders, and products — as CSV files. Analytics stakeholders need trusted sales metrics and a dashboard. The pipeline must ingest the files as-is (Bronze), validate and flag quality problems without silently dropping them (Silver), publish business aggregations (Gold), and expose a small BI dashboard.

This is not only a coding exercise. The submission must make the AI-assisted engineering process visible: requirement analysis, design, prompts, testing, debugging, and reflection.

## Functional Requirements

- Generate realistic sample CSVs: ~10,000 customers, ~100,000 orders, ~500 products, with ~700 intentional quality issues.
- Bronze: ingest all three CSVs into Delta tables with explicit schemas and ingestion metadata. No cleaning.
- Silver: run completeness, uniqueness, type validation, referential integrity, and business-logic checks. Flag rows. Publish a quality metrics report with pass percentage per check.
- Gold: sales by product, revenue by customer, daily/weekly trends, customer segmentation.
- Dashboard: at least three SQL visualizations (top products bar, customer revenue histogram, segmentation pie), plus filters.
- Input validation and error handling on missing paths, missing columns, and type-unreadable files.
- README that can be followed end-to-end on Databricks Community Edition.
- At least one meaningful test tier covering data generation defects and quality-check expectations.

## Non-Functional Requirements

- Deterministic data generation (fixed seed) so quality tests are stable.
- Idempotent layer writes (overwrite by batch) so reruns do not duplicate facts.
- Readable, commented Python/SQL with a consistent naming convention (`bronze_*`, `silver_*`, `gold_*`).
- Configurable catalog/schema and input path for Community Edition vs a named schema.
- No real PII, secrets, or production connection strings.
- Community Edition compatible: Hive metastore / default database, DBFS or Workspace files, Delta tables, Databricks SQL dashboard.

## Assumptions

- Databricks Community Edition is the system of record for Spark, Delta, and the dashboard. Local Python is used for CSV generation and CSV-level tests.
- Unity Catalog may be unavailable; tables are created in a configurable database (default `medallion_ecommerce`).
- Gold metrics count **Completed** orders only, unless a query explicitly says otherwise. Cancelled and Pending orders remain in Silver for audit.
- Referential integrity is evaluated only when the foreign key is not null. Null FKs fail completeness, not RI, so defect counts stay separable.
- Duplicate key rows are extra physical CSV rows. Uniqueness flags **every** row that shares a duplicated business key.
- `lifetime_value` on the customer file is a source-system attribute. Gold `lifetime_value_actual` is the sum of completed-order revenue in this dataset.
- Dates are stored as `DATE`. `payment_date` may be null.
- File sizes in the brief are targets, not hard constraints.

## Edge Cases

- Duplicate `customer_id` / `order_id` values after ingest.
- Null `email`, `customer_id`, `product_id`.
- Orphan `customer_id` / `product_id` values that do not exist in parent tables.
- Cancelled/Pending orders with null `payment_date`.
- Completed orders missing `payment_date` (business-logic failure).
- `total_amount` not equal to `quantity * unit_price` within a 0.01 tolerance.
- Rerun of Bronze/Silver/Gold with the same input.
- Missing CSV path or unexpected columns at ingest.
- Histogram/pie queries over customers with zero completed orders.

## Clarifications Needed / Decisions Taken

The brief disagrees with itself in a few places. These decisions are explicit:

| Ambiguity | Decision |
| --- | --- |
| “All 4 quality checks” vs five Silver files | Implement four mandatory categories **plus** business logic. |
| “Three aggregation tables” vs four Gold files | Implement all four Gold outputs, including daily/weekly trends. |
| “All 4 aggregations” vs three named Gold tables | Same as above. |
| Delete vs flag bad rows | Flag and retain. Gold uses `quality_check_result = 'PASS'` only. |
| S3 vs DBFS | Configurable path; Community Edition default is DBFS `/FileStore/medallion/raw`. |
