"""Delivery and operations page."""

from __future__ import annotations

import streamlit as st
from app.utils.charts import bar_chart, line_chart
from app.utils.data_loader import (
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
from app.utils.labels import DELIVERY_STATUS_LABELS, translate_order_status

st.set_page_config(page_title="Entrega e Operação", page_icon="🚚", layout="wide")
st.title("Entrega e Operação")
st.caption(
    "Monitoramento de prazos, atrasos, status dos pedidos e impacto na " "experiência do cliente."
)

try:
    tables = load_tables("fact_orders", "fact_reviews")
except MissingExportError as error:
    render_export_error(error)

orders = tables["fact_orders"]
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
    statuses = sorted(orders["order_status"].dropna().unique())
    status_options = {translate_order_status(status): status for status in statuses}
    selected_status_labels = st.multiselect("Status do pedido", sorted(status_options))
    selected_statuses = [status_options[label] for label in selected_status_labels]

if len(selected_dates) != 2:
    st.info("Selecione uma data inicial e uma data final.")
    st.stop()

filtered = filter_frame(
    orders,
    date_column="order_date",
    date_range=selected_dates,
    state_column="customer_state",
    states=selected_states,
    status_column="order_status",
    statuses=selected_statuses,
)

if filtered.empty:
    st.warning("Nenhum pedido encontrado para os filtros selecionados.")
    st.stop()

delivered_frame = filtered[filtered["is_delivered"].fillna(False)].copy()
delivered = delivered_frame["order_id"].nunique()
late = int(delivered_frame["is_late_delivery"].fillna(False).sum())

metrics = st.columns(4)
metrics[0].metric("Taxa de atraso", format_percentage(late / delivered if delivered else 0))
metrics[1].metric(
    "Prazo médio de entrega",
    f"{format_decimal(delivered_frame['delivery_days'].mean(), 1)} dias" if delivered else "N/D",
)
metrics[2].metric(
    "Frete médio por pedido",
    format_brl(filtered["freight_value"].mean()),
)
metrics[3].metric("Pedidos entregues", format_integer(delivered))

state_delivery = (
    delivered_frame.groupby("customer_state", as_index=False)
    .agg(
        delivered_orders=("order_id", "nunique"),
        late_orders=("is_late_delivery", "sum"),
    )
    .assign(late_delivery_rate=lambda frame: frame["late_orders"] / frame["delivered_orders"])
    .sort_values("late_delivery_rate", ascending=False)
)
monthly_delivery = (
    delivered_frame.assign(
        order_month=delivered_frame["order_date"].dt.to_period("M").dt.to_timestamp()
    )
    .groupby("order_month", as_index=False)["delivery_days"]
    .mean()
)
status_orders = (
    filtered.groupby("order_status", as_index=False)["order_id"]
    .nunique()
    .rename(columns={"order_id": "total_orders"})
    .sort_values("total_orders", ascending=False)
)
status_orders["order_status_label"] = status_orders["order_status"].map(translate_order_status)

filtered_reviews = reviews[reviews["order_id"].isin(set(filtered["order_id"]))].copy()
filtered_reviews["delivery_status"] = filtered_reviews["is_late_delivery"].map(
    DELIVERY_STATUS_LABELS
)
review_impact = (
    filtered_reviews.dropna(subset=["delivery_status", "review_score"])
    .groupby("delivery_status", as_index=False)["review_score"]
    .mean()
)

left, right = st.columns(2)
with left:
    st.plotly_chart(
        bar_chart(
            state_delivery.head(15).sort_values("late_delivery_rate"),
            x="late_delivery_rate",
            y="customer_state",
            title="Taxa de atraso por estado",
            orientation="h",
            hover_data={
                "late_delivery_rate": ":.1%",
                "delivered_orders": ":,.0f",
                "late_orders": ":,.0f",
            },
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
        line_chart(
            monthly_delivery,
            x="order_month",
            y="delivery_days",
            title="Prazo médio de entrega por mês",
            hover_data={"delivery_days": ":.1f"},
        ),
        width="stretch",
    )
    if review_impact.empty:
        st.info("Nao ha reviews suficientes para comparar atraso e avaliacao.")
    else:
        st.plotly_chart(
            bar_chart(
                review_impact,
                x="delivery_status",
                y="review_score",
                title="Avaliação média: pedidos no prazo vs. atrasados",
                hover_data={"review_score": ":.2f"},
            ),
            width="stretch",
        )
