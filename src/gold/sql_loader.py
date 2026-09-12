"""Parse Gold SQL files without Spark dependencies."""

from __future__ import annotations

import re

CTAS_USING_DELTA = re.compile(
    r"CREATE\s+OR\s+REPLACE\s+TABLE\s+(?P<table>[^\s]+)\s+USING\s+DELTA\s+AS\s+(?P<select>.+)",
    re.IGNORECASE | re.DOTALL,
)


def parse_gold_statements(sql_text: str, database: str) -> list[str]:
    text = sql_text.replace("${DATABASE}", database)
    parts = [p.strip() for p in re.split(r";\s*", text) if p.strip()]
    cleaned: list[str] = []
    for part in parts:
        lines = [ln for ln in part.splitlines() if not ln.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if stmt:
            cleaned.append(stmt)
    return cleaned


def parse_ctas_statement(stmt: str) -> tuple[str, str]:
    match = CTAS_USING_DELTA.match(stmt.strip())
    if not match:
        raise ValueError(f"Unsupported Gold SQL (expected CTAS): {stmt[:120]}...")
    return match.group("table"), match.group("select").strip()


def qualify_table_ref(table_ref: str, catalog: str, schema: str) -> str:
    parts = table_ref.split(".")
    if len(parts) == 3:
        return table_ref
    if len(parts) == 2:
        return f"{catalog}.{table_ref}"
    if len(parts) == 1:
        return f"{catalog}.{schema}.{table_ref}"
    raise ValueError(f"Invalid table reference: {table_ref}")
