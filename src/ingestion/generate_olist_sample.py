"""Generate a referentially consistent Olist sample from the full raw CSV files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FULL_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "Brazilian E-commerce"
SAMPLE_DATA_DIR = PROJECT_ROOT / "data" / "sample" / "olist"
DEFAULT_ORDER_LIMIT = 1_000

REQUIRED_FILES = [
    "olist_customers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "product_category_name_translation.csv",
]


def validate_full_dataset() -> None:
    missing_files = [
        FULL_DATA_DIR / filename
        for filename in REQUIRED_FILES
        if not (FULL_DATA_DIR / filename).exists()
    ]
    if missing_files:
        files = "\n".join(f"- {path}" for path in missing_files)
        raise FileNotFoundError(
            "The complete Olist dataset is required to generate the sample. "
            f"Missing files:\n{files}"
        )


def load_source_tables(connection: Any) -> None:
    source_tables = {
        "customers": "olist_customers_dataset.csv",
        "geolocation": "olist_geolocation_dataset.csv",
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "order_payments": "olist_order_payments_dataset.csv",
        "order_reviews": "olist_order_reviews_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "category_translation": "product_category_name_translation.csv",
    }

    for table_name, filename in source_tables.items():
        connection.execute(
            f"""
            CREATE TEMP TABLE source_{table_name} AS
            SELECT *
            FROM read_csv_auto(?, header = true)
            """,
            [str(FULL_DATA_DIR / filename)],
        )


def export_query(connection: Any, filename: str, query: str) -> int:
    output_path = SAMPLE_DATA_DIR / filename
    connection.execute(
        f"COPY ({query}) TO ? (FORMAT CSV, HEADER TRUE)",
        [str(output_path)],
    )
    return int(
        connection.execute(
            "SELECT COUNT(*) FROM read_csv_auto(?, header = true)",
            [str(output_path)],
        ).fetchone()[0]
    )


def generate_sample(order_limit: int = DEFAULT_ORDER_LIMIT) -> dict[str, int]:
    if order_limit <= 0:
        raise ValueError("order_limit must be greater than zero")

    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to generate the Olist sample. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    validate_full_dataset()
    SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    with duckdb.connect() as connection:
        load_source_tables(connection)
        connection.execute(
            """
            CREATE TEMP TABLE sample_orders AS
            SELECT order_id
            FROM source_orders
            ORDER BY order_purchase_timestamp, order_id
            LIMIT ?
            """,
            [order_limit],
        )

        exports = {
            "olist_orders_dataset.csv": """
                SELECT orders.*
                FROM source_orders AS orders
                INNER JOIN sample_orders USING (order_id)
                ORDER BY orders.order_purchase_timestamp, orders.order_id
            """,
            "olist_customers_dataset.csv": """
                SELECT DISTINCT customers.*
                FROM source_customers AS customers
                INNER JOIN source_orders AS orders USING (customer_id)
                INNER JOIN sample_orders USING (order_id)
                ORDER BY customers.customer_id
            """,
            "olist_order_items_dataset.csv": """
                SELECT items.*
                FROM source_order_items AS items
                INNER JOIN sample_orders USING (order_id)
                ORDER BY items.order_id, items.order_item_id
            """,
            "olist_order_payments_dataset.csv": """
                SELECT payments.*
                FROM source_order_payments AS payments
                INNER JOIN sample_orders USING (order_id)
                ORDER BY payments.order_id, payments.payment_sequential
            """,
            "olist_order_reviews_dataset.csv": """
                SELECT
                    reviews.review_id,
                    reviews.order_id,
                    reviews.review_score,
                    NULLIF(
                        REGEXP_REPLACE(
                            TRIM(reviews.review_comment_title),
                            '\\s+',
                            ' ',
                            'g'
                        ),
                        ''
                    ) AS review_comment_title,
                    NULLIF(
                        REGEXP_REPLACE(
                            TRIM(reviews.review_comment_message),
                            '\\s+',
                            ' ',
                            'g'
                        ),
                        ''
                    ) AS review_comment_message,
                    reviews.review_creation_date,
                    reviews.review_answer_timestamp
                FROM source_order_reviews AS reviews
                INNER JOIN sample_orders USING (order_id)
                ORDER BY reviews.order_id, reviews.review_id
            """,
            "olist_products_dataset.csv": """
                SELECT DISTINCT products.*
                FROM source_products AS products
                INNER JOIN source_order_items AS items USING (product_id)
                INNER JOIN sample_orders USING (order_id)
                ORDER BY products.product_id
            """,
            "olist_sellers_dataset.csv": """
                SELECT DISTINCT sellers.*
                FROM source_sellers AS sellers
                INNER JOIN source_order_items AS items USING (seller_id)
                INNER JOIN sample_orders USING (order_id)
                ORDER BY sellers.seller_id
            """,
            "product_category_name_translation.csv": """
                SELECT DISTINCT translations.*
                FROM source_category_translation AS translations
                INNER JOIN source_products AS products USING (product_category_name)
                INNER JOIN source_order_items AS items USING (product_id)
                INNER JOIN sample_orders USING (order_id)
                ORDER BY translations.product_category_name
            """,
            "olist_geolocation_dataset.csv": """
                WITH referenced_prefixes AS (
                    SELECT CAST(customers.customer_zip_code_prefix AS VARCHAR) AS zip_prefix
                    FROM source_customers AS customers
                    INNER JOIN source_orders AS orders USING (customer_id)
                    INNER JOIN sample_orders USING (order_id)

                    UNION

                    SELECT CAST(sellers.seller_zip_code_prefix AS VARCHAR)
                    FROM source_sellers AS sellers
                    INNER JOIN source_order_items AS items USING (seller_id)
                    INNER JOIN sample_orders USING (order_id)
                ),
                deduplicated_geolocation AS (
                    SELECT
                        geolocation.*,
                        ROW_NUMBER() OVER (
                            PARTITION BY
                                geolocation.geolocation_zip_code_prefix,
                                geolocation.geolocation_city,
                                geolocation.geolocation_state
                            ORDER BY
                                geolocation.geolocation_lat,
                                geolocation.geolocation_lng
                        ) AS row_number
                    FROM source_geolocation AS geolocation
                    INNER JOIN referenced_prefixes AS prefixes
                        ON CAST(geolocation.geolocation_zip_code_prefix AS VARCHAR)
                            = prefixes.zip_prefix
                )
                SELECT * EXCLUDE (row_number)
                FROM deduplicated_geolocation
                WHERE row_number = 1
                ORDER BY geolocation_zip_code_prefix, geolocation_city
            """,
        }

        return {
            filename: export_query(connection, filename, query)
            for filename, query in exports.items()
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--orders",
        type=int,
        default=DEFAULT_ORDER_LIMIT,
        help=f"Number of orders to include (default: {DEFAULT_ORDER_LIMIT}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        exported_rows = generate_sample(args.orders)
    except (FileNotFoundError, ModuleNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Olist sample created in {SAMPLE_DATA_DIR}")
    for filename, row_count in exported_rows.items():
        print(f"- {filename}: {row_count} rows")


if __name__ == "__main__":
    main()
