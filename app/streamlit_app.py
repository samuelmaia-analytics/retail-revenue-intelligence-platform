"""Landing page and Portuguese navigation for the Streamlit application."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = next(
    parent for parent in Path(__file__).resolve().parents if (parent / "pyproject.toml").is_file()
)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.utils.data_loader import (  # noqa: E402
    MissingExportError,
    ensure_exports_exist,
    render_export_error,
)


def render_home() -> None:
    """Render the portfolio context and application instructions."""
    st.set_page_config(
        page_title="Retail Revenue Intelligence Platform",
        page_icon="📊",
        layout="wide",
    )

    st.title("Retail Revenue Intelligence Platform")
    st.caption("Projeto de portfólio | Samuel Maia - Data Analyst / Analytics Engineer")

    st.markdown("""
Esta aplicação apresenta uma leitura executiva do **Brazilian E-Commerce Public
Dataset by Olist**, disponibilizado publicamente no **Kaggle**. O conjunto é
histórico e anonimizado. O projeto é independente, foi desenvolvido para
portfólio e não representa uma solução criada para a Olist.
""")

    try:
        ensure_exports_exist()
    except MissingExportError as error:
        render_export_error(error)

    st.success("Os 11 arquivos analíticos foram encontrados em `powerbi/export/`.")

    st.subheader("Resumo executivo")
    st.markdown("""
O pipeline transforma CSVs da fonte em um modelo analítico testado, com indicadores
de receita, pedidos, produtos, entregas, clientes, vendedores, pagamentos e
avaliações. As páginas laterais permitem explorar os principais resultados sem
abrir o Power BI.
""")

    architecture, source, stack = st.columns(3)
    with architecture:
        st.markdown("### Arquitetura")
        st.markdown("`CSV Olist -> raw -> staging -> marts -> CSV -> Streamlit / Power BI`")
    with source:
        st.markdown("### Fonte de dados")
        st.markdown("Brazilian E-Commerce Public Dataset by Olist, disponível no Kaggle.")
    with stack:
        st.markdown("### Stack")
        st.markdown("Python, SQL, DuckDB, pandas, Plotly, Streamlit, Power BI e pytest.")

    st.subheader("Limites de interpretação")
    st.warning("""
- O dataset é público e histórico; não representa a operação atual da Olist.
- Não há custo de produto, portanto margem real não é calculada.
- Não há dados de campanhas de marketing, investimento ou atribuição.
""")

    st.info("Use a navegação lateral para abrir as cinco páginas analíticas.")


navigation = st.navigation(
    [
        st.Page(render_home, title="Início", icon="🏠", default=True),
        st.Page("pages/1_Executive_Overview.py", title="Visão Executiva", icon="📈"),
        st.Page("pages/2_Revenue_Products.py", title="Receita e Produtos", icon="🛍️"),
        st.Page("pages/3_Delivery_Operations.py", title="Entrega e Operação", icon="🚚"),
        st.Page(
            "pages/4_Customers_Retention.py",
            title="Clientes e Retenção",
            icon="👥",
        ),
        st.Page(
            "pages/5_Sellers_Reviews.py",
            title="Vendedores e Avaliações",
            icon="⭐",
        ),
    ]
)
navigation.run()
