# Code review notes

Reviewer: author (self-review before company submission)

## Checklist

- [x] Bronze ingest does not filter, impute, or drop duplicates
- [x] Silver retains all Bronze rows and sets `quality_check_result`
- [x] Completeness, uniqueness, type, RI, and business logic all contribute to PASS
- [x] RI uses distinct parent keys (no join explosion on duplicate customers)
- [x] Gold CTAS uses PASS + Completed (except segmentation, which reads Gold customer revenue)
- [x] Inactive customers retained via LEFT JOIN
- [x] No secrets, no real PII
- [x] README run order matches scripts
- [x] Tests lock injected defect counts and uniqueness math
- [x] Databricks CE still required for Delta + dashboard evidence

## Residual risk

Without a Community Edition execution, Delta `CREATE OR REPLACE TABLE ... USING DELTA AS` and dashboard widgets are reviewed statically only. Run `src/run_pipeline.py` on CE and paste `silver_quality_metrics` into `debugging-notes.md` before the form submission if time allows.
