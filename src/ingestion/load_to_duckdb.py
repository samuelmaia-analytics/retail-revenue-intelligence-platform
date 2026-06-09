"""Load raw CSV files into a local DuckDB database."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
FULL_OLIST_DIR = RAW_DIR / "Brazilian E-commerce"
SAMPLE_OLIST_DIR = PROJECT_ROOT / "data" / "sample" / "olist"
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"
RAW_SCHEMA = "raw"
DataMode = Literal["auto", "full", "sample"]


@dataclass(frozen=True)
class RawTable:
    table_name: str
    csv_filename: str
    primary_key: str


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


def validate_required_files(source_dir: Path) -> None:
    missing_files = [
        source_dir / filename
        for filename in OLIST_REQUIRED_FILES
        if not (source_dir / filename).exists()
    ]

    if missing_files:
        files = "\n".join(f"- {path}" for path in missing_files)
        raise FileNotFoundError(f"Missing required Olist CSV files in {source_dir}:\n{files}")


def has_required_files(source_dir: Path) -> bool:
    return all((source_dir / filename).exists() for filename in OLIST_REQUIRED_FILES)


def resolve_source_dir(mode: DataMode) -> tuple[Path, str]:
    if mode == "full":
        validate_required_files(FULL_OLIST_DIR)
        return FULL_OLIST_DIR, "full"
    if mode == "sample":
        validate_required_files(SAMPLE_OLIST_DIR)
        return SAMPLE_OLIST_DIR, "sample"
    if has_required_files(FULL_OLIST_DIR):
        return FULL_OLIST_DIR, "full"
    if has_required_files(SAMPLE_OLIST_DIR):
        return SAMPLE_OLIST_DIR, "sample"

    raise FileNotFoundError(
        "No complete Olist input was found. Download the full dataset to "
        f"{FULL_OLIST_DIR} or restore the versioned sample in {SAMPLE_OLIST_DIR}."
    )


def load_olist_raw_tables(connection: Any, source_dir: Path) -> dict[str, int]:
    connection.execute(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}")

    for raw_table in OLIST_RAW_TABLES:
        csv_path = source_dir / raw_table.csv_filename
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE raw.{raw_table.table_name} AS
            SELECT *
            FROM read_csv_auto(?, header = true)
            """,
            [str(csv_path)],
        )

    connection.execute("""
        DROP TABLE IF EXISTS raw.category_translation;
        DROP TABLE IF EXISTS raw.marketing_campaigns;
        DROP TABLE IF EXISTS raw.order_campaigns;
        DROP TABLE IF EXISTS raw.shipments;
        """)

    for raw_table in OLIST_RAW_TABLES:
        missing_primary_keys = connection.execute(f"""
            SELECT COUNT(*)
            FROM raw.{raw_table.table_name}
            WHERE
                {raw_table.primary_key} IS NULL
                OR TRIM(CAST({raw_table.primary_key} AS VARCHAR)) = ''
            """).fetchone()[0]

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


def load_all_raw_tables(mode: DataMode = "auto") -> tuple[dict[str, int], str]:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to load raw CSV files. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    source_dir, selected_mode = resolve_source_dir(mode)

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        loaded_rows = load_olist_raw_tables(connection, source_dir)

    return loaded_rows, selected_mode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("auto", "full", "sample"),
        default="auto",
        help="Input mode: full raw data, versioned sample, or automatic fallback.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        loaded_rows, selected_mode = load_all_raw_tables(args.mode)
    except (FileNotFoundError, ModuleNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Using Olist data mode: {selected_mode}")
    print(f"Loaded raw CSV files into {DATABASE_PATH}")
    for table_name, row_count in loaded_rows.items():
        print(f"- {table_name}: {row_count} rows")


if __name__ == "__main__":
    main()
