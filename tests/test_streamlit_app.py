"""Smoke tests for the Streamlit application and exported data contract."""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import pytest
from app.utils.charts import bar_chart
from app.utils.data_loader import EXPECTED_TABLES, load_table
from app.utils.labels import (
    add_masked_id_labels,
    friendly_product_category,
    translate_customer_segment,
    translate_order_status,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATHS = [
    PROJECT_ROOT / "app" / "streamlit_app.py",
    *sorted((PROJECT_ROOT / "app" / "pages").glob("*.py")),
]
RUNNING_IN_CI = os.getenv("CI") == "true"


@pytest.mark.parametrize("table_name", EXPECTED_TABLES)
def test_streamlit_export_table_loads(table_name: str) -> None:
    frame = load_table(table_name)
    assert isinstance(frame, pd.DataFrame)
    assert not frame.empty


@pytest.mark.parametrize("app_path", APP_PATHS, ids=lambda path: path.name)
def test_streamlit_page_starts_without_exception(app_path: Path) -> None:
    if RUNNING_IN_CI:
        pytest.skip("Streamlit page rendering smoke test runs locally, not in GitHub Actions.")

    from streamlit.testing.v1 import AppTest

    app = AppTest.from_file(str(app_path), default_timeout=30)
    app.run(timeout=30)

    assert not app.exception


def test_friendly_product_category_uses_translation_and_fallback() -> None:
    assert friendly_product_category("health_beauty") == "Saúde e beleza"
    assert friendly_product_category("custom_new_category") == "Custom New Category"


def test_status_and_customer_segment_translations() -> None:
    assert translate_order_status("delivered") == "Entregue"
    assert translate_customer_segment("repeat_buyer") == "Cliente recorrente"


def test_masked_ids_preserve_technical_values() -> None:
    source = pd.DataFrame({"product_id": ["abc", "xyz"]})
    result = add_masked_id_labels(
        source,
        source="product_id",
        target="product_label",
        technical_target="technical_product_id",
        prefix="Produto",
    )

    assert result["product_label"].tolist() == ["Produto 001", "Produto 002"]
    assert result["technical_product_id"].tolist() == ["abc", "xyz"]


def test_chart_uses_friendly_axis_labels() -> None:
    figure = bar_chart(
        pd.DataFrame(
            {
                "customer_state": ["SP"],
                "gross_revenue": [1000.0],
            }
        ),
        x="gross_revenue",
        y="customer_state",
        title="Receita por estado do cliente",
        orientation="h",
    )

    assert figure.layout.xaxis.title.text == "Receita bruta"
    assert figure.layout.yaxis.title.text == "Estado do cliente"
    assert figure.layout.xaxis.tickprefix == "R$ "
    assert "R$ %{x:,.2f}" in figure.data[0].hovertemplate
