"""Execute Gold SQL files against the configured database."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.config import DATABASE
from src.common.spark_utils import ensure_database, get_spark

SQL_DIR = Path(__file__).resolve().parent
SQL_FILES = [
    "01_sales_by_product.sql",
    "02_revenue_by_customer.sql",
    "03_daily_weekly_trends.sql",
    "04_customer_segmentation.sql",
]


def _statements(sql_text: str) -> list[str]:
    text = sql_text.replace("${DATABASE}", DATABASE)
    parts = [p.strip() for p in re.split(r";\s*", text) if p.strip() and not p.strip().startswith("--")]
    cleaned = []
    for part in parts:
        lines = [ln for ln in part.splitlines() if not ln.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if stmt:
            cleaned.append(stmt)
    return cleaned


def create_gold_tables() -> None:
    spark = get_spark("gold-aggregations")
    ensure_database(spark, DATABASE)
    for name in SQL_FILES:
        path = SQL_DIR / name
        sql_text = path.read_text(encoding="utf-8")
        for stmt in _statements(sql_text):
            spark.sql(stmt)
        print(f"Applied {name}")
    print("Gold tables:")
    for table in [
        "gold_sales_by_product",
        "gold_revenue_by_customer",
        "gold_daily_trends",
        "gold_weekly_trends",
        "gold_customer_segmentation",
    ]:
        n = spark.table(f"{DATABASE}.{table}").count()
        print(f"  {table}: {n} rows")


def main() -> None:
    create_gold_tables()


if __name__ == "__main__":
    main()
