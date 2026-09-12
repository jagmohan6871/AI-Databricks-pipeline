"""Bronze ingest: orders.csv → bronze_orders."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bronze.ingest_common import ingest_orders
from src.common.config import DATABASE, new_batch_id
from src.common.spark_utils import ensure_database, get_spark


def main() -> None:
    spark = get_spark("bronze-orders")
    ensure_database(spark, DATABASE)
    batch_id = new_batch_id()
    n = ingest_orders(spark, batch_id)
    print(f"bronze_orders rows={n} batch_id={batch_id}")


if __name__ == "__main__":
    main()
