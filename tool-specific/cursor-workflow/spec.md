# Specification — E-commerce Medallion Pipeline

## Goal

Deliver a working Bronze → Silver → Gold → Dashboard pipeline on Databricks Community Edition, plus the evaluation’s documentation and prompt-history artifacts.

## Interfaces

- Input: `customers.csv`, `orders.csv`, `products.csv`
- Config: `src/common/config.py` (`DATABASE`, `RAW_DATA_PATH`, `BATCH_ID`)
- Output Delta tables listed in `data-model.md`

## Invariants

1. Data generator seed is `42`.
2. Order quality-issue slices do not overlap.
3. Ingest validates path and required columns, then writes Delta with overwrite.
4. Silver retains all Bronze rows.
5. `referential_integrity_pass` is true when the FK is null (completeness owns it) or when the parent key exists.
6. Gold completed-order filter is applied in SQL, not by deleting Silver rows.
7. Segmentation CASE order: Inactive → High-Value → Repeat → One-Time.

## Acceptance checks

See Core Acceptance Criteria in the evaluation brief and `README.md` validation queries.
