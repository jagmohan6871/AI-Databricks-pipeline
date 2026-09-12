"""Optional Spark integration tests. Skipped when PySpark/Delta is unavailable."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("pyspark")

from pyspark.sql import SparkSession


@pytest.fixture(scope="module")
def spark():
    try:
        session = (
            SparkSession.builder.master("local[2]")
            .appName("medallion-tests")
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.sql.shuffle.partitions", "2")
            .getOrCreate()
        )
        yield session
        session.stop()
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Spark session could not start: {exc}")


def test_bronze_cast_empty_string_to_null(spark, tmp_path: Path) -> None:
    from src.bronze.schemas import ORDER_REQUIRED, cast_orders, read_csv_raw

    csv_path = tmp_path / "orders.csv"
    csv_path.write_text(
        "order_id,customer_id,order_date,product_id,quantity,unit_price,total_amount,order_status,payment_date\n"
        "1,,2024-01-01,1,1,10.00,10.00,Completed,2024-01-01\n",
        encoding="utf-8",
    )
    df = cast_orders(read_csv_raw(spark, str(csv_path), ORDER_REQUIRED))
    row = df.collect()[0]
    assert row.order_id == 1
    assert row.customer_id is None


def test_uniqueness_flags_both_duplicate_rows(spark) -> None:
    from src.silver.02_quality_uniqueness import orders_uniqueness

    df = spark.createDataFrame(
        [(1,), (1,), (2,)],
        schema="order_id int",
    )
    out = orders_uniqueness(df).orderBy("order_id")
    flags = [(r.order_id, r.uniqueness_pass) for r in out.collect()]
    assert flags == [(1, False), (1, False), (2, True)]
