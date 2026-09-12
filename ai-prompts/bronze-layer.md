# AI Prompts — Bronze Layer

## Prompt 1: Ingest design

**PROMPT SENT:**
Create Bronze ingest scripts matching the required filenames. Explicit schemas, no cleaning, metadata columns, Delta overwrite, ingestion log, fail if path or columns missing. Configurable `MEDALLION_RAW_PATH` with local `data/` fallback.

**AI RESPONSE SUMMARY:**
Shared `ingest_common.py` plus three thin wrappers and `ingest_all.py`. Read as strings, blank → null, then cast.

**YOUR EVALUATION:**
- Accepted: string-then-cast (protects empty FK fields), overwrite + log append.
- Changed: path probe tries Spark read then falls back to repo `data/`.
- Rejected: autoloader / S3 IAM examples (out of CE scope).

---

## Prompt 2: Schema SQL

**PROMPT SENT:**
Add `database/schema.sql` documenting Delta tables for CE Hive metastore.

**AI RESPONSE SUMMARY:**
CREATE DATABASE + Bronze/Gold DDL.

**YOUR EVALUATION:**
Accepted as documentation; Python still owns `CREATE DATABASE IF NOT EXISTS` and overwriteSchema for Silver flag columns.
