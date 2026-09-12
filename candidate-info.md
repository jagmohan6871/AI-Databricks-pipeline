# Candidate Information

**Name:** Jag Mohan Singh
**Role:** Data Engineer
**Primary Technology Stack:** Python / PySpark, SQL, Databricks
**Primary AI Tool Used:** Cursor
**Project Option Selected:** Data Pipeline (Medallion Architecture)
**Assessment Start Date:** 2026-09-12
**Submission Date:** 2026-09-12

## Tools & Environment

- Databricks: Community Edition (primary runtime for Spark/Delta and the SQL dashboard)
- Local: Python 3 for sample data generation and CSV-level tests
- Languages: Python, PySpark, SQL
- Libraries: PySpark, Delta Lake (Databricks runtime), Python standard library
- AI Tool: Cursor

## Setup Summary

1. Generate sample CSVs with `python src/data_generation/generate_sample_data.py`.
2. Clone or import this repository into Databricks Community Edition.
3. Copy `data/*.csv` to a DBFS/Workspace path (default: `/FileStore/medallion/raw`).
4. Run Bronze → Silver → Gold scripts in order.
5. Create a Databricks SQL dashboard from `src/dashboard/dashboard_queries.sql`.

Full commands are in `README.md`.
