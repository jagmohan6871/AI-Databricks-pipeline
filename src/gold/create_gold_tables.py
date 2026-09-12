"""Execute Gold SQL files against the configured database."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.config import DATABASE
from src.gold.sql_loader import parse_ctas_statement, parse_gold_statements, qualify_table_ref

SQL_DIR = Path(__file__).resolve().parent
SQL_FILES = [
    "01_sales_by_product.sql",
    "02_revenue_by_customer.sql",
    "03_daily_weekly_trends.sql",
    "04_customer_segmentation.sql",
]
GOLD_TABLES = [
    "gold_sales_by_product",
    "gold_revenue_by_customer",
    "gold_daily_trends",
    "gold_weekly_trends",
    "gold_customer_segmentation",
]


def create_gold_tables() -> None:
    from src.common.spark_utils import (
        current_catalog,
        ensure_database,
        get_spark,
        write_delta_overwrite,
    )

    spark = get_spark("gold-aggregations")
    ensure_database(spark, DATABASE)
    catalog = current_catalog(spark)

    for name in SQL_FILES:
        path = SQL_DIR / name
        sql_text = path.read_text(encoding="utf-8")
        statements = parse_gold_statements(sql_text, DATABASE)
        if not statements:
            raise RuntimeError(
                f"No SQL parsed from {name}. Pull latest repo (sql_loader.py fix) and retry."
            )
        for stmt in statements:
            table_ref, select_sql = parse_ctas_statement(stmt)
            full_name = qualify_table_ref(table_ref, catalog, DATABASE)
            result = spark.sql(select_sql)
            write_delta_overwrite(result, full_name)
            print(f"  wrote {full_name}")
        print(f"Applied {name} ({len(statements)} statement(s))")

    print("Gold tables:")
    for table in GOLD_TABLES:
        full_name = qualify_table_ref(table, catalog, DATABASE)
        n = spark.table(full_name).count()
        print(f"  {full_name}: {n} rows")


def main() -> None:
    create_gold_tables()


if __name__ == "__main__":
    main()
