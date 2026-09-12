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


def test_gold_ctas_parser_extracts_select() -> None:
    from src.gold.sql_loader import (
        parse_ctas_statement,
        parse_gold_statements,
        qualify_table_ref,
    )

    text = (GOLD / "01_sales_by_product.sql").read_text(encoding="utf-8")
    stmt = parse_gold_statements(text, "medallion_ecommerce")[0]
    table_ref, select_sql = parse_ctas_statement(stmt)
    assert table_ref == "medallion_ecommerce.gold_sales_by_product"
    assert "FROM medallion_ecommerce.silver_orders o" in select_sql
    assert qualify_table_ref(table_ref, "workspace", "medallion_ecommerce") == (
        "workspace.medallion_ecommerce.gold_sales_by_product"
    )
