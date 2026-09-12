"""Shared Bronze ingest routine."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.bronze.schemas import (
    CUSTOMER_REQUIRED,
    ORDER_REQUIRED,
    PRODUCT_REQUIRED,
    cast_customers,
    cast_orders,
    cast_products,
    read_csv_raw,
)
from src.common.config import (
    CUSTOMERS_FILE,
    DATABASE,
    ORDERS_FILE,
    PRODUCTS_FILE,
    new_batch_id,
    raw_file,
    table_name,
)
from src.common.spark_utils import (
    ensure_database,
    get_spark,
    log_ingest,
    require_columns,
    write_delta_overwrite,
)


def _with_metadata(
    df: DataFrame, source_path: str, batch_id: str, row_count: int
) -> DataFrame:
    return (
        df.withColumn("_source_file", F.lit(source_path))
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_batch_id", F.lit(batch_id))
        .withColumn("_input_row_count", F.lit(row_count))
    )


def _ingest(
    spark: SparkSession,
    *,
    filename: str,
    required: list[str],
    caster,
    bronze_table: str,
    batch_id: str,
) -> int:
    source_path = raw_file(filename)
    # Allow a local override when developing outside Databricks.
    local_fallback = ROOT / "data" / filename
    path = source_path
    try:
        test_df = spark.read.format("text").load(source_path).limit(1)
        test_df.count()
    except Exception:
        if local_fallback.exists():
            path = str(local_fallback)
        else:
            raise FileNotFoundError(
                f"Raw file not found at {source_path} or {local_fallback}. "
                "Upload CSVs to MEDALLION_RAW_PATH or generate data/ locally."
            ) from None

    raw = read_csv_raw(spark, path, required)
    require_columns(raw, required, path)
    typed = caster(raw)
    row_count = typed.count()
    if row_count == 0:
        raise ValueError(f"{path} loaded zero rows")

    out = _with_metadata(typed, path, batch_id, row_count)
    full_name = table_name(bronze_table)
    write_delta_overwrite(out, full_name)
    log_ingest(
        spark,
        DATABASE,
        full_name,
        path,
        row_count,
        batch_id,
        status="SUCCESS",
        message=f"overwrite {row_count} rows",
    )
    return row_count


def ingest_customers(spark: SparkSession, batch_id: str) -> int:
    return _ingest(
        spark,
        filename=CUSTOMERS_FILE,
        required=CUSTOMER_REQUIRED,
        caster=cast_customers,
        bronze_table="bronze_customers",
        batch_id=batch_id,
    )


def ingest_orders(spark: SparkSession, batch_id: str) -> int:
    return _ingest(
        spark,
        filename=ORDERS_FILE,
        required=ORDER_REQUIRED,
        caster=cast_orders,
        bronze_table="bronze_orders",
        batch_id=batch_id,
    )


def ingest_products(spark: SparkSession, batch_id: str) -> int:
    return _ingest(
        spark,
        filename=PRODUCTS_FILE,
        required=PRODUCT_REQUIRED,
        caster=cast_products,
        bronze_table="bronze_products",
        batch_id=batch_id,
    )


def ingest_all(spark: SparkSession | None = None, batch_id: str | None = None) -> dict:
    spark = spark or get_spark("bronze-ingest")
    ensure_database(spark, DATABASE)
    batch_id = batch_id or os.environ.get("MEDALLION_BATCH_ID") or new_batch_id()
    counts = {
        "batch_id": batch_id,
        "customers": ingest_customers(spark, batch_id),
        "orders": ingest_orders(spark, batch_id),
        "products": ingest_products(spark, batch_id),
    }
    return counts
