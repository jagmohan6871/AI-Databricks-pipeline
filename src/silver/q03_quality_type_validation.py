"""Type and domain validation after Bronze casts."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

VALID_SEGMENTS = ["Premium", "Standard", "Basic"]
VALID_STATUSES = ["Pending", "Completed", "Cancelled"]


def customers_types(df: DataFrame) -> DataFrame:
    id_ok = F.col("customer_id").isNotNull()
    date_ok = F.col("signup_date").isNotNull()
    segment_ok = F.col("customer_segment").isin(VALID_SEGMENTS)
    ltv_ok = F.col("lifetime_value").isNotNull() & (F.col("lifetime_value") >= 0)
    reasons = F.concat_ws(
        ";",
        F.when(~id_ok, F.lit("INVALID_CUSTOMER_ID")),
        F.when(~date_ok, F.lit("INVALID_DATE")),
        F.when(~segment_ok, F.lit("INVALID_SEGMENT")),
        F.when(~ltv_ok, F.lit("INVALID_PRICE")),
    )
    return df.withColumn(
        "type_validation_pass", id_ok & date_ok & segment_ok & ltv_ok
    ).withColumn("type_reasons", F.when(F.length(reasons) > 0, reasons))


def orders_types(df: DataFrame) -> DataFrame:
    order_id_ok = F.col("order_id").isNotNull()
    date_ok = F.col("order_date").isNotNull()
    status_ok = F.col("order_status").isin(VALID_STATUSES)
    qty_ok = F.col("quantity").isNotNull() & (F.col("quantity") > 0)
    price_ok = F.col("unit_price").isNotNull() & (F.col("unit_price") >= 0)
    amt_ok = F.col("total_amount").isNotNull() & (F.col("total_amount") >= 0)
    reasons = F.concat_ws(
        ";",
        F.when(~order_id_ok, F.lit("INVALID_ORDER_ID")),
        F.when(~date_ok, F.lit("INVALID_DATE")),
        F.when(~status_ok, F.lit("INVALID_STATUS")),
        F.when(~qty_ok, F.lit("INVALID_QUANTITY")),
        F.when(~price_ok, F.lit("INVALID_PRICE")),
        F.when(~amt_ok, F.lit("INVALID_AMOUNT")),
    )
    passed = order_id_ok & date_ok & status_ok & qty_ok & price_ok & amt_ok
    return df.withColumn("type_validation_pass", passed).withColumn(
        "type_reasons", F.when(F.length(reasons) > 0, reasons)
    )


def products_types(df: DataFrame) -> DataFrame:
    id_ok = F.col("product_id").isNotNull()
    price_ok = F.col("price").isNotNull() & (F.col("price") >= 0)
    cost_ok = F.col("cost").isNotNull() & (F.col("cost") >= 0)
    stock_ok = F.col("stock_quantity").isNotNull() & (F.col("stock_quantity") >= 0)
    reorder_ok = F.col("reorder_level").isNotNull() & (F.col("reorder_level") >= 0)
    reasons = F.concat_ws(
        ";",
        F.when(~id_ok, F.lit("INVALID_PRODUCT_ID")),
        F.when(~price_ok, F.lit("INVALID_PRICE")),
        F.when(~cost_ok, F.lit("INVALID_COST")),
        F.when(~stock_ok, F.lit("INVALID_STOCK")),
        F.when(~reorder_ok, F.lit("INVALID_STOCK")),
    )
    passed = id_ok & price_ok & cost_ok & stock_ok & reorder_ok
    return df.withColumn("type_validation_pass", passed).withColumn(
        "type_reasons", F.when(F.length(reasons) > 0, reasons)
    )
