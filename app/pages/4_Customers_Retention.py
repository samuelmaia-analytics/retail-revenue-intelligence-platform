"""Customers and retention page."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from app.utils.charts import bar_chart, histogram_chart
from app.utils.data_loader import (
    MissingExportError,
    format_brl,
    format_integer,
    format_percentage,
    load_table,
    render_export_error,
)
from app.utils.labels import translate_customer_segment

st.set_page_config(page_title="Clientes e Retenção", page_icon="👥", layout="wide")
st.title("Clientes e Retenção")
st.caption(
    "Análise de recorrência, valor e recência dos clientes com base em " "`customer_unique_id`."
)

try:
    customers = load_table("fact_customer_retention")
except MissingExportError as error:
    render_export_error(error)

with st.sidebar:
    st.header("Filtros")
    segments = sorted(customers["customer_segment"].dropna().unique())
    segment_options = {translate_customer_segment(segment): segment for segment in segments}
    selected_segment_labels = st.multiselect("Segmento de cliente", sorted(segment_options))
    selected_segments = [segment_options[label] for label in selected_segment_labels]
    maximum_orders = max(int(customers["total_orders"].max()), 1)
    order_range = st.slider(
        "Pedidos por cliente",
        min_value=1,
        max_value=maximum_orders,
        value=(1, maximum_orders),
    )

filtered = customers[
    customers["total_orders"].between(order_range[0], order_range[1], inclusive="both")
].copy()
if selected_segments:
    filtered = filtered[filtered["customer_segment"].isin(selected_segments)]

if filtered.empty:
    st.warning("Nenhum cliente encontrado para os filtros selecionados.")
    st.stop()

unique_customers = filtered["customer_unique_id"].nunique()
repeat_customers = filtered.loc[filtered["total_orders"] >= 2, "customer_unique_id"].nunique()

metrics = st.columns(4)
metrics[0].metric("Clientes únicos", format_integer(unique_customers))
metrics[1].metric("Clientes recorrentes", format_integer(repeat_customers))
metrics[2].metric(
    "Taxa de recompra",
    format_percentage(repeat_customers / unique_customers if unique_customers else 0),
)
metrics[3].metric(
    "Receita média por cliente",
    format_brl(filtered["gross_revenue"].mean()),
)

filtered["customer_segment_label"] = filtered["customer_segment"].map(translate_customer_segment)
segments_frame = (
    filtered.groupby("customer_segment_label", as_index=False)
    .agg(
        total_customers=("customer_unique_id", "nunique"),
        gross_revenue=("gross_revenue", "sum"),
    )
    .sort_values("total_customers", ascending=False)
)
orders_distribution = (
    filtered.assign(
        order_bucket=pd.cut(
            filtered["total_orders"],
            bins=[0, 1, 2, 3, 5, float("inf")],
            labels=["1", "2", "3", "4-5", "6+"],
        )
    )
    .groupby("order_bucket", observed=False, as_index=False)["customer_unique_id"]
    .nunique()
    .rename(columns={"customer_unique_id": "total_customers"})
)

left, right = st.columns(2)
with left:
    st.plotly_chart(
        bar_chart(
            segments_frame,
            x="customer_segment_label",
            y="total_customers",
            title="Distribuição por segmento de cliente",
            hover_data={"total_customers": ":,.0f"},
        ),
        width="stretch",
    )
    st.plotly_chart(
        bar_chart(
            segments_frame,
            x="customer_segment_label",
            y="gross_revenue",
            title="Receita por segmento de cliente",
            hover_data={"gross_revenue": ":,.2f"},
        ),
        width="stretch",
    )
with right:
    st.plotly_chart(
        bar_chart(
            orders_distribution,
            x="order_bucket",
            y="total_customers",
            title="Distribuição de clientes por quantidade de pedidos",
            hover_data={"total_customers": ":,.0f"},
        ),
        width="stretch",
    )
    st.plotly_chart(
        histogram_chart(
            filtered,
            x="days_since_last_order",
            title="Distribuição de dias desde a última compra",
            bins=30,
        ),
        width="stretch",
    )

st.caption(
    "A recência usa a maior data do dataset como referência, preservando a "
    "coerência histórica da base."
)
