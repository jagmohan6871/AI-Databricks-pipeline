"""Run all Bronze ingest jobs with a shared batch id."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.bronze.ingest_common import ingest_all


def main() -> None:
    counts = ingest_all()
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
