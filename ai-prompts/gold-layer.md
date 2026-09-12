# AI Prompts — Gold Layer

## Prompt 1: Aggregations

**PROMPT SENT:**
Create four SQL files plus `create_gold_tables.py`. Use Silver PASS and Completed orders. Segmentation CASE: Inactive, High-Value, Repeat, One-Time. Replace ${DATABASE}.

**AI RESPONSE SUMMARY:**
CTAS tables for product sales, customer revenue (left join so inactive customers remain), daily/weekly trends, segmentation from `gold_revenue_by_customer`.

**YOUR EVALUATION:**
- Accepted: left join for inactive customers; High-Value threshold 5000 revenue or 15 orders.
- Changed: `CAST(date_trunc('WEEK', ...) AS DATE)` instead of `::date`.
- Rejected: filtering Gold to “customers who ordered” only (would hide Inactive).
