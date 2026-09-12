"""Spark session and Delta helpers that run on Databricks or locally."""

from __future__ import annotations

from datetime import datetime, timezone

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


def get_spark(app_name: str = "medallion-pipeline") -> SparkSession:
    existing = SparkSession.getActiveSession()
    if existing is not None:
        return existing
    return (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def ensure_database(spark: SparkSession, database: str) -> None:
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {database}")
    spark.sql(f"USE {database}")


def utc_now_col():
    return F.lit(datetime.now(timezone.utc).isoformat())


def write_delta_overwrite(df: DataFrame, full_table_name: str) -> None:
    (
        df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(full_table_name)
    )


def require_columns(df: DataFrame, required: list[str], source: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")


def log_ingest(
    spark: SparkSession,
    database: str,
    table: str,
    source_path: str,
    row_count: int,
    batch_id: str,
    status: str,
    message: str = "",
) -> None:
    log_table = f"{database}.bronze_ingestion_log"
    spark.sql(
        f"""
        CREATE TABLE IF NOT EXISTS {log_table} (
            table_name STRING,
            source_path STRING,
            row_count LONG,
            batch_id STRING,
            status STRING,
            message STRING,
            ingested_at STRING
        ) USING DELTA
        """
    )
    spark.createDataFrame(
        [
            {
                "table_name": table,
                "source_path": source_path,
                "row_count": int(row_count),
                "batch_id": batch_id,
                "status": status,
                "message": message,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    ).write.format("delta").mode("append").saveAsTable(log_table)
