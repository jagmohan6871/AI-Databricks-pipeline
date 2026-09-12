"""End-to-end orchestrator for Databricks or local Spark."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bronze.ingest_common import ingest_all
from src.gold.create_gold_tables import create_gold_tables
from src.silver.create_silver_tables import create_silver_tables


def main() -> None:
    bronze = ingest_all()
    print("Bronze:", json.dumps(bronze, indent=2))
    silver_batch = create_silver_tables(batch_id=bronze["batch_id"])
    print("Silver batch:", silver_batch)
    create_gold_tables()
    print("Pipeline complete.")


if __name__ == "__main__":
    main()
