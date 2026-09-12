# AI Prompts — Debugging

## Prompt 1: Uniqueness expected counts

**PROMPT SENT:**
If we append 10 duplicate customer rows, how many uniqueness failures should Silver report if we flag every row with a duplicated key?

**AI RESPONSE SUMMARY:**
20 rows (original + copy for each of 10 keys). Same pattern: 40 order uniqueness failures.

**YOUR EVALUATION:**
Accepted and encoded in tests. This was the most important correction in the project.

## Prompt 2: Local pytest

**PROMPT SENT:**
`python3 -m pytest` fails with no module named pytest. Pipeline should not require pytest on Databricks.

**AI RESPONSE SUMMARY:**
Add `requirements.txt` with pytest only; document Spark tests as optional skip.

**YOUR EVALUATION:**
Accepted.
