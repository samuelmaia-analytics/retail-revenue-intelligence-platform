"""Friendly labels and presentation-only translations for the Streamlit app."""

from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

COLUMN_LABELS = {
    "gross_revenue": "Receita bruta",
    "item_price": "Receita bruta",
    "freight_value": "Valor do frete",
    "total_payment_value": "Valor total pago",
    "total_orders": "Total de pedidos",
    "delivered_orders": "Pedidos entregues",
    "late_orders": "Pedidos atrasados",
    "late_deliveries": "Pedidos atrasados",
    "total_items": "Itens vendidos",
    "total_customers": "Total de clientes",
    "total_sellers": "Total de vendedores",
    "average_order_value": "Ticket médio",
    "late_delivery_rate": "Taxa de atraso",
    "delivery_days": "Dias de entrega",
    "average_review_score": "Nota média",
    "review_score": "Nota da avaliação",
    "customer_state": "Estado do cliente",
    "seller_state": "Estado do vendedor",
    "product_category_name_english": "Categoria do produto",
    "product_category_label": "Categoria do produto",
    "product_id": "Produto",
    "product_label": "Produto",
    "seller_id": "Vendedor",
    "seller_label": "Vendedor",
    "customer_segment": "Segmento de cliente",
    "customer_segment_label": "Segmento de cliente",
    "days_since_last_order": "Dias desde a última compra",
    "payment_type": "Forma de pagamento",
    "payment_installments": "Parcelas",
    "order_status": "Status do pedido",
    "order_status_label": "Status do pedido",
    "order_month": "Mês do pedido",
    "order_month_label": "Mês do pedido",
    "order_bucket": "Pedidos por cliente",
    "delivery_status": "Situação da entrega",
    "count": "Quantidade",
    "technical_product_id": "ID técnico do produto",
    "technical_seller_id": "ID técnico do vendedor",
}

PRODUCT_CATEGORY_LABELS = {
    "health_beauty": "Saúde e beleza",
    "watches_gifts": "Relógios e presentes",
    "bed_bath_table": "Cama, mesa e banho",
    "sports_leisure": "Esporte e lazer",
    "computers_accessories": "Informática e acessórios",
    "furniture_decor": "Móveis e decoração",
    "cool_stuff": "Utilidades e presentes",
    "housewares": "Utilidades domésticas",
    "auto": "Automotivo",
    "garden_tools": "Jardim e ferramentas",
    "toys": "Brinquedos",
    "baby": "Bebês",
    "perfumery": "Perfumaria",
    "telephony": "Telefonia",
    "office_furniture": "Móveis de escritório",
    "electronics": "Eletrônicos",
    "fashion_bags_accessories": "Moda, bolsas e acessórios",
    "pet_shop": "Pet shop",
    "stationery": "Papelaria",
    "consoles_games": "Consoles e games",
    "construction_tools_construction": "Construção e ferramentas",
    "home_appliances": "Eletrodomésticos",
    "musical_instruments": "Instrumentos musicais",
    "small_appliances": "Pequenos eletrodomésticos",
    "books_general_interest": "Livros",
    "food": "Alimentos",
    "drinks": "Bebidas",
    "audio": "Áudio",
    "unknown": "Categoria não informada",
}

ORDER_STATUS_LABELS = {
    "delivered": "Entregue",
    "shipped": "Enviado",
    "canceled": "Cancelado",
    "unavailable": "Indisponível",
    "invoiced": "Faturado",
    "processing": "Em processamento",
    "created": "Criado",
    "approved": "Aprovado",
}

CUSTOMER_SEGMENT_LABELS = {
    "inactive_customer": "Cliente inativo",
    "one_time_buyer": "Compra única",
    "repeat_buyer": "Cliente recorrente",
    "high_value_customer": "Cliente de alto valor",
}

DELIVERY_STATUS_LABELS = {
    True: "Pedido atrasado",
    False: "Pedido no prazo",
}


def friendly_product_category(value: object) -> str:
    """Translate an Olist category or format an unmapped value for display."""
    if pd.isna(value) or not str(value).strip():
        return PRODUCT_CATEGORY_LABELS["unknown"]

    normalized = str(value).strip().lower()
    if normalized in PRODUCT_CATEGORY_LABELS:
        return PRODUCT_CATEGORY_LABELS[normalized]

    return normalized.replace("_", " ").title()


def add_product_category_labels(
    frame: pd.DataFrame,
    *,
    source: str = "product_category_name_english",
    target: str = "product_category_label",
) -> pd.DataFrame:
    """Return a copy with a presentation-only Portuguese category column."""
    result = frame.copy()
    result[target] = result[source].map(friendly_product_category)
    return result


def translate_order_status(value: object) -> str:
    """Translate an Olist order status for visual display."""
    if pd.isna(value):
        return "Não informado"
    normalized = str(value).strip().lower()
    return ORDER_STATUS_LABELS.get(normalized, normalized.replace("_", " ").title())


def translate_customer_segment(value: object) -> str:
    """Translate a materialized customer segment for visual display."""
    if pd.isna(value):
        return "Não informado"
    normalized = str(value).strip().lower()
    return CUSTOMER_SEGMENT_LABELS.get(normalized, normalized.replace("_", " ").title())


def build_masked_id_map(values: Iterable[object], prefix: str) -> dict[str, str]:
    """Build stable sequential labels while keeping source IDs unchanged."""
    unique_values = sorted({str(value) for value in values if pd.notna(value)})
    width = max(3, len(str(len(unique_values))))
    return {
        value: f"{prefix} {index:0{width}d}" for index, value in enumerate(unique_values, start=1)
    }


def add_masked_id_labels(
    frame: pd.DataFrame,
    *,
    source: str,
    target: str,
    technical_target: str,
    prefix: str,
    id_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Return a copy with a masked label and a tooltip-only technical ID."""
    result = frame.copy()
    normalized_ids = result[source].astype("string")
    mapping = id_map or build_masked_id_map(normalized_ids, prefix)
    result[target] = normalized_ids.map(mapping).fillna(f"{prefix} não identificado")
    result[technical_target] = normalized_ids
    return result
