"""Quality-check expectations derived from CSVs (Spark-free)."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"

VALID_SEGMENTS = {"Premium", "Standard", "Basic"}
VALID_STATUSES = {"Pending", "Completed", "Cancelled"}


def _rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _blank(value: str) -> bool:
    return value is None or value.strip() == ""


def test_customer_completeness_failures() -> None:
    failed = [r for r in _rows("customers.csv") if _blank(r["email"])]
    assert len(failed) == 50


def test_customer_uniqueness_failures() -> None:
    ids = [r["customer_id"] for r in _rows("customers.csv")]
    counts = Counter(ids)
    failed = [i for i in ids if counts[i] > 1]
    assert len(failed) == 20


def test_order_completeness_failures() -> None:
    failed = [
        r
        for r in _rows("orders.csv")
        if _blank(r["customer_id"]) or _blank(r["product_id"])
    ]
    assert len(failed) == 300


def test_order_uniqueness_failures() -> None:
    ids = [r["order_id"] for r in _rows("orders.csv")]
    counts = Counter(ids)
    failed = [i for i in ids if counts[i] > 1]
    assert len(failed) == 40


def test_order_ri_failures_skip_null_fks() -> None:
    customers = {r["customer_id"] for r in _rows("customers.csv") if not _blank(r["customer_id"])}
    products = {r["product_id"] for r in _rows("products.csv") if not _blank(r["product_id"])}
    failed = []
    for r in _rows("orders.csv"):
        orphan_c = (not _blank(r["customer_id"])) and r["customer_id"] not in customers
        orphan_p = (not _blank(r["product_id"])) and r["product_id"] not in products
        if orphan_c or orphan_p:
            failed.append(r)
    assert len(failed) == 80  # 50 + 30; null FKs excluded


def test_type_validation_all_generated_rows_pass() -> None:
    for r in _rows("customers.csv"):
        assert r["customer_segment"] in VALID_SEGMENTS
        assert r["signup_date"]
        float(r["lifetime_value"])
    for r in _rows("orders.csv"):
        assert r["order_status"] in VALID_STATUSES
        assert int(r["quantity"]) > 0
        assert float(r["unit_price"]) >= 0
        assert abs(float(r["total_amount"]) - int(r["quantity"]) * float(r["unit_price"])) <= 0.01
    for r in _rows("products.csv"):
        assert int(r["stock_quantity"]) >= 0
        assert float(r["cost"]) <= float(r["price"])


def test_gold_segmentation_case_order() -> None:
    def segment(orders: int, revenue: float) -> str:
        if orders == 0:
            return "Inactive"
        if revenue >= 5000 or orders >= 15:
            return "High-Value"
        if orders >= 2:
            return "Repeat"
        return "One-Time"

    assert segment(0, 99999) == "Inactive"
    assert segment(15, 10) == "High-Value"
    assert segment(2, 6000) == "High-Value"
    assert segment(3, 100) == "Repeat"
    assert segment(1, 100) == "One-Time"
