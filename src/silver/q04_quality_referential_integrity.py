"""Referential integrity. Null FKs are skipped (completeness owns them)."""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def orders_referential_integrity(
    orders: DataFrame, customers: DataFrame, products: DataFrame
) -> DataFrame:
    customer_keys = (
        customers.select("customer_id")
        .where(F.col("customer_id").isNotNull())
        .distinct()
        .withColumnRenamed("customer_id", "valid_customer_id")
    )
    product_keys = (
        products.select("product_id")
        .where(F.col("product_id").isNotNull())
        .distinct()
        .withColumnRenamed("product_id", "valid_product_id")
    )
    df = orders.join(
        customer_keys, orders.customer_id == customer_keys.valid_customer_id, "left"
    ).join(product_keys, orders.product_id == product_keys.valid_product_id, "left")

    cust_ok = F.col("customer_id").isNull() | F.col("valid_customer_id").isNotNull()
    prod_ok = F.col("product_id").isNull() | F.col("valid_product_id").isNotNull()
    reasons = F.concat_ws(
        ";",
        F.when(
            F.col("customer_id").isNotNull() & F.col("valid_customer_id").isNull(),
            F.lit("ORPHAN_CUSTOMER_ID"),
        ),
        F.when(
            F.col("product_id").isNotNull() & F.col("valid_product_id").isNull(),
            F.lit("ORPHAN_PRODUCT_ID"),
        ),
    )
    return (
        df.withColumn("referential_integrity_pass", cust_ok & prod_ok)
        .withColumn("ri_reasons", F.when(F.length(reasons) > 0, reasons))
        .drop("valid_customer_id", "valid_product_id")
    )


def customers_referential_integrity(df: DataFrame) -> DataFrame:
    """Customers have no parent FKs in this model."""
    return df.withColumn("referential_integrity_pass", F.lit(True)).withColumn(
        "ri_reasons", F.lit(None).cast("string")
    )


def products_referential_integrity(df: DataFrame) -> DataFrame:
    return df.withColumn("referential_integrity_pass", F.lit(True)).withColumn(
        "ri_reasons", F.lit(None).cast("string")
    )
