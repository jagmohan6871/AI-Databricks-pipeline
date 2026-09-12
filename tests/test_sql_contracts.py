"""Static contracts so Gold SQL cannot silently drop quality filters."""

from pathlib import Path

GOLD = Path(__file__).resolve().parents[1] / "src" / "gold"


def test_gold_sql_filters_pass_and_completed() -> None:
    for name in [
        "01_sales_by_product.sql",
        "02_revenue_by_customer.sql",
        "03_daily_weekly_trends.sql",
    ]:
        text = (GOLD / name).read_text(encoding="utf-8")
        assert "quality_check_result = 'PASS'" in text
        assert "order_status = 'Completed'" in text


def test_segmentation_case_order() -> None:
    text = (GOLD / "04_customer_segmentation.sql").read_text(encoding="utf-8")
    inactive = text.index("Inactive")
    high = text.index("High-Value")
    repeat = text.index("Repeat")
    one = text.index("One-Time")
    assert inactive < high < repeat < one


def test_gold_sql_parser_keeps_comment_prefixed_statements() -> None:
    from src.gold.sql_loader import parse_gold_statements

    counts = {
        "01_sales_by_product.sql": 1,
        "02_revenue_by_customer.sql": 1,
        "03_daily_weekly_trends.sql": 2,
        "04_customer_segmentation.sql": 1,
    }
    for name, expected in counts.items():
        text = (GOLD / name).read_text(encoding="utf-8")
        stmts = parse_gold_statements(text, "medallion_ecommerce")
        assert len(stmts) == expected, f"{name}: expected {expected}, got {len(stmts)}"
        assert all(stmt.upper().startswith("CREATE OR REPLACE TABLE") for stmt in stmts)
