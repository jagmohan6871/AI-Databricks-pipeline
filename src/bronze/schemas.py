"""Explicit Bronze schemas and CSV readers. No business transformations."""

from __future__ import annotations

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DateType,
    DecimalType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

CUSTOMER_REQUIRED = [
    "customer_id",
    "customer_name",
    "email",
    "country",
    "signup_date",
    "customer_segment",
    "lifetime_value",
]
ORDER_REQUIRED = [
    "order_id",
    "customer_id",
    "order_date",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "order_status",
    "payment_date",
]
PRODUCT_REQUIRED = [
    "product_id",
    "product_name",
    "category",
    "price",
    "cost",
    "stock_quantity",
    "reorder_level",
]


def _string_schema(fields: list[str]) -> StructType:
    return StructType([StructField(name, StringType(), True) for name in fields])


def read_csv_raw(spark: SparkSession, path: str, fields: list[str]) -> DataFrame:
    df = (
        spark.read.format("csv")
        .option("header", "true")
        .option("multiLine", "false")
        .schema(_string_schema(fields))
        .load(path)
    )
    for col in fields:
        df = df.withColumn(
            col,
            F.when(F.trim(F.col(col)) == "", F.lit(None)).otherwise(F.col(col)),
        )
    return df


def cast_customers(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("customer_id", F.col("customer_id").cast(IntegerType()))
        .withColumn("signup_date", F.to_date("signup_date", "yyyy-MM-dd").cast(DateType()))
        .withColumn("lifetime_value", F.col("lifetime_value").cast(DecimalType(12, 2)))
    )


def cast_orders(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("order_id", F.col("order_id").cast(IntegerType()))
        .withColumn("customer_id", F.col("customer_id").cast(IntegerType()))
        .withColumn("order_date", F.to_date("order_date", "yyyy-MM-dd").cast(DateType()))
        .withColumn("product_id", F.col("product_id").cast(IntegerType()))
        .withColumn("quantity", F.col("quantity").cast(IntegerType()))
        .withColumn("unit_price", F.col("unit_price").cast(DecimalType(12, 2)))
        .withColumn("total_amount", F.col("total_amount").cast(DecimalType(12, 2)))
        .withColumn("payment_date", F.to_date("payment_date", "yyyy-MM-dd").cast(DateType()))
    )


def cast_products(df: DataFrame) -> DataFrame:
    return (
        df.withColumn("product_id", F.col("product_id").cast(IntegerType()))
        .withColumn("price", F.col("price").cast(DecimalType(12, 2)))
        .withColumn("cost", F.col("cost").cast(DecimalType(12, 2)))
        .withColumn("stock_quantity", F.col("stock_quantity").cast(IntegerType()))
        .withColumn("reorder_level", F.col("reorder_level").cast(IntegerType()))
    )
