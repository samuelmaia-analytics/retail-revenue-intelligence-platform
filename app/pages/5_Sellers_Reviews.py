"""Sellers and reviews page."""

from __future__ import annotations

import streamlit as st
from app.utils.charts import bar_chart, scatter_chart
from app.utils.data_loader import (
    MissingExportError,
    format_brl,
    format_decimal,
    format_integer,
    format_percentage,
    load_table,
    render_export_error,
)
from app.utils.labels import add_masked_id_labels, build_masked_id_map

st.set_page_config(page_title="Vendedores e Avaliações", page_icon="⭐", layout="wide")
st.title("Vendedores e Avaliações")
st.caption("Desempenho dos vendedores considerando receita, volume, atrasos e avaliações.")

try:
    sellers = load_table("fact_seller_performance")
except MissingExportError as error:
    render_export_error(error)

seller_id_map = build_masked_id_map(sellers["seller_id"], "Vendedor")

with st.sidebar:
    st.header("Filtros")
    states = sorted(sellers["seller_state"].dropna().unique())
    selected_states = st.multiselect("UF do seller", states)
    maximum_orders = max(int(sellers["total_orders"].max()), 1)
    minimum_orders = st.slider(
        "Volume minimo de pedidos",
        min_value=1,
        max_value=maximum_orders,
        value=1,
    )

filtered = sellers[sellers["total_orders"] >= minimum_orders].copy()
if selected_states:
    filtered = filtered[filtered["seller_state"].isin(selected_states)]

if filtered.empty:
    st.warning("Nenhum seller encontrado para os filtros selecionados.")
    st.stop()

seller_count = filtered["seller_id"].nunique()
if seller_count == 1:
    st.info(
        "O filtro selecionado retorna apenas um vendedor. Os gráficos mostram o "
        "registro disponível, sem comparação entre vendedores."
    )
elif seller_count < 5:
    st.info(
        f"O filtro selecionado retorna {seller_count} vendedores. Considere ampliar "
        "os filtros para uma comparação mais representativa."
    )

total_sellers = filtered["seller_id"].nunique()
seller_orders = filtered["total_orders"].sum()
weighted_late_rate = filtered["late_deliveries"].sum() / seller_orders if seller_orders else 0
reviewed_order_weight = filtered.loc[filtered["average_review_score"].notna(), "total_orders"].sum()
weighted_review = (
    (filtered["average_review_score"] * filtered["total_orders"]).sum() / reviewed_order_weight
    if reviewed_order_weight
    else 0
)

metrics = st.columns(4)
metrics[0].metric("Total de vendedores", format_integer(total_sellers))
metrics[1].metric(
    "Receita media por vendedor",
    format_brl(filtered["gross_revenue"].mean()),
)
metrics[2].metric("Nota média das avaliações", format_decimal(weighted_review))
metrics[3].metric("Taxa média de atraso", format_percentage(weighted_late_rate))

top_revenue = filtered.nlargest(15, "gross_revenue").sort_values("gross_revenue")
state_summary = (
    filtered.groupby("seller_state", as_index=False)
    .agg(
        total_sellers=("seller_id", "nunique"),
        gross_revenue=("gross_revenue", "sum"),
    )
    .sort_values("gross_revenue", ascending=False)
)
late_volume_threshold = max(minimum_orders, 10)
late_candidates = filtered[filtered["total_orders"] >= late_volume_threshold]
uses_late_volume_fallback = late_candidates.empty
if uses_late_volume_fallback:
    late_candidates = filtered
top_late = late_candidates.nlargest(15, "late_delivery_rate").sort_values("late_delivery_rate")
top_reviews = (
    filtered[filtered["average_review_score"].notna()]
    .nlargest(15, "total_orders")
    .sort_values("average_review_score")
)
top_revenue = add_masked_id_labels(
    top_revenue,
    source="seller_id",
    target="seller_label",
    technical_target="technical_seller_id",
    prefix="Vendedor",
    id_map=seller_id_map,
)
top_late = add_masked_id_labels(
    top_late,
    source="seller_id",
    target="seller_label",
    technical_target="technical_seller_id",
    prefix="Vendedor",
    id_map=seller_id_map,
)
top_reviews = add_masked_id_labels(
    top_reviews,
    source="seller_id",
    target="seller_label",
    technical_target="technical_seller_id",
    prefix="Vendedor",
    id_map=seller_id_map,
)
scatter_sellers = add_masked_id_labels(
    filtered.dropna(subset=["average_review_score"]),
    source="seller_id",
    target="seller_label",
    technical_target="technical_seller_id",
    prefix="Vendedor",
    id_map=seller_id_map,
)


def seller_chart_height(row_count: int) -> int:
    """Keep small filtered selections compact and larger rankings readable."""
    return min(560, max(280, 42 * row_count + 100))


ranking_height = seller_chart_height(len(top_revenue))
late_chart_title = "Vendedores com maior taxa de atraso"
if uses_late_volume_fallback:
    late_chart_title += " (volume disponível no filtro)"

left, right = st.columns(2)
with left:
    st.plotly_chart(
        bar_chart(
            top_revenue,
            x="gross_revenue",
            y="seller_label",
            title="Vendedores com maior receita",
            orientation="h",
            height=ranking_height,
            hover_data={
                "gross_revenue": ":,.2f",
                "total_orders": ":,.0f",
                "technical_seller_id": True,
                "seller_id": False,
            },
        ),
        width="stretch",
    )
    if uses_late_volume_fallback:
        st.caption(
            "Nenhum vendedor no filtro atingiu 10 pedidos. O ranking de atraso "
            "considera o volume disponível e deve ser interpretado com cautela."
        )
    st.plotly_chart(
        bar_chart(
            top_late,
            x="late_delivery_rate",
            y="seller_label",
            title=late_chart_title,
            orientation="h",
            height=seller_chart_height(len(top_late)),
            hover_data={
                "late_delivery_rate": ":.1%",
                "total_orders": ":,.0f",
                "technical_seller_id": True,
                "seller_id": False,
            },
        ),
        width="stretch",
    )
with right:
    st.plotly_chart(
        bar_chart(
            state_summary.head(15).sort_values("gross_revenue"),
            x="gross_revenue",
            y="seller_state",
            title="Receita por estado do vendedor",
            orientation="h",
            height=seller_chart_height(len(state_summary.head(15))),
            hover_data={
                "gross_revenue": ":,.2f",
                "total_sellers": ":,.0f",
            },
        ),
        width="stretch",
    )
    st.plotly_chart(
        bar_chart(
            top_reviews,
            x="average_review_score",
            y="seller_label",
            title="Nota média dos vendedores com maior volume",
            orientation="h",
            height=seller_chart_height(len(top_reviews)),
            hover_data={
                "average_review_score": ":.2f",
                "total_orders": ":,.0f",
                "technical_seller_id": True,
                "seller_id": False,
            },
        ),
        width="stretch",
    )

st.plotly_chart(
    scatter_chart(
        scatter_sellers,
        x="late_delivery_rate",
        y="average_review_score",
        size="gross_revenue",
        color="seller_state",
        hover_name="seller_label",
        title="Relação entre atraso e avaliação",
        hover_data={
            "late_delivery_rate": ":.1%",
            "average_review_score": ":.2f",
            "gross_revenue": ":,.2f",
            "total_orders": ":,.0f",
            "technical_seller_id": True,
            "seller_id": False,
        },
    ),
    width="stretch",
)

st.caption(
    "As avaliações pertencem ao pedido. A nota por vendedor é uma associação aos "
    "pedidos em que ele participou, não uma avaliação individual direta."
)
