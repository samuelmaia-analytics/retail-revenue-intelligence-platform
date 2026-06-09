"""Data quality tests for the Olist DuckDB analytics pipeline."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import duckdb
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"

OLIST_ORDER_STATUSES = {
    "approved",
    "canceled",
    "created",
    "delivered",
    "invoiced",
    "processing",
    "shipped",
    "unavailable",
}

EXPECTED_MART_TABLES = [
    "dim_customers",
    "dim_products",
    "dim_sellers",
    "dim_dates",
    "fact_orders",
    "fact_order_items",
    "fact_payments",
    "fact_reviews",
    "fact_revenue_daily",
    "fact_customer_retention",
    "fact_seller_performance",
]


@pytest.fixture(scope="session")
def connection() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    assert (
        DATABASE_PATH.exists()
    ), f"DuckDB database not found at {DATABASE_PATH}. Run the pipeline before pytest."

    database = duckdb.connect(str(DATABASE_PATH), read_only=True)
    try:
        yield database
    finally:
        database.close()


def violation_count(connection: duckdb.DuckDBPyConnection, query: str) -> int:
    return int(connection.execute(query).fetchone()[0])


def assert_no_violations(
    connection: duckdb.DuckDBPyConnection,
    query: str,
    rule: str,
) -> None:
    violations = violation_count(connection, query)
    assert violations == 0, f"{rule}: found {violations} violating rows"


# Raw layer


def test_raw_orders_order_id_not_null(connection: duckdb.DuckDBPyConnection) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM raw.orders WHERE order_id IS NULL",
        "raw.orders.order_id must not be null",
    )


def test_raw_orders_order_id_unique(connection: duckdb.DuckDBPyConnection) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM raw.orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        )
        """,
        "raw.orders.order_id must be unique",
    )


def test_raw_customers_customer_id_not_null(connection: duckdb.DuckDBPyConnection) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM raw.customers WHERE customer_id IS NULL",
        "raw.customers.customer_id must not be null",
    )


def test_raw_products_product_id_not_null(connection: duckdb.DuckDBPyConnection) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM raw.products WHERE product_id IS NULL",
        "raw.products.product_id must not be null",
    )


def test_raw_order_items_order_id_not_null(connection: duckdb.DuckDBPyConnection) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM raw.order_items WHERE order_id IS NULL",
        "raw.order_items.order_id must not be null",
    )


def test_raw_order_items_product_id_not_null(connection: duckdb.DuckDBPyConnection) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM raw.order_items WHERE product_id IS NULL",
        "raw.order_items.product_id must not be null",
    )


def test_raw_order_payments_order_id_not_null(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM raw.order_payments WHERE order_id IS NULL",
        "raw.order_payments.order_id must not be null",
    )


# Relationships


def test_raw_order_items_orders_relationship(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM raw.order_items AS items
        LEFT JOIN raw.orders AS orders
            ON items.order_id = orders.order_id
        WHERE orders.order_id IS NULL
        """,
        "every raw.order_items.order_id must exist in raw.orders",
    )


def test_raw_orders_customers_relationship(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM raw.orders AS orders
        LEFT JOIN raw.customers AS customers
            ON orders.customer_id = customers.customer_id
        WHERE customers.customer_id IS NULL
        """,
        "every raw.orders.customer_id must exist in raw.customers",
    )


def test_raw_order_items_products_relationship(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM raw.order_items AS items
        LEFT JOIN raw.products AS products
            ON items.product_id = products.product_id
        WHERE products.product_id IS NULL
        """,
        "every raw.order_items.product_id must exist in raw.products",
    )


def test_raw_order_items_sellers_relationship(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM raw.order_items AS items
        LEFT JOIN raw.sellers AS sellers
            ON items.seller_id = sellers.seller_id
        WHERE sellers.seller_id IS NULL
        """,
        "every raw.order_items.seller_id must exist in raw.sellers",
    )


def test_raw_order_payments_orders_relationship(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM raw.order_payments AS payments
        LEFT JOIN raw.orders AS orders
            ON payments.order_id = orders.order_id
        WHERE orders.order_id IS NULL
        """,
        "every raw.order_payments.order_id must exist in raw.orders",
    )


# Staging layer


def test_staging_orders_order_date_not_null(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM staging.stg_orders WHERE order_date IS NULL",
        "staging.stg_orders.order_date must not be null",
    )


def test_staging_orders_status_is_valid(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    observed_statuses = {
        row[0]
        for row in connection.execute(
            "SELECT DISTINCT order_status FROM staging.stg_orders"
        ).fetchall()
    }
    invalid_statuses = observed_statuses - OLIST_ORDER_STATUSES

    assert None not in observed_statuses, "staging.stg_orders.order_status must not be null"
    assert not invalid_statuses, f"unexpected Olist order statuses: {sorted(invalid_statuses)}"


def test_staging_orders_is_late_delivery_is_boolean(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    data_type = connection.execute("""
        SELECT data_type
        FROM information_schema.columns
        WHERE
            table_schema = 'staging'
            AND table_name = 'stg_orders'
            AND column_name = 'is_late_delivery'
        """).fetchone()

    assert data_type is not None, "staging.stg_orders.is_late_delivery does not exist"
    assert data_type[0] == "BOOLEAN"


def test_staging_order_items_item_price_not_negative(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM staging.stg_order_items WHERE item_price < 0",
        "staging.stg_order_items.item_price must not be negative",
    )


def test_staging_order_items_freight_value_not_negative(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM staging.stg_order_items WHERE freight_value < 0",
        "staging.stg_order_items.freight_value must not be negative",
    )


def test_staging_order_reviews_score_in_range(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM staging.stg_order_reviews
        WHERE review_score IS NOT NULL AND review_score NOT BETWEEN 1 AND 5
        """,
        "staging.stg_order_reviews.review_score must be between 1 and 5",
    )


# Marts layer


@pytest.mark.parametrize("table_name", EXPECTED_MART_TABLES)
def test_expected_mart_table_exists(
    connection: duckdb.DuckDBPyConnection,
    table_name: str,
) -> None:
    table_count = violation_count(
        connection,
        f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = 'marts' AND table_name = '{table_name}'
        """,
    )
    assert table_count == 1, f"expected table marts.{table_name} was not found"


def test_marts_fact_orders_order_id_unique(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM marts.fact_orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        )
        """,
        "marts.fact_orders.order_id must be unique",
    )


def test_marts_fact_orders_gross_revenue_not_negative(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        "SELECT COUNT(*) FROM marts.fact_orders WHERE gross_revenue < 0",
        "marts.fact_orders.gross_revenue must not be negative",
    )


def test_marts_fact_orders_total_payment_value_not_negative(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM marts.fact_orders
        WHERE total_payment_value IS NOT NULL AND total_payment_value < 0
        """,
        "marts.fact_orders.total_payment_value must not be negative",
    )


def test_marts_customer_retention_customer_unique_id_unique(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM (
            SELECT customer_unique_id
            FROM marts.fact_customer_retention
            GROUP BY customer_unique_id
            HAVING COUNT(*) > 1
        )
        """,
        "marts.fact_customer_retention.customer_unique_id must be unique",
    )


def test_marts_seller_late_delivery_rate_in_range(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM marts.fact_seller_performance
        WHERE late_delivery_rate IS NULL OR late_delivery_rate NOT BETWEEN 0 AND 1
        """,
        "marts.fact_seller_performance.late_delivery_rate must be between 0 and 1",
    )


def test_marts_fact_reviews_score_in_range(
    connection: duckdb.DuckDBPyConnection,
) -> None:
    assert_no_violations(
        connection,
        """
        SELECT COUNT(*)
        FROM marts.fact_reviews
        WHERE review_score IS NOT NULL AND review_score NOT BETWEEN 1 AND 5
        """,
        "marts.fact_reviews.review_score must be between 1 and 5",
    )
