"""Project entrypoint for local development checks."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    """Print a concise project status message."""
    database_path = PROJECT_ROOT / "data" / "processed" / "retail.duckdb"

    print("Retail Revenue Intelligence Platform")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Local DuckDB path: {database_path}")


if __name__ == "__main__":
    main()
