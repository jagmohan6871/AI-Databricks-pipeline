"""Business-logic checks beyond types and keys."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def customers_business_logic(df: DataFrame, as_of_date: str) -> DataFrame:
    signup_ok = F.col("signup_date").isNull() | (F.col("signup_date") <= F.lit(as_of_date))
    return df.withColumn("business_logic_pass", signup_ok).withColumn(
        "business_reasons",
        F.when(~signup_ok, F.lit("FUTURE_SIGNUP")),
    )


def orders_business_logic(df: DataFrame) -> DataFrame:
    amount_ok = F.abs(
        F.col("total_amount") - (F.col("quantity") * F.col("unit_price"))
    ) <= F.lit(0.01)
    # Null amount/qty already fail type checks; treat null math as fail here too.
    amount_ok = amount_ok & F.col("total_amount").isNotNull()

    payment_required_ok = (F.col("order_status") != F.lit("Completed")) | F.col(
        "payment_date"
    ).isNotNull()
    payment_order_ok = (
        F.col("payment_date").isNull() | F.col("order_date").isNull()
    ) | (F.col("payment_date") >= F.col("order_date"))

    reasons = F.concat_ws(
        ";",
        F.when(~amount_ok, F.lit("AMOUNT_MISMATCH")),
        F.when(~payment_required_ok, F.lit("MISSING_PAYMENT_DATE")),
        F.when(~payment_order_ok, F.lit("PAYMENT_BEFORE_ORDER")),
    )
    passed = amount_ok & payment_required_ok & payment_order_ok
    return df.withColumn("business_logic_pass", passed).withColumn(
        "business_reasons", F.when(F.length(reasons) > 0, reasons)
    )


def products_business_logic(df: DataFrame) -> DataFrame:
    cost_ok = (
        F.col("cost").isNull()
        | F.col("price").isNull()
        | (F.col("cost") <= F.col("price"))
    )
    return df.withColumn("business_logic_pass", cost_ok).withColumn(
        "business_reasons", F.when(~cost_ok, F.lit("COST_GT_PRICE"))
    )
