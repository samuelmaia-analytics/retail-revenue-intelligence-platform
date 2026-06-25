"""Revenue and products page."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "pyproject.toml").is_file()
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.charts import bar_chart  # noqa: E402
from app.utils.data_loader import (  # noqa: E402
    MissingExportError,
    date_bounds,
    filter_frame,
    format_brl,
    format_integer,
    load_table,
    render_export_error,
)
from app.utils.labels import (  # noqa: E402
    add_masked_id_labels,
    add_product_category_labels,
    build_masked_id_map,
)

st.set_page_config(page_title="Receita e Produtos", page_icon="🛍️", layout="wide")
st.title("Receita e Produtos")
st.caption("Análise da composição da receita por categoria, produto, estado e frete.")

try:
    items = load_table("fact_order_items")
except MissingExportError as error:
    render_export_error(error)

items = add_product_category_labels(items)
product_id_map = build_masked_id_map(items["product_id"], "Produto")
minimum_date, maximum_date = date_bounds(items, "order_date")

with st.sidebar:
    st.header("Filtros")
    selected_dates = st.date_input(
        "Periodo",
        value=(minimum_date.date(), maximum_date.date()),
        min_value=minimum_date.date(),
        max_value=maximum_date.date(),
    )
    categories = sorted(items["product_category_label"].unique())
    selected_categories = st.multiselect("Categoria", categories)
    states = sorted(items["customer_state"].dropna().unique())
    selected_states = st.multiselect("UF do cliente", states)

if len(selected_dates) != 2:
    st.info("Selecione uma data inicial e uma data final.")
    st.stop()

filtered = filter_frame(
    items,
    date_column="order_date",
    date_range=selected_dates,
    state_column="customer_state",
    states=selected_states,
    category_column="product_category_label",
    categories=selected_categories,
)

if filtered.empty:
    st.warning("Nenhum item encontrado para os filtros selecionados.")
    st.stop()

gross_revenue = filtered["item_price"].sum()
total_orders = filtered["order_id"].nunique()
metrics = st.columns(4)
metrics[0].metric("Receita bruta", format_brl(gross_revenue))
metrics[1].metric("Itens vendidos", format_integer(len(filtered)))
metrics[2].metric(
    "Ticket médio por pedido",
    format_brl(gross_revenue / total_orders if total_orders else 0),
)
metrics[3].metric("Valor total do frete", format_brl(filtered["freight_value"].sum()))

category = (
    filtered.groupby("product_category_label", as_index=False)
    .agg(gross_revenue=("item_price", "sum"), freight_value=("freight_value", "sum"))
    .sort_values("gross_revenue", ascending=False)
)
products = (
    filtered.groupby("product_id", as_index=False)
    .agg(gross_revenue=("item_price", "sum"), total_items=("order_item_id", "count"))
    .nlargest(15, "gross_revenue")
    .sort_values("gross_revenue")
)
products = add_masked_id_labels(
    products,
    source="product_id",
    target="product_label",
    technical_target="technical_product_id",
    prefix="Produto",
    id_map=product_id_map,
)
states_frame = (
    filtered.groupby("customer_state", as_index=False)["item_price"]
    .sum()
    .rename(columns={"item_price": "gross_revenue"})
    .sort_values("gross_revenue", ascending=False)
)

left, right = st.columns(2)
with left:
    st.plotly_chart(
        bar_chart(
            category.head(15).sort_values("gross_revenue"),
            x="gross_revenue",
            y="product_category_label",
            title="Categorias com maior receita",
            orientation="h",
            hover_data={"gross_revenue": ":,.2f"},
        ),
        width="stretch",
    )
    st.plotly_chart(
        bar_chart(
            states_frame.head(15).sort_values("gross_revenue"),
            x="gross_revenue",
            y="customer_state",
            title="Receita por estado do cliente",
            orientation="h",
            hover_data={"gross_revenue": ":,.2f"},
        ),
        width="stretch",
    )
with right:
    st.plotly_chart(
        bar_chart(
            products,
            x="gross_revenue",
            y="product_label",
            title="Produtos com maior receita",
            orientation="h",
            height=500,
            hover_data={
                "gross_revenue": ":,.2f",
                "total_items": ":,.0f",
                "technical_product_id": True,
                "product_id": False,
            },
        ),
        width="stretch",
    )
    st.plotly_chart(
        bar_chart(
            category.nlargest(15, "freight_value").sort_values("freight_value"),
            x="freight_value",
            y="product_category_label",
            title="Valor de frete por categoria",
            orientation="h",
            hover_data={"freight_value": ":,.2f"},
        ),
        width="stretch",
    )
