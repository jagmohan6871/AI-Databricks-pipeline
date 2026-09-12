"""Execute Gold SQL files against the configured database."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.config import DATABASE
from src.gold.sql_loader import parse_gold_statements

SQL_DIR = Path(__file__).resolve().parent
SQL_FILES = [
    "01_sales_by_product.sql",
    "02_revenue_by_customer.sql",
    "03_daily_weekly_trends.sql",
    "04_customer_segmentation.sql",
]


def create_gold_tables() -> None:
    from src.common.spark_utils import ensure_database, get_spark

    spark = get_spark("gold-aggregations")
    ensure_database(spark, DATABASE)
    for name in SQL_FILES:
        path = SQL_DIR / name
        sql_text = path.read_text(encoding="utf-8")
        for stmt in parse_gold_statements(sql_text, DATABASE):
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
