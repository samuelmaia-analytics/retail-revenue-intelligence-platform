"""Export marts tables from DuckDB to local files for Power BI."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"
EXPORT_DIR = PROJECT_ROOT / "powerbi" / "exports"

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


def export_marts() -> dict[str, Path]:
    try:
        import duckdb
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The 'duckdb' package is required to export marts. "
            "Install project dependencies with: pip install -r requirements.txt"
        ) from exc

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"DuckDB database not found: {DATABASE_PATH}. Run the ingestion pipeline first."
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    exported_files: dict[str, Path] = {}

    with duckdb.connect(str(DATABASE_PATH)) as connection:
        for table_name in MART_TABLES:
            output_path = EXPORT_DIR / f"{table_name}.csv"
            connection.execute(
                f"""
                COPY marts.{table_name}
                TO ?
                WITH (HEADER, DELIMITER ',')
                """,
                [str(output_path)],
            )
            exported_files[f"marts.{table_name}"] = output_path

    return exported_files


def main() -> None:
    try:
        exported_files = export_marts()
    except (FileNotFoundError, ModuleNotFoundError) as exc:
        print(f"ERROR: {exc}")
        raise SystemExit(1) from exc

    print(f"Power BI exports created in {EXPORT_DIR}")
    for table_name, output_path in exported_files.items():
        print(f"- {table_name}: {output_path}")


if __name__ == "__main__":
    main()
