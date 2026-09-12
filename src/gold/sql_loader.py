"""Parse Gold SQL files without Spark dependencies."""

from __future__ import annotations

import re


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
