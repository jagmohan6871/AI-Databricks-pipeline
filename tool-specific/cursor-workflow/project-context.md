# Cursor project context

## What this repo is

Company AI capability exercise: an e-commerce Databricks medallion pipeline with lifecycle artifacts. Not a production workload. Synthetic data only.

## Runtime

- Local Python: `src/data_generation/generate_sample_data.py` and `pytest`.
- Databricks Community Edition: Bronze/Silver/Gold Delta tables and SQL dashboard.
- Default database: `medallion_ecommerce`.
- Default raw path: `/FileStore/medallion/raw`.

## Non-negotiables

- Bronze does not clean data.
- Silver flags rows (`quality_check_result`); it does not delete.
- Gold uses Silver PASS + Completed orders.
- Intentional CSV defects must remain exactly as specified.
- Prompt history in `ai-prompts/` must be real.

## Where to look

| Topic | File |
| --- | --- |
| Requirements | `requirements-analysis.md` |
| Architecture | `design-notes.md` |
| Schemas | `data-model.md` |
| DQ rules | `data-quality-strategy.md` |
| Task list | `tool-specific/cursor-workflow/task-breakdown.md` |
| Spec | `tool-specific/cursor-workflow/spec.md` |
