"""Run DuckDB staging SQL scripts in dependency order."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"
STAGING_SQL_DIR = PROJECT_ROOT / "sql" / "staging"

STAGING_SCRIPTS = [
    "stg_customers.sql",
    "stg_geolocation.sql",
    "stg_orders.sql",
    "stg_order_items.sql",
    "stg_order_payments.sql",
    "stg_order_reviews.sql",
    "stg_products.sql",
    "stg_sellers.sql",
    "stg_product_category_translation.sql",
]


def run_sql_script(connection, script_name: str) -> None:
    script_path = STAGING_SQL_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"SQL script not found: {script_path}")

    try:
        connection.execute(script_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to run {script_path}: {exc}") from exc


def table_name_from_script(script_name: str) -> str:
    return f"staging.{Path(script_name).stem}"


def run_staging() -> dict[str, int]:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to run staging. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}. "
            "Run python src/ingestion/load_to_duckdb.py first."
        )

    row_counts: dict[str, int] = {}

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS staging")

        for script_name in STAGING_SCRIPTS:
            table_name = table_name_from_script(script_name)
            print(f"Running {script_name} -> {table_name}")
            run_sql_script(connection, script_name)
            row_count = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            row_counts[table_name] = int(row_count)

    return row_counts


def main() -> None:
    try:
        row_counts = run_staging()
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Staging tables created in {DATABASE_PATH}")
    for table_name, row_count in row_counts.items():
        print(f"- {table_name}: {row_count} rows")


if __name__ == "__main__":
    main()
