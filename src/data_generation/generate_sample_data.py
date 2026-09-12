"""Deterministic e-commerce CSV generator with intentional quality issues.

Run from the repository root:

    python src/data_generation/generate_sample_data.py

Outputs data/customers.csv, data/orders.csv, data/products.csv.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

SEED = 42
AS_OF = date(2026, 9, 12)

N_CUSTOMERS = 10_000
N_PRODUCTS = 500
N_ORDERS = 100_000

NULL_EMAILS = 50
DUP_CUSTOMERS = 10
NULL_ORDER_CUSTOMER = 100
NULL_ORDER_PRODUCT = 200
ORPHAN_CUSTOMERS = 50
ORPHAN_PRODUCTS = 30
DUP_ORDERS = 20

# Disjoint slices of the 100,000 base orders (end-exclusive).
SLICE_NULL_CUSTOMER = (0, 100)  # 100 rows
SLICE_NULL_PRODUCT = (100, 300)  # 200 rows
SLICE_ORPHAN_CUSTOMER = (300, 350)  # 50 rows
SLICE_ORPHAN_PRODUCT = (350, 380)  # 30 rows
# Remaining 99,620 base orders are clean on those four checks.

ORPHAN_CUSTOMER_ID_BASE = 9_000_000
ORPHAN_PRODUCT_ID_BASE = 8_000_000

FIRST_NAMES = [
    "Aarav", "Aisha", "Amelia", "Anika", "Arjun", "Chen", "Diego", "Elena",
    "Fatima", "Grace", "Hassan", "Hiro", "Imani", "James", "Jia", "Keiko",
    "Liam", "Lucia", "Maya", "Noah", "Omar", "Priya", "Quinn", "Rosa",
    "Sofia", "Tara", "Uma", "Viktor", "Wei", "Yara", "Zane",
]
LAST_NAMES = [
    "Anderson", "Patel", "Garcia", "Kim", "Silva", "Nguyen", "Khan", "Muller",
    "Sato", "Costa", "Brown", "Singh", "Lopez", "Ivanov", "Mensah", "Okafor",
    "Williams", "Chen", "Ali", "Novak",
]
COUNTRIES = [
    "United States", "United Kingdom", "India", "Germany", "Canada",
    "Australia", "France", "Brazil", "Japan", "Singapore",
]
SEGMENTS = ["Premium", "Standard", "Basic"]
CATEGORIES = [
    "Electronics", "Home", "Apparel", "Beauty", "Sports",
    "Grocery", "Toys", "Books", "Automotive", "Office",
]
STATUSES = ["Completed", "Pending", "Cancelled"]


@dataclass(frozen=True)
class Paths:
    customers: Path
    orders: Path
    products: Path


def repo_data_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data"


def _name(rng: random.Random) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def _email(rng: random.Random, customer_id: int, name: str) -> str:
    slug = name.lower().replace(" ", ".")
    domain = rng.choice(["example.com", "shopmail.test", "retail.dev"])
    return f"{slug}.{customer_id}@{domain}"


def _date_between(rng: random.Random, start: date, end: date) -> date:
    span = (end - start).days
    return start + timedelta(days=rng.randint(0, max(span, 0)))


def generate_products(rng: random.Random) -> list[dict]:
    rows = []
    for product_id in range(1, N_PRODUCTS + 1):
        category = CATEGORIES[(product_id - 1) % len(CATEGORIES)]
        cost = round(rng.uniform(3.0, 180.0), 2)
        markup = rng.uniform(1.15, 2.4)
        price = round(cost * markup, 2)
        rows.append(
            {
                "product_id": product_id,
                "product_name": f"{category} Item {product_id:03d}",
                "category": category,
                "price": f"{price:.2f}",
                "cost": f"{cost:.2f}",
                "stock_quantity": rng.randint(0, 5000),
                "reorder_level": rng.randint(10, 250),
            }
        )
    return rows


def generate_customers(rng: random.Random) -> list[dict]:
    rows = []
    for customer_id in range(1, N_CUSTOMERS + 1):
        name = _name(rng)
        signup = _date_between(rng, date(2020, 1, 1), AS_OF)
        segment = rng.choices(SEGMENTS, weights=[0.15, 0.55, 0.30], k=1)[0]
        ltv = round(rng.uniform(25.0, 12000.0), 2)
        rows.append(
            {
                "customer_id": customer_id,
                "customer_name": name,
                "email": _email(rng, customer_id, name),
                "country": rng.choice(COUNTRIES),
                "signup_date": signup.isoformat(),
                "customer_segment": segment,
                "lifetime_value": f"{ltv:.2f}",
            }
        )

    # Completeness: 50 NULL emails on otherwise unique customers (ids 1-50).
    for i in range(NULL_EMAILS):
        rows[i]["email"] = ""

    # Uniqueness: 10 extra rows copying customer_id 1001-1010.
    for i in range(DUP_CUSTOMERS):
        source = rows[1000 + i].copy()
        source["customer_name"] = source["customer_name"] + " (dup)"
        rows.append(source)

    return rows


def generate_orders(
    rng: random.Random, customers: list[dict], products: list[dict]
) -> list[dict]:
    valid_customer_ids = [c["customer_id"] for c in customers[:N_CUSTOMERS]]
    valid_product_ids = [p["product_id"] for p in products]
    price_by_product = {int(p["product_id"]): float(p["price"]) for p in products}

    rows: list[dict] = []
    for i in range(N_ORDERS):
        order_id = i + 1
        customer_id: int | None = rng.choice(valid_customer_ids)
        product_id: int | None = rng.choice(valid_product_ids)

        if SLICE_NULL_CUSTOMER[0] <= i < SLICE_NULL_CUSTOMER[1]:
            customer_id = None
        elif SLICE_ORPHAN_CUSTOMER[0] <= i < SLICE_ORPHAN_CUSTOMER[1]:
            customer_id = ORPHAN_CUSTOMER_ID_BASE + (i - SLICE_ORPHAN_CUSTOMER[0])

        if SLICE_NULL_PRODUCT[0] <= i < SLICE_NULL_PRODUCT[1]:
            product_id = None
        elif SLICE_ORPHAN_PRODUCT[0] <= i < SLICE_ORPHAN_PRODUCT[1]:
            product_id = ORPHAN_PRODUCT_ID_BASE + (i - SLICE_ORPHAN_PRODUCT[0])

        order_date = _date_between(rng, date(2023, 1, 1), AS_OF)
        status = rng.choices(STATUSES, weights=[0.82, 0.12, 0.06], k=1)[0]
        quantity = rng.randint(1, 6)
        if product_id is not None and product_id in price_by_product:
            unit_price = price_by_product[product_id]
        else:
            unit_price = round(rng.uniform(5.0, 250.0), 2)
        total = round(quantity * unit_price, 2)
        payment_date = ""
        if status == "Completed":
            payment_date = (
                order_date + timedelta(days=rng.randint(0, 5))
            ).isoformat()

        rows.append(
            {
                "order_id": order_id,
                "customer_id": "" if customer_id is None else customer_id,
                "order_date": order_date.isoformat(),
                "product_id": "" if product_id is None else product_id,
                "quantity": quantity,
                "unit_price": f"{unit_price:.2f}",
                "total_amount": f"{total:.2f}",
                "order_status": status,
                "payment_date": payment_date,
            }
        )

    # Uniqueness: 20 extra rows copying order_id 5001-5020 (clean region).
    for i in range(DUP_ORDERS):
        source = rows[5000 + i].copy()
        rows.append(source)

    return rows


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_all(data_dir: Path | None = None) -> Paths:
    rng = random.Random(SEED)
    data_dir = data_dir or repo_data_dir()
    products = generate_products(rng)
    customers = generate_customers(rng)
    orders = generate_orders(rng, customers, products)

    paths = Paths(
        customers=data_dir / "customers.csv",
        orders=data_dir / "orders.csv",
        products=data_dir / "products.csv",
    )
    _write_csv(
        paths.customers,
        [
            "customer_id",
            "customer_name",
            "email",
            "country",
            "signup_date",
            "customer_segment",
            "lifetime_value",
        ],
        customers,
    )
    _write_csv(
        paths.orders,
        [
            "order_id",
            "customer_id",
            "order_date",
            "product_id",
            "quantity",
            "unit_price",
            "total_amount",
            "order_status",
            "payment_date",
        ],
        orders,
    )
    _write_csv(
        paths.products,
        [
            "product_id",
            "product_name",
            "category",
            "price",
            "cost",
            "stock_quantity",
            "reorder_level",
        ],
        products,
    )
    return paths


if __name__ == "__main__":
    written = generate_all()
    print(f"Wrote {written.customers}")
    print(f"Wrote {written.orders}")
    print(f"Wrote {written.products}")
