"""Executive overview page."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "pyproject.toml").is_file()
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.charts import bar_chart, line_chart  # noqa: E402
from app.utils.data_loader import (  # noqa: E402
    MissingExportError,
    date_bounds,
    filter_frame,
    format_brl,
    format_decimal,
    format_integer,
    format_percentage,
    load_tables,
    render_export_error,
)
from app.utils.labels import (  # noqa: E402
    add_product_category_labels,
    translate_order_status,
)

st.set_page_config(page_title="Visão Executiva", page_icon="📈", layout="wide")
st.title("Visão Executiva")
st.caption("Visão consolidada de receita, pedidos, entregas e satisfação dos clientes.")

try:
    tables = load_tables("fact_orders", "fact_order_items", "fact_reviews")
except MissingExportError as error:
    render_export_error(error)

orders = tables["fact_orders"]
items = tables["fact_order_items"]
reviews = tables["fact_reviews"]

minimum_date, maximum_date = date_bounds(orders, "order_date")
with st.sidebar:
    st.header("Filtros")
    selected_dates = st.date_input(
        "Periodo",
        value=(minimum_date.date(), maximum_date.date()),
        min_value=minimum_date.date(),
        max_value=maximum_date.date(),
    )
    states = sorted(orders["customer_state"].dropna().unique())
    selected_states = st.multiselect("UF do cliente", states)

if len(selected_dates) != 2:
    st.info("Selecione uma data inicial e uma data final.")
    st.stop()

filtered_orders = filter_frame(
    orders,
    date_column="order_date",
    date_range=selected_dates,
    state_column="customer_state",
    states=selected_states,
)
order_ids = set(filtered_orders["order_id"])
filtered_items = items[items["order_id"].isin(order_ids)].copy()
filtered_reviews = reviews[reviews["order_id"].isin(order_ids)].copy()

total_orders = filtered_orders["order_id"].nunique()
gross_revenue = filtered_orders["gross_revenue"].sum()
delivered = int(filtered_orders["is_delivered"].fillna(False).sum())
cancelled = int(filtered_orders["is_cancelled"].fillna(False).sum())
late = int(filtered_orders["is_late_delivery"].fillna(False).sum())

metrics = st.columns(7)
metrics[0].metric("Receita bruta", format_brl(gross_revenue))
metrics[1].metric("Total de pedidos", format_integer(total_orders))
metrics[2].metric(
    "Ticket médio",
    format_brl(gross_revenue / total_orders if total_orders else 0),
)
metrics[3].metric("Pedidos entregues", format_integer(delivered))
metrics[4].metric("Pedidos cancelados", format_integer(cancelled))
metrics[5].metric(
    "Taxa de atraso",
    format_percentage(late / delivered if delivered else 0),
)
metrics[6].metric(
    "Nota média das avaliações",
    (
        format_decimal(filtered_reviews["review_score"].mean())
        if not filtered_reviews.empty
        else "N/D"
    ),
)

if filtered_orders.empty:
    st.warning("Nenhum pedido encontrado para os filtros selecionados.")
    st.stop()

monthly = (
    filtered_orders.assign(
        order_month=filtered_orders["order_date"].dt.to_period("M").dt.to_timestamp()
    )
    .groupby("order_month", as_index=False)["gross_revenue"]
    .sum()
)
state_revenue = (
    filtered_orders.groupby("customer_state", as_index=False)["gross_revenue"]
    .sum()
    .sort_values("gross_revenue", ascending=False)
)
status_orders = (
    filtered_orders.groupby("order_status", as_index=False)["order_id"]
    .nunique()
    .rename(columns={"order_id": "total_orders"})
    .sort_values("total_orders", ascending=False)
)
status_orders["order_status_label"] = status_orders["order_status"].map(translate_order_status)
category_revenue = (
    add_product_category_labels(filtered_items)
    .groupby("product_category_label", as_index=False)["item_price"]
    .sum()
    .nlargest(10, "item_price")
    .sort_values("item_price")
)

left, right = st.columns(2)
with left:
    st.plotly_chart(
        line_chart(
            monthly,
            x="order_month",
            y="gross_revenue",
            title="Evolução mensal da receita",
            hover_data={"gross_revenue": ":,.2f"},
        ),
        width="stretch",
    )
    st.plotly_chart(
        bar_chart(
            status_orders,
            x="order_status_label",
            y="total_orders",
            title="Distribuição de pedidos por status",
            hover_data={"total_orders": ":,.0f", "order_status": False},
        ),
        width="stretch",
    )
with right:
    st.plotly_chart(
        bar_chart(
            state_revenue.head(15).sort_values("gross_revenue"),
            x="gross_revenue",
            y="customer_state",
            title="Receita por estado do cliente",
            orientation="h",
            hover_data={"gross_revenue": ":,.2f"},
        ),
        width="stretch",
    )
    st.plotly_chart(
        bar_chart(
            category_revenue,
            x="item_price",
            y="product_category_label",
            title="Categorias com maior receita",
            orientation="h",
            hover_data={"item_price": ":,.2f"},
        ),
        width="stretch",
    )
