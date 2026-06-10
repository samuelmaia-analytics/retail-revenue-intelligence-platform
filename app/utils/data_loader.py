"""Shared data loading and filtering helpers for the Streamlit application."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "powerbi" / "export"

EXPECTED_TABLES = (
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
)

DATE_COLUMNS = {
    "dim_dates": ("full_date",),
    "fact_orders": (
        "order_date",
        "approved_date",
        "delivered_customer_date",
        "estimated_delivery_date",
    ),
    "fact_order_items": ("order_date",),
    "fact_reviews": ("review_creation_date", "review_answer_timestamp", "order_date"),
    "fact_revenue_daily": ("order_date",),
    "fact_customer_retention": ("first_order_date", "last_order_date"),
}

BOOLEAN_COLUMNS = {
    "dim_dates": ("is_weekend",),
    "fact_orders": ("is_delivered", "is_cancelled", "is_late_delivery"),
    "fact_reviews": ("has_review_comment", "is_late_delivery"),
}


class MissingExportError(FileNotFoundError):
    """Raised when one or more required Power BI exports are unavailable."""


def missing_exports() -> list[Path]:
    """Return the required CSV paths that do not exist."""
    return [
        EXPORT_DIR / f"{table_name}.csv"
        for table_name in EXPECTED_TABLES
        if not (EXPORT_DIR / f"{table_name}.csv").is_file()
    ]


def ensure_exports_exist() -> None:
    """Raise a clear error when the analytical CSV exports are unavailable."""
    missing = missing_exports()
    if not missing:
        return

    filenames = ", ".join(path.name for path in missing)
    raise MissingExportError(
        "Os CSVs analiticos ainda nao estao disponiveis. "
        "Execute `python src/transformation/export_powerbi_tables.py` "
        f"na raiz do projeto. Arquivos ausentes: {filenames}."
    )


@st.cache_data(show_spinner=False)
def load_table(table_name: str) -> pd.DataFrame:
    """Load and normalize one exported mart table."""
    if table_name not in EXPECTED_TABLES:
        raise ValueError(f"Tabela nao suportada: {table_name}")

    ensure_exports_exist()
    frame = pd.read_csv(EXPORT_DIR / f"{table_name}.csv", low_memory=False)

    for column in DATE_COLUMNS.get(table_name, ()):
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")

    for column in BOOLEAN_COLUMNS.get(table_name, ()):
        if column in frame.columns:
            frame[column] = (
                frame[column]
                .astype("string")
                .str.strip()
                .str.lower()
                .map({"true": True, "false": False})
                .astype("boolean")
            )

    return frame


def load_tables(*table_names: str) -> dict[str, pd.DataFrame]:
    """Load several exported tables through the shared Streamlit cache."""
    return {table_name: load_table(table_name) for table_name in table_names}


def render_export_error(error: MissingExportError) -> None:
    """Render the standard missing-data message and stop the current page."""
    st.error(str(error))
    st.code("python src/transformation/export_powerbi_tables.py", language="bash")
    st.stop()


def date_bounds(frame: pd.DataFrame, column: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Return valid minimum and maximum dates for a frame."""
    values = frame[column].dropna()
    if values.empty:
        today = pd.Timestamp.today().normalize()
        return today, today
    return values.min().normalize(), values.max().normalize()


def filter_frame(
    frame: pd.DataFrame,
    *,
    date_column: str | None = None,
    date_range: tuple[object, object] | None = None,
    state_column: str | None = None,
    states: Iterable[str] | None = None,
    category_column: str | None = None,
    categories: Iterable[str] | None = None,
    status_column: str | None = None,
    statuses: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Apply the common dashboard filters without mutating the cached frame."""
    mask = pd.Series(True, index=frame.index)

    if date_column and date_range:
        start_date, end_date = (pd.Timestamp(value) for value in date_range)
        mask &= frame[date_column].between(start_date, end_date, inclusive="both")

    if state_column and states:
        mask &= frame[state_column].isin(states)

    if category_column and categories:
        mask &= frame[category_column].fillna("unknown").isin(categories)

    if status_column and statuses:
        mask &= frame[status_column].isin(statuses)

    return frame.loc[mask].copy()


def format_brl(value: float) -> str:
    """Format a number as Brazilian currency without depending on OS locale."""
    formatted = f"{value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {formatted}"


def format_integer(value: int | float) -> str:
    """Format an integer with Brazilian thousands separators."""
    return f"{int(value):,}".replace(",", ".")


def format_percentage(value: float) -> str:
    """Format a decimal ratio as a percentage."""
    return f"{value:.1%}".replace(".", ",")


def format_decimal(value: float, decimal_places: int = 2) -> str:
    """Format a decimal using Brazilian separators."""
    return f"{value:.{decimal_places}f}".replace(".", ",")
