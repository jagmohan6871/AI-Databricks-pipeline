"""Pipeline configuration shared by Bronze, Silver, and Gold scripts.

Override any value with environment variables when running on Databricks:

    spark.conf.set is not required; use os.environ in a notebook:
    %env MEDALLION_DATABASE=medallion_ecommerce
    %env MEDALLION_RAW_PATH=/FileStore/medallion/raw
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

DATABASE = os.environ.get("MEDALLION_DATABASE", "medallion_ecommerce")
RAW_DATA_PATH = os.environ.get("MEDALLION_RAW_PATH", "/FileStore/medallion/raw")
CHECKPOINT_PATH = os.environ.get(
    "MEDALLION_CHECKPOINT_PATH", "/FileStore/medallion/checkpoints"
)

# Generation "today" — matches the evaluation workspace date and the CSV generator.
AS_OF_DATE = os.environ.get("MEDALLION_AS_OF_DATE", "2026-09-12")

CUSTOMERS_FILE = "customers.csv"
ORDERS_FILE = "orders.csv"
PRODUCTS_FILE = "products.csv"


def new_batch_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}_{uuid.uuid4().hex[:8]}"


def table_name(layer_table: str) -> str:
    return f"{DATABASE}.{layer_table}"


def raw_file(filename: str) -> str:
    return f"{RAW_DATA_PATH.rstrip('/')}/{filename}"
