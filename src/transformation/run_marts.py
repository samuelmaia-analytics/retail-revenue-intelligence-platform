"""Run DuckDB marts SQL scripts in dependency order."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"
MARTS_SQL_DIR = PROJECT_ROOT / "sql" / "marts"

MARTS_SCRIPTS = [
    "dim_customers.sql",
    "dim_products.sql",
    "dim_sellers.sql",
    "dim_dates.sql",
    "fact_orders.sql",
    "fact_order_items.sql",
    "fact_payments.sql",
    "fact_reviews.sql",
    "fact_revenue_daily.sql",
    "fact_customer_retention.sql",
    "fact_seller_performance.sql",
]


def run_sql_script(connection, script_name: str, table_name: str) -> int:
    script_path = MARTS_SQL_DIR / script_name

    if not script_path.exists():
        raise FileNotFoundError(f"SQL script not found: {script_path}")

    sql = script_path.read_text(encoding="utf-8")
    try:
        connection.execute("BEGIN TRANSACTION")
        connection.execute(sql)
        row_count = int(connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])
        if row_count == 0:
            raise RuntimeError(
                f"{table_name} was created with zero rows. "
                "Check the staging inputs and business filters."
            )
        connection.execute("COMMIT")
        return row_count
    except Exception as exc:
        connection.execute("ROLLBACK")
        if isinstance(exc, RuntimeError):
            raise
        raise RuntimeError(f"Failed to run {script_path}: {exc}") from exc


def table_name_from_script(script_name: str) -> str:
    return f"marts.{Path(script_name).stem}"


def run_marts() -> dict[str, int]:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to run marts. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}. "
            "Run python src/ingestion/load_to_duckdb.py first."
        )

    row_counts: dict[str, int] = {}

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS marts")

        for script_name in MARTS_SCRIPTS:
            table_name = table_name_from_script(script_name)
            print(f"Running {script_name} -> {table_name}")
            row_counts[table_name] = run_sql_script(connection, script_name, table_name)

    return row_counts


def main() -> None:
    try:
        row_counts = run_marts()
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Marts created in {DATABASE_PATH}")
    for table_name, row_count in row_counts.items():
        print(f"- {table_name}: {row_count} rows")


if __name__ == "__main__":
    main()
