"""Load raw CSV files into a local DuckDB database."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OLIST_DIR = RAW_DIR / "Brazilian E-commerce"
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"
RAW_SCHEMA = "raw"


@dataclass(frozen=True)
class RawTable:
    table_name: str
    csv_filename: str
    primary_key: str


RAW_TABLES = [
    RawTable("customers", "customers.csv", "customer_id"),
    RawTable("products", "products.csv", "product_id"),
    RawTable("orders", "orders.csv", "order_id"),
    RawTable("order_items", "order_items.csv", "order_item_id"),
]

OLIST_RAW_TABLES = [
    RawTable("customers", "olist_customers_dataset.csv", "customer_id"),
    RawTable("geolocation", "olist_geolocation_dataset.csv", "geolocation_zip_code_prefix"),
    RawTable("orders", "olist_orders_dataset.csv", "order_id"),
    RawTable("order_items", "olist_order_items_dataset.csv", "order_id"),
    RawTable("order_payments", "olist_order_payments_dataset.csv", "order_id"),
    RawTable("order_reviews", "olist_order_reviews_dataset.csv", "review_id"),
    RawTable("products", "olist_products_dataset.csv", "product_id"),
    RawTable("sellers", "olist_sellers_dataset.csv", "seller_id"),
    RawTable(
        "product_category_translation",
        "product_category_name_translation.csv",
        "product_category_name",
    ),
]

OLIST_REQUIRED_FILES = [
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


def validate_required_files(raw_tables: list[RawTable]) -> None:
    missing_files = [
        str(RAW_DIR / raw_table.csv_filename)
        for raw_table in raw_tables
        if not (RAW_DIR / raw_table.csv_filename).exists()
    ]

    if missing_files:
        files = "\n".join(f"- {path}" for path in missing_files)
        raise FileNotFoundError(
            "Missing required raw CSV files. Expected files in data/raw/:\n" f"{files}"
        )


def has_canonical_raw_files() -> bool:
    return all((RAW_DIR / raw_table.csv_filename).exists() for raw_table in RAW_TABLES)


def has_olist_raw_files() -> bool:
    return all((OLIST_DIR / filename).exists() for filename in OLIST_REQUIRED_FILES)


def load_raw_table(connection: Any, raw_table: RawTable) -> int:
    csv_path = RAW_DIR / raw_table.csv_filename
    qualified_table = f"{RAW_SCHEMA}.{raw_table.table_name}"

    connection.execute(
        f"""
        CREATE OR REPLACE TABLE {qualified_table} AS
        SELECT *
        FROM read_csv_auto(?, header = true)
        """,
        [str(csv_path)],
    )

    missing_primary_keys = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM {qualified_table}
        WHERE
            {raw_table.primary_key} IS NULL
            OR TRIM(CAST({raw_table.primary_key} AS VARCHAR)) = ''
        """,
    ).fetchone()[0]

    if missing_primary_keys > 0:
        raise ValueError(
            f"{qualified_table} has {missing_primary_keys} null values "
            f"in primary key column {raw_table.primary_key}."
        )

    row_count = connection.execute(f"SELECT COUNT(*) FROM {qualified_table}").fetchone()[0]
    return int(row_count)


def load_olist_raw_tables(connection: Any) -> dict[str, int]:
    connection.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

    for raw_table in OLIST_RAW_TABLES:
        csv_path = OLIST_DIR / raw_table.csv_filename
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE raw.{raw_table.table_name} AS
            SELECT *
            FROM read_csv_auto(?, header = true)
            """,
            [str(csv_path)],
        )

    connection.execute(
        """
        DROP TABLE IF EXISTS raw.category_translation;
        DROP TABLE IF EXISTS raw.marketing_campaigns;
        DROP TABLE IF EXISTS raw.order_campaigns;
        DROP TABLE IF EXISTS raw.shipments;
        """
    )

    for raw_table in OLIST_RAW_TABLES:
        missing_primary_keys = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM raw.{raw_table.table_name}
            WHERE
                {raw_table.primary_key} IS NULL
                OR TRIM(CAST({raw_table.primary_key} AS VARCHAR)) = ''
            """
        ).fetchone()[0]

        if missing_primary_keys > 0:
            raise ValueError(
                f"raw.{raw_table.table_name} has {missing_primary_keys} null values "
                f"in primary key column {raw_table.primary_key}."
            )

    return {
        f"raw.{raw_table.table_name}": int(
            connection.execute(f"SELECT COUNT(*) FROM raw.{raw_table.table_name}").fetchone()[0]
        )
        for raw_table in OLIST_RAW_TABLES
    }


def load_all_raw_tables() -> dict[str, int]:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to load raw CSV files. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    loaded_rows: dict[str, int] = {}

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        if has_canonical_raw_files():
            connection.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

            for raw_table in RAW_TABLES:
                row_count = load_raw_table(connection, raw_table)
                loaded_rows[f"{RAW_SCHEMA}.{raw_table.table_name}"] = row_count
        elif has_olist_raw_files():
            loaded_rows = load_olist_raw_tables(connection)
        else:
            validate_required_files(RAW_TABLES)

    return loaded_rows


def main() -> None:
    try:
        loaded_rows = load_all_raw_tables()
    except (FileNotFoundError, ModuleNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Loaded raw CSV files into {DATABASE_PATH}")
    for table_name, row_count in loaded_rows.items():
        print(f"- {table_name}: {row_count} rows")


if __name__ == "__main__":
    main()
