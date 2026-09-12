# Task breakdown (as given to Cursor)

Work the evaluation in this order. Do not start Gold before Silver flags exist.

1. **Foundation** — Write requirements, design, data model, DQ strategy, Cursor context files, `.cursorrules`.
2. **Sample data** — Deterministic generator; exact defect counts; notes file; write CSVs.
3. **Bronze** — Shared config/spark helpers; three ingest scripts + `ingest_all.py`; schema SQL; setup notes.
4. **Silver** — Five check modules + `create_silver_tables.py`; metrics table; valid/quarantine views.
5. **Gold** — Four SQL aggregations + `create_gold_tables.py`.
6. **Dashboard** — 3+ visualization queries and a Databricks SQL setup guide.
7. **Tests** — CSV defect tests; quality expectation tests; optional Spark tests if runtime exists.
8. **Lifecycle wrap** — Prompt history, debugging notes, reflection, README, final AI usage summary.

Prompt style for each task:

> Implement only `<file>`. Follow `data-quality-strategy.md`. Do not drop rows. Do not add dependencies.
