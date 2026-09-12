"""CSV-level tests for the sample generator (no Spark required)."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

from src.data_generation.generate_sample_data import (
    DUP_CUSTOMERS,
    DUP_ORDERS,
    N_CUSTOMERS,
    N_ORDERS,
    N_PRODUCTS,
    NULL_EMAILS,
    NULL_ORDER_CUSTOMER,
    NULL_ORDER_PRODUCT,
    ORPHAN_CUSTOMER_ID_BASE,
    ORPHAN_CUSTOMERS,
    ORPHAN_PRODUCT_ID_BASE,
    ORPHAN_PRODUCTS,
    generate_all,
)

DATA = Path(__file__).resolve().parents[1] / "data"


def _rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_generate_is_deterministic(tmp_path: Path) -> None:
    a = generate_all(tmp_path / "a")
    b = generate_all(tmp_path / "b")
    assert a.customers.read_text() == b.customers.read_text()
    assert a.orders.read_text() == b.orders.read_text()
    assert a.products.read_text() == b.products.read_text()


def test_row_counts() -> None:
    customers = _rows("customers.csv")
    orders = _rows("orders.csv")
    products = _rows("products.csv")
    assert len(customers) == N_CUSTOMERS + DUP_CUSTOMERS
    assert len(orders) == N_ORDERS + DUP_ORDERS
    assert len(products) == N_PRODUCTS


def test_null_emails() -> None:
    customers = _rows("customers.csv")
    assert sum(1 for r in customers if not r["email"].strip()) == NULL_EMAILS


def test_duplicate_customer_ids() -> None:
    ids = [r["customer_id"] for r in _rows("customers.csv")]
    counts = Counter(ids)
    duplicated_keys = [k for k, n in counts.items() if n > 1]
    assert len(duplicated_keys) == DUP_CUSTOMERS
    assert sum(1 for i in ids if counts[i] > 1) == DUP_CUSTOMERS * 2


def test_order_completeness_issues() -> None:
    orders = _rows("orders.csv")[:N_ORDERS]
    null_c = sum(1 for r in orders if not r["customer_id"].strip())
    null_p = sum(1 for r in orders if not r["product_id"].strip())
    assert null_c == NULL_ORDER_CUSTOMER
    assert null_p == NULL_ORDER_PRODUCT


def test_order_orphans() -> None:
    customer_ids = {r["customer_id"] for r in _rows("customers.csv")}
    product_ids = {r["product_id"] for r in _rows("products.csv")}
    orders = _rows("orders.csv")[:N_ORDERS]
    orphan_c = [
        r
        for r in orders
        if r["customer_id"].strip() and r["customer_id"] not in customer_ids
    ]
    orphan_p = [
        r
        for r in orders
        if r["product_id"].strip() and r["product_id"] not in product_ids
    ]
    assert len(orphan_c) == ORPHAN_CUSTOMERS
    assert len(orphan_p) == ORPHAN_PRODUCTS
    assert all(r["customer_id"].startswith(str(ORPHAN_CUSTOMER_ID_BASE)[:3]) or int(r["customer_id"]) >= ORPHAN_CUSTOMER_ID_BASE for r in orphan_c)
    assert all(int(r["product_id"]) >= ORPHAN_PRODUCT_ID_BASE for r in orphan_p)


def test_order_defect_slices_are_disjoint() -> None:
    orders = _rows("orders.csv")[:N_ORDERS]
    tagged = []
    for r in orders:
        tags = []
        if not r["customer_id"].strip():
            tags.append("nc")
        if not r["product_id"].strip():
            tags.append("np")
        if r["customer_id"].strip() and int(r["customer_id"]) >= ORPHAN_CUSTOMER_ID_BASE:
            tags.append("oc")
        if r["product_id"].strip() and int(r["product_id"]) >= ORPHAN_PRODUCT_ID_BASE:
            tags.append("op")
        if tags:
            tagged.append(tags)
    assert all(len(t) == 1 for t in tagged)
    assert len(tagged) == (
        NULL_ORDER_CUSTOMER + NULL_ORDER_PRODUCT + ORPHAN_CUSTOMERS + ORPHAN_PRODUCTS
    )


def test_duplicate_order_ids() -> None:
    ids = [r["order_id"] for r in _rows("orders.csv")]
    counts = Counter(ids)
    duplicated_keys = [k for k, n in counts.items() if n > 1]
    assert len(duplicated_keys) == DUP_ORDERS
    assert sum(1 for i in ids if counts[i] > 1) == DUP_ORDERS * 2
