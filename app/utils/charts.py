"""Plotly chart helpers with a consistent dashboard style."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.utils.labels import COLUMN_LABELS

PRIMARY_COLOR = "#2563EB"
SECONDARY_COLOR = "#0F766E"
WARNING_COLOR = "#D97706"
NEGATIVE_COLOR = "#DC2626"
COLOR_SEQUENCE = [PRIMARY_COLOR, SECONDARY_COLOR, WARNING_COLOR, "#7C3AED", "#0891B2"]

CURRENCY_COLUMNS = {"gross_revenue", "item_price", "freight_value", "total_payment_value"}
PERCENTAGE_COLUMNS = {"late_delivery_rate", "cancellation_rate", "repeat_purchase_rate"}
INTEGER_COLUMNS = {
    "total_orders",
    "delivered_orders",
    "late_orders",
    "late_deliveries",
    "total_items",
    "total_customers",
    "total_sellers",
}
DECIMAL_COLUMNS = {"delivery_days", "review_score", "average_review_score"}


def _style_figure(figure: go.Figure, *, height: int = 420) -> go.Figure:
    figure.update_layout(
        height=height,
        margin={"l": 20, "r": 20, "t": 55, "b": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial, sans-serif", "color": "#263238"},
        legend_title_text="",
        hoverlabel={"bgcolor": "white"},
        separators=",.",
    )
    figure.update_xaxes(showgrid=False, linecolor="#D1D5DB")
    figure.update_yaxes(gridcolor="#E5E7EB", zeroline=False)
    return figure


def _axis_format(column: str) -> dict[str, object]:
    if column in CURRENCY_COLUMNS:
        return {"tickprefix": "R$ ", "tickformat": ",.2f"}
    if column in PERCENTAGE_COLUMNS:
        return {"tickformat": ".1%"}
    if column in INTEGER_COLUMNS:
        return {"tickformat": ",.0f"}
    if column in DECIMAL_COLUMNS:
        return {"tickformat": ".1f"}
    return {}


def _friendly_labels(overrides: dict[str, str] | None = None) -> dict[str, str]:
    labels = COLUMN_LABELS.copy()
    if overrides:
        labels.update(overrides)
    return labels


def _hover_value(column: str, axis: str) -> str:
    if column in CURRENCY_COLUMNS:
        return f"R$ %{{{axis}:,.2f}}"
    if column in PERCENTAGE_COLUMNS:
        return f"%{{{axis}:.1%}}"
    if column in INTEGER_COLUMNS:
        return f"%{{{axis}:,.0f}}"
    if column == "delivery_days":
        return f"%{{{axis}:.1f}} dias"
    if column in {"review_score", "average_review_score"}:
        return f"%{{{axis}:.2f}}"
    if column == "order_month":
        return f"%{{{axis}|%m/%Y}}"
    return f"%{{{axis}}}"


def _format_primary_hover(figure: go.Figure, *, x: str, y: str) -> None:
    for trace in figure.data:
        template = trace.hovertemplate
        if not template:
            continue
        for column, axis in ((x, "x"), (y, "y")):
            label = COLUMN_LABELS.get(column, column)
            template = template.replace(
                f"{label}=%{{{axis}}}",
                f"{label}={_hover_value(column, axis)}",
            )
        trace.hovertemplate = template


def line_chart(
    data: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    markers: bool = True,
    labels: dict[str, str] | None = None,
    hover_data: dict[str, object] | list[str] | None = None,
) -> go.Figure:
    figure = px.line(
        data,
        x=x,
        y=y,
        title=title,
        markers=markers,
        labels=_friendly_labels(labels),
        hover_data=hover_data,
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    figure.update_traces(line={"width": 3})
    _format_primary_hover(figure, x=x, y=y)
    figure.update_xaxes(**_axis_format(x))
    figure.update_yaxes(**_axis_format(y))
    return _style_figure(figure)


def bar_chart(
    data: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    orientation: str = "v",
    color: str | None = None,
    text_auto: str | bool = False,
    height: int = 420,
    labels: dict[str, str] | None = None,
    hover_data: dict[str, object] | list[str] | None = None,
    category_orders: dict[str, list[object]] | None = None,
) -> go.Figure:
    figure = px.bar(
        data,
        x=x,
        y=y,
        title=title,
        orientation=orientation,
        color=color,
        text_auto=text_auto,
        labels=_friendly_labels(labels),
        hover_data=hover_data,
        category_orders=category_orders,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    figure.update_traces(textposition="outside", cliponaxis=False)
    _format_primary_hover(figure, x=x, y=y)
    figure.update_xaxes(**_axis_format(x))
    figure.update_yaxes(**_axis_format(y))
    return _style_figure(figure, height=height)


def scatter_chart(
    data: pd.DataFrame,
    *,
    x: str,
    y: str,
    title: str,
    size: str | None = None,
    color: str | None = None,
    hover_name: str | None = None,
    labels: dict[str, str] | None = None,
    hover_data: dict[str, object] | list[str] | None = None,
) -> go.Figure:
    figure = px.scatter(
        data,
        x=x,
        y=y,
        title=title,
        size=size,
        color=color,
        hover_name=hover_name,
        labels=_friendly_labels(labels),
        hover_data=hover_data,
        color_discrete_sequence=COLOR_SEQUENCE,
        opacity=0.75,
    )
    _format_primary_hover(figure, x=x, y=y)
    figure.update_xaxes(**_axis_format(x))
    figure.update_yaxes(**_axis_format(y))
    return _style_figure(figure)


def histogram_chart(
    data: pd.DataFrame,
    *,
    x: str,
    title: str,
    bins: int = 30,
    labels: dict[str, str] | None = None,
    hover_data: dict[str, object] | list[str] | None = None,
) -> go.Figure:
    figure = px.histogram(
        data,
        x=x,
        nbins=bins,
        title=title,
        labels=_friendly_labels(labels),
        hover_data=hover_data,
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    _format_primary_hover(figure, x=x, y="count")
    figure.update_xaxes(**_axis_format(x))
    figure.update_yaxes(title_text=COLUMN_LABELS["count"], tickformat=",.0f")
    return _style_figure(figure)
