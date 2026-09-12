"""Completeness: critical fields are populated."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def customers_completeness(df: DataFrame) -> DataFrame:
    email_ok = F.col("email").isNotNull() & (F.length(F.trim(F.col("email"))) > 0)
    return df.withColumn("completeness_pass", email_ok).withColumn(
        "completeness_reasons",
        F.when(~email_ok, F.lit("NULL_EMAIL")).otherwise(F.lit(None)),
    )


def orders_completeness(df: DataFrame) -> DataFrame:
    cust_ok = F.col("customer_id").isNotNull()
    prod_ok = F.col("product_id").isNotNull()
    reasons = F.concat_ws(
        ";",
        F.when(~cust_ok, F.lit("NULL_CUSTOMER_ID")),
        F.when(~prod_ok, F.lit("NULL_PRODUCT_ID")),
    )
    return df.withColumn("completeness_pass", cust_ok & prod_ok).withColumn(
        "completeness_reasons", F.when(F.length(reasons) > 0, reasons)
    )


def products_completeness(df: DataFrame) -> DataFrame:
    id_ok = F.col("product_id").isNotNull()
    name_ok = F.col("product_name").isNotNull() & (
        F.length(F.trim(F.col("product_name"))) > 0
    )
    reasons = F.concat_ws(
        ";",
        F.when(~id_ok, F.lit("NULL_PRODUCT_ID")),
        F.when(~name_ok, F.lit("NULL_PRODUCT_NAME")),
    )
    return df.withColumn("completeness_pass", id_ok & name_ok).withColumn(
        "completeness_reasons", F.when(F.length(reasons) > 0, reasons)
    )
