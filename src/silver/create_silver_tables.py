"""Build Silver tables, quarantine views, and quality metrics."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from src.common.config import AS_OF_DATE, DATABASE, new_batch_id, table_name
from src.common.spark_utils import ensure_database, get_spark, write_delta_overwrite
from src.silver.q01_quality_completeness import (
    customers_completeness,
    orders_completeness,
    products_completeness,
)
from src.silver.q02_quality_uniqueness import (
    customers_uniqueness,
    orders_uniqueness,
    products_uniqueness,
)
from src.silver.q03_quality_type_validation import (
    customers_types,
    orders_types,
    products_types,
)
from src.silver.q04_quality_referential_integrity import (
    customers_referential_integrity,
    orders_referential_integrity,
    products_referential_integrity,
)
from src.silver.q05_quality_business_logic import (
    customers_business_logic,
    orders_business_logic,
    products_business_logic,
)

CHECKS = [
    "completeness",
    "uniqueness",
    "type_validation",
    "referential_integrity",
    "business_logic",
]


def _combine_reasons(*cols):
    return F.concat_ws(";", *[c for c in cols])


def _finalize(df: DataFrame) -> DataFrame:
    passed = (
        F.col("completeness_pass")
        & F.col("uniqueness_pass")
        & F.col("type_validation_pass")
        & F.col("referential_integrity_pass")
        & F.col("business_logic_pass")
    )
    reasons = _combine_reasons(
        F.col("completeness_reasons"),
        F.col("uniqueness_reasons"),
        F.col("type_reasons"),
        F.col("ri_reasons"),
        F.col("business_reasons"),
    )
    return (
        df.withColumn("quality_failure_reasons", F.when(F.length(reasons) > 0, reasons))
        .withColumn("quality_check_result", F.when(passed, F.lit("PASS")).otherwise(F.lit("FAIL")))
        .drop(
            "completeness_reasons",
            "uniqueness_reasons",
            "type_reasons",
            "ri_reasons",
            "business_reasons",
        )
    )


def build_silver_customers(bronze: DataFrame) -> DataFrame:
    df = customers_completeness(bronze)
    df = customers_uniqueness(df)
    df = customers_types(df)
    df = customers_referential_integrity(df)
    df = customers_business_logic(df, AS_OF_DATE)
    return _finalize(df)


def build_silver_products(bronze: DataFrame) -> DataFrame:
    df = products_completeness(bronze)
    df = products_uniqueness(df)
    df = products_types(df)
    df = products_referential_integrity(df)
    df = products_business_logic(df)
    return _finalize(df)


def build_silver_orders(
    bronze_orders: DataFrame, bronze_customers: DataFrame, bronze_products: DataFrame
) -> DataFrame:
    df = orders_completeness(bronze_orders)
    df = orders_uniqueness(df)
    df = orders_types(df)
    df = orders_referential_integrity(df, bronze_customers, bronze_products)
    df = orders_business_logic(df)
    return _finalize(df)


def metrics_for(df: DataFrame, table_name_value: str, batch_id: str) -> DataFrame:
    mapping = {
        "completeness": "completeness_pass",
        "uniqueness": "uniqueness_pass",
        "type_validation": "type_validation_pass",
        "referential_integrity": "referential_integrity_pass",
        "business_logic": "business_logic_pass",
    }
    total = df.count()
    rows = []
    for check_name, col_name in mapping.items():
        passed = df.where(F.col(col_name)).count()
        failed = total - passed
        pct = 0.0 if total == 0 else round(100.0 * passed / total, 4)
        rows.append(
            (
                table_name_value,
                check_name,
                int(total),
                int(passed),
                int(failed),
                float(pct),
                batch_id,
            )
        )
    spark = df.sparkSession
    return spark.createDataFrame(
        rows,
        schema="table_name string, check_name string, rows_checked long, rows_passed long, rows_failed long, pass_percentage double, batch_id string",
    ).withColumn("computed_at", F.current_timestamp())


def _create_views(spark: SparkSession) -> None:
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {table_name("silver_orders_valid")} AS
        SELECT * FROM {table_name("silver_orders")}
        WHERE quality_check_result = 'PASS'
        """
    )
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {table_name("silver_orders_quarantine")} AS
        SELECT * FROM {table_name("silver_orders")}
        WHERE quality_check_result = 'FAIL'
        """
    )
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {table_name("silver_customers_valid")} AS
        SELECT * FROM {table_name("silver_customers")}
        WHERE quality_check_result = 'PASS'
        """
    )
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {table_name("silver_customers_quarantine")} AS
        SELECT * FROM {table_name("silver_customers")}
        WHERE quality_check_result = 'FAIL'
        """
    )


def create_silver_tables(
    spark: SparkSession | None = None, batch_id: str | None = None
) -> str:
    spark = spark or get_spark("silver-quality")
    ensure_database(spark, DATABASE)
    batch_id = batch_id or new_batch_id()

    customers = spark.table(table_name("bronze_customers"))
    orders = spark.table(table_name("bronze_orders"))
    products = spark.table(table_name("bronze_products"))

    silver_c = build_silver_customers(customers)
    silver_p = build_silver_products(products)
    silver_o = build_silver_orders(orders, customers, products)

    write_delta_overwrite(silver_c, table_name("silver_customers"))
    write_delta_overwrite(silver_p, table_name("silver_products"))
    write_delta_overwrite(silver_o, table_name("silver_orders"))

    metrics = (
        metrics_for(silver_c, "silver_customers", batch_id)
        .unionByName(metrics_for(silver_p, "silver_products", batch_id))
        .unionByName(metrics_for(silver_o, "silver_orders", batch_id))
    )
    write_delta_overwrite(metrics, table_name("silver_quality_metrics"))
    _create_views(spark)
    print(f"Silver tables written batch_id={batch_id}")
    metrics.show(50, truncate=False)
    return batch_id


def main() -> None:
    create_silver_tables()


if __name__ == "__main__":
    main()
