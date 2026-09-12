# Data Generation Notes

## Why synthetic data

The evaluation forbids real customer PII. This script builds a reproducible e-commerce extract that is large enough for aggregations and dirty enough for Silver checks.

## How it is generated

- Language: Python 3, standard library only (`csv`, `random`, `datetime`).
- Seed: `42`.
- As-of date: `2026-09-12` (workspace date for the exercise).
- Command: `python src/data_generation/generate_sample_data.py`

Customers, products, then orders. Order unit prices copy the product list price when the `product_id` exists so Gold revenue is coherent.

## Intentional quality issues

Issues exist so Silver can prove it catches them — not because a real source system would publish them on purpose. They mimic late-arriving keys, extract glitches, and duplicate CDC rows.

| Defect | Implementation | Count |
| --- | --- | --- |
| NULL email | Blank `email` on customer_id 1–50 | 50 |
| Duplicate customer_id | Extra rows copying ids 1001–1010 | 10 extra rows |
| NULL order customer_id | Base orders index 0–99 | 100 |
| NULL order product_id | Base orders index 100–299 | 200 |
| Orphan customer_id | Ids `9000000+` on orders index 300–349 | 50 |
| Orphan product_id | Ids `8000000+` on orders index 350–379 | 30 |
| Duplicate order_id | Extra rows copying ids 5001–5020 | 20 extra rows |

Order defect slices do not overlap. Duplicate extras are appended after the 100,000 base orders.

## Expected file totals

- `customers.csv`: 10,010 rows (10,000 + 10 duplicates)
- `orders.csv`: 100,020 rows (100,000 + 20 duplicates)
- `products.csv`: 500 rows

## Uniqueness failure shape

Silver flags **every** row whose business key is duplicated. Ten duplicated customer keys therefore produce 20 uniqueness failures. Twenty duplicated order keys produce 40 uniqueness failures.
