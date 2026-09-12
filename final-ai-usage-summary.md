# Final AI usage summary

| Stage | Tool | How used | Human gate |
| --- | --- | --- | --- |
| Requirements | Cursor | Extract contradictions and acceptance criteria from the PDF | Wrote `requirements-analysis.md` in own words; chose stricter file-list interpretation |
| Design | Cursor | Bronze/Silver/Gold grain, flag vs delete, Gold filters | Locked RI-skips-null and uniqueness-flags-all-duplicates |
| Data generation | Cursor | Generator structure | Standard library only; fixed seed; disjoint order slices |
| Bronze | Cursor | CSV read, casts, metadata, ingest log | Fail-fast paths; no transforms |
| Silver | Cursor | Five check modules + metrics | Deleted broken `_finalize` draft; distinct keys for RI |
| Gold | Cursor | SQL aggregations | Replaced `::date`; confirmed CASE order |
| Dashboard | Cursor | Queries + CE setup guide | Required tiles have no bind parameters |
| Tests | Cursor | pytest assertions | Corrected uniqueness expected counts |
| Docs | Cursor | README and templates | Trimmed generic filler; kept honest “not run on CE yet” debugging note |

**Primary tool:** Cursor  
**What was not sent to the model:** real customer data, credentials, private workspace tokens.

**Judgment:** AI accelerated scaffolding. Ownership of grain, defect math, and Databricks compatibility stayed with the engineer.
