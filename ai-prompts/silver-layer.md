# AI Prompts — Silver Layer

## Prompt 1: Check modules

**PROMPT SENT:**
Implement five Silver files: completeness, uniqueness, type validation, referential integrity, business logic. Flag rows, do not delete. Null FKs skip RI. Uniqueness flags every row sharing a duplicated key.

**AI RESPONSE SUMMARY:**
Column-wise boolean flags and reason codes; RI left-join to distinct parent keys.

**YOUR EVALUATION:**
- Accepted: reason codes, skip-null RI, window uniqueness.
- Changed: `_finalize` rewritten to a single explicit AND of five flags (first draft had dead code).
- Rejected: dropping FAIL rows into a separate table only (we keep full Silver plus views).

---

## Prompt 2: Metrics

**PROMPT SENT:**
Write `silver_quality_metrics` with checked/passed/failed/pass_percentage per table and check.

**AI RESPONSE SUMMARY:**
`metrics_for()` counting each flag then union + overwrite.

**YOUR EVALUATION:**
Accepted. Note: uses several `.count()` actions; fine at ~100k rows on CE.
