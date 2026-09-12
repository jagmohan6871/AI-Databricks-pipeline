"""Uniqueness: flag every row whose business key appears more than once."""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F


def _flag_duplicates(df: DataFrame, key: str, reason: str) -> DataFrame:
    window = Window.partitionBy(key)
    key_present = F.col(key).isNotNull()
    dup = key_present & (F.count(F.lit(1)).over(window) > 1)
    # Null keys are completeness issues, not uniqueness.
    return df.withColumn("uniqueness_pass", ~dup).withColumn(
        "uniqueness_reasons", F.when(dup, F.lit(reason))
    )


def customers_uniqueness(df: DataFrame) -> DataFrame:
    return _flag_duplicates(df, "customer_id", "DUP_CUSTOMER_ID")


def orders_uniqueness(df: DataFrame) -> DataFrame:
    return _flag_duplicates(df, "order_id", "DUP_ORDER_ID")


def products_uniqueness(df: DataFrame) -> DataFrame:
    return _flag_duplicates(df, "product_id", "DUP_PRODUCT_ID")
