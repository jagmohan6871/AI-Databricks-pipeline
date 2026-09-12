# AI Prompts — Data Generation

## Prompt 1: Generator contract

**PROMPT SENT:**
Implement `src/data_generation/generate_sample_data.py` with seed 42, standard library only. 10,000 customers, 500 products, 100,000 orders, then inject the exact defect counts from the brief on disjoint order slices. Write CSVs under `data/`.

**AI RESPONSE SUMMARY:**
Python script using `random.Random(42)`, named segments/categories, blank emails, appended duplicate rows, orphan id ranges 9_000_000 / 8_000_000.

**YOUR EVALUATION:**
- Accepted: seed, disjoint slices, extra duplicate rows, no `faker`.
- Changed: as-of date set to 2026-09-12; duplicate sources taken from clean id ranges (1001–1010, 5001–5020).
- Rejected: adding Faker or pandas.

**FINAL DECISION:** Use this generator. Document uniqueness failure shape separately.

---

## Prompt 2: Generation notes

**PROMPT SENT:**
Write `DATA_GENERATION_NOTES.md` explaining why issues exist and expected CSV row counts including extras.

**AI RESPONSE SUMMARY:**
Table of defects and 10,010 / 100,020 / 500 expected rows.

**YOUR EVALUATION:**
Accepted after adding the uniqueness “2 × extras” explanation.
