# Data Quality Strategy

## Quality Checks Overview

Thresholds are reporting targets. Rows are still flagged even if the batch is above the threshold.

### 1. Completeness Check

- **What:** No NULLs in critical fields.
- **How:**
  - customers: `email` is not null and not blank
  - orders: `customer_id` not null and `product_id` not null
  - products: `product_id` not null and `product_name` not null/blank
- **Threshold:** >99% complete
- **Result:** Flag rows that fail. Reason codes: `NULL_EMAIL`, `NULL_CUSTOMER_ID`, `NULL_PRODUCT_ID`, `NULL_PRODUCT_NAME`

### 2. Uniqueness Check

- **What:** Business keys are unique.
- **How:** Window count over `customer_id` / `order_id` / `product_id`. Flag every row whose key appears more than once.
- **Threshold:** 100% unique
- **Result:** Reason codes: `DUP_CUSTOMER_ID`, `DUP_ORDER_ID`, `DUP_PRODUCT_ID`

### 3. Type validation

- **What:** Values match the declared types and allowed domains.
- **How:**
  - IDs parse as integers (already typed after Bronze; null from corrupt CSV fails)
  - dates are not null where required (`signup_date`, `order_date`)
  - `order_status` in (`Pending`, `Completed`, `Cancelled`)
  - `customer_segment` in (`Premium`, `Standard`, `Basic`)
  - `quantity` > 0, `unit_price` ≥ 0, `stock_quantity` ≥ 0, `reorder_level` ≥ 0
- **Threshold:** >99.5% valid
- **Result:** Reason codes: `INVALID_STATUS`, `INVALID_SEGMENT`, `INVALID_QUANTITY`, `INVALID_PRICE`, `INVALID_DATE`, `INVALID_STOCK`

### 4. Referential Integrity

- **What:** Foreign keys exist in parent tables.
- **How:** Left anti-join style checks. Skip when the FK is null (completeness owns nulls).
  - `orders.customer_id` must exist in `customers.customer_id`
  - `orders.product_id` must exist in `products.product_id`
- **Threshold:** >99.9% valid
- **Result:** Reason codes: `ORPHAN_CUSTOMER_ID`, `ORPHAN_PRODUCT_ID`

### 5. Business logic (additional)

- **What:** Domain rules beyond types.
- **How:**
  - `abs(total_amount - quantity * unit_price) ≤ 0.01`
  - Completed orders must have `payment_date`
  - `payment_date` must be ≥ `order_date` when present
  - product `cost` ≤ `price`
  - `signup_date` not after the generation “today” (2026-09-12)
- **Threshold:** >99% valid
- **Result:** Reason codes: `AMOUNT_MISMATCH`, `MISSING_PAYMENT_DATE`, `PAYMENT_BEFORE_ORDER`, `COST_GT_PRICE`, `FUTURE_SIGNUP`

## Quality Metrics Report

Table `silver_quality_metrics`:

| Column | Meaning |
| --- | --- |
| table_name | silver_customers / silver_orders / silver_products |
| check_name | completeness / uniqueness / type_validation / referential_integrity / business_logic |
| rows_checked | row count |
| rows_passed | flag = true |
| rows_failed | flag = false |
| pass_percentage | 100.0 * passed / checked |
| batch_id | run id |
| computed_at | timestamp |

A batch is “healthy” when every check meets its threshold. The sample data is intentionally **not** fully healthy on completeness, uniqueness, and referential integrity for orders/customers.

## Sample Data Quality Issues

Base unique rows: 10,000 customers, 500 products, 100,000 orders.

| Issue | File | Count | Check |
| --- | --- | --- | --- |
| NULL email | customers.csv | 50 | completeness |
| Duplicate customer_id (extra rows) | customers.csv | 10 extra rows | uniqueness |
| NULL customer_id | orders.csv | 100 | completeness |
| NULL product_id | orders.csv | 200 | completeness |
| customer_id not in customers | orders.csv | 50 | referential integrity |
| product_id not in products | orders.csv | 30 | referential integrity |
| Duplicate order_id (extra rows) | orders.csv | 20 extra rows | uniqueness |

Approximate problematic **base** rows: 50 + 100 + 200 + 50 + 30 = 430 unique-issue order/customer rows, plus 10 + 20 extra duplicate rows. Duplicate extras also cause the original key rows to fail uniqueness (10 customer keys → 20 uniqueness failures; 20 order keys → 40 uniqueness failures). Final CSV row counts:

- customers: 10,010
- orders: 100,020
- products: 500

Issue sets on orders are disjoint by construction so expected counts are testable.
