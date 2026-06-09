"""Export the main DuckDB marts tables as UTF-8 CSV files for Power BI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"
EXPORT_DIR = PROJECT_ROOT / "powerbi" / "export"


@dataclass(frozen=True)
class ExportedTable:
    qualified_name: str
    output_path: Path
    row_count: int


MART_TABLES = [
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


def validate_mart_tables(connection: Any) -> None:
    existing_tables = {
        row[0]
        for row in connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'marts'
            """
        ).fetchall()
    }
    missing_tables = [table_name for table_name in MART_TABLES if table_name not in existing_tables]

    if missing_tables:
        missing = ", ".join(f"marts.{table_name}" for table_name in missing_tables)
        raise RuntimeError(
            f"Required marts tables were not found: {missing}. "
            "Run python src/transformation/run_marts.py first."
        )


def export_table(connection: Any, table_name: str) -> ExportedTable:
    qualified_name = f"marts.{table_name}"
    output_path = EXPORT_DIR / f"{table_name}.csv"
    temporary_path = output_path.with_suffix(".csv.tmp")
    row_count = int(connection.execute(f"SELECT COUNT(*) FROM {qualified_name}").fetchone()[0])

    try:
        # DuckDB writes CSV text as UTF-8 by default.
        connection.execute(
            f"""
            COPY {qualified_name}
            TO ?
            WITH (
                FORMAT CSV,
                HEADER TRUE,
                DELIMITER ',',
                QUOTE '"',
                ESCAPE '"'
            )
            """,
            [str(temporary_path)],
        )
        temporary_path.read_text(encoding="utf-8")
        temporary_path.replace(output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    return ExportedTable(
        qualified_name=qualified_name,
        output_path=output_path,
        row_count=row_count,
    )


def export_powerbi_tables() -> list[ExportedTable]:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to export Power BI tables. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}. Run the pipeline first."
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with duckdb.connect(str(DATABASE_PATH), read_only=True) as connection:
            validate_mart_tables(connection)
            return [export_table(connection, table_name) for table_name in MART_TABLES]
    except Exception as exc:
        if isinstance(exc, (FileNotFoundError, ModuleNotFoundError, RuntimeError)):
            raise
        raise RuntimeError(f"Failed to export Power BI tables: {exc}") from exc


def main() -> None:
    try:
        exported_tables = export_powerbi_tables()
    except (FileNotFoundError, ModuleNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Power BI CSV files created in {EXPORT_DIR}")
    for exported_table in exported_tables:
        print(
            f"- {exported_table.qualified_name}: "
            f"{exported_table.row_count} rows -> {exported_table.output_path}"
        )


if __name__ == "__main__":
    main()
