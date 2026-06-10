"""Run basic DuckDB data quality tests for the analytics pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"


@dataclass(frozen=True)
class QueryTest:
    name: str
    sql: str
    expected_value: int = 0


TESTS = [
    QueryTest(
        "raw_orders_pk_not_null",
        """
        SELECT COUNT(*)
        FROM raw.orders
        WHERE order_id IS NULL OR TRIM(CAST(order_id AS VARCHAR)) = ''
        """,
    ),
    QueryTest(
        "raw_customers_pk_not_null",
        """
        SELECT COUNT(*)
        FROM raw.customers
        WHERE customer_id IS NULL OR TRIM(CAST(customer_id AS VARCHAR)) = ''
        """,
    ),
    QueryTest(
        "raw_order_items_pk_not_null",
        """
        SELECT COUNT(*)
        FROM raw.order_items
        WHERE order_item_id IS NULL OR TRIM(CAST(order_item_id AS VARCHAR)) = ''
        """,
    ),
    QueryTest(
        "order_items_have_orders",
        """
        SELECT COUNT(*)
        FROM staging.stg_order_items AS oi
        LEFT JOIN staging.stg_orders AS o
            ON oi.order_id = o.order_id
        WHERE o.order_id IS NULL
        """,
    ),
    QueryTest(
        "orders_have_customers",
        """
        SELECT COUNT(*)
        FROM staging.stg_orders AS o
        LEFT JOIN staging.stg_customers AS c
            ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
        """,
    ),
    QueryTest(
        "order_items_have_products",
        """
        SELECT COUNT(*)
        FROM staging.stg_order_items AS oi
        LEFT JOIN staging.stg_products AS p
            ON oi.product_id = p.product_id
        WHERE p.product_id IS NULL
        """,
    ),
    QueryTest(
        "fact_orders_not_empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM marts.fact_orders",
    ),
    QueryTest(
        "fact_order_items_not_empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM marts.fact_order_items",
    ),
    QueryTest(
        "daily_revenue_not_empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM marts.fact_revenue_daily",
    ),
    QueryTest(
        "fact_payments_not_empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM marts.fact_payments",
    ),
    QueryTest(
        "fact_reviews_not_empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM marts.fact_reviews",
    ),
    QueryTest(
        "seller_performance_not_empty",
        "SELECT CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END FROM marts.fact_seller_performance",
    ),
    QueryTest(
        "no_negative_revenue_in_marts",
        """
        SELECT COUNT(*)
        FROM marts.fact_orders
        WHERE gross_revenue < 0 OR total_payment_value < 0 OR freight_value < 0
        """,
    ),
]


def run_tests() -> None:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to run data tests. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}. Run the pipeline first."
        )

    failed_tests: list[str] = []

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        for test in TESTS:
            observed_value = connection.execute(test.sql).fetchone()[0]
            status = "PASS" if observed_value == test.expected_value else "FAIL"
            print(f"{status}: {test.name} observed={observed_value} expected={test.expected_value}")

            if status == "FAIL":
                failed_tests.append(test.name)

    if failed_tests:
        failed = ", ".join(failed_tests)
        raise ValueError(f"Data quality tests failed: {failed}")


def main() -> None:
    try:
        run_tests()
    except (FileNotFoundError, ModuleNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print("All data quality tests passed.")


if __name__ == "__main__":
    main()
