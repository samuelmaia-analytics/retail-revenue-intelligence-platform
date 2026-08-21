# Retail Revenue Intelligence Platform

Projeto de portfólio em **Data Analytics, BI e Analytics Engineering** que transforma dados públicos de e-commerce em uma base analítica confiável para análise comercial, operacional e executiva.

> Projeto independente de portfólio com dados públicos do Olist. Não representa a operação atual da empresa nem declara impacto comercial real.

## O problema

Uma operação de marketplace precisa combinar vendas, clientes, pagamentos, produtos, sellers e entregas para responder perguntas como:

- Como receita, pedidos e ticket médio evoluem?
- Quais categorias, produtos, estados e sellers concentram receita?
- Onde atrasos e cancelamentos merecem atenção?
- Como experiência do cliente e logística se relacionam?
- Quais segmentos apresentam maior recorrência e valor?

## A solução

```text
CSVs públicos
  → ingestão Python
  → DuckDB Raw
  → Staging SQL
  → Marts dimensionais
  → Data Quality
  → análises SQL
  → Power BI / Streamlit
```

## Principais entregas

- Pipeline em Python e SQL com execução `full`, `sample` e `auto`.
- Banco analítico DuckDB em camadas `raw`, `staging` e `marts`.
- Modelo dimensional com dimensões, fatos e grains documentados.
- Queries analíticas para receita, operação, clientes, pagamentos e sellers.
- Testes automatizados de qualidade e integridade dos dados.
- Exportação de tabelas analíticas para consumo no Power BI.
- Aplicação Streamlit com visão executiva e páginas temáticas.
- Documentação de métricas, arquitetura e limitações do dataset.

## Valor demonstrado

O projeto demonstra como organizar dados brutos em uma camada analítica consistente, reduzir risco de dupla contagem por meio de grains explícitos, padronizar métricas e disponibilizar informação pronta para decisão em BI.

## Stack

**Dados e transformação:** Python, SQL, DuckDB, pandas  
**BI e visualização:** Power BI, DAX, Streamlit  
**Qualidade e engenharia:** pytest, Ruff, Black, GitHub Actions  
**Documentação:** Markdown, dicionário de dados e catálogo de métricas

## Principais métricas

- Receita bruta
- Pedidos e ticket médio
- Frete
- Cancelamento
- Atraso de entrega
- Avaliação média
- Clientes recorrentes
- Receita por categoria, estado e seller
- Mix de pagamentos

> O dataset não possui custo de produto; por isso, margem e lucro real não são calculados.

## Como revisar este projeto em 5 minutos

1. Leia esta página para entender o problema e a arquitetura.
2. Explore `sql/marts/` para ver a modelagem dimensional.
3. Veja `sql/analysis/` para as perguntas de negócio.
4. Abra `powerbi/` para medidas e especificação do dashboard.
5. Execute o Streamlit para visualizar a camada de consumo.

## Execução rápida

```bash
git clone https://github.com/samuelmaia-analytics/retail-revenue-intelligence-platform.git
cd retail-revenue-intelligence-platform
python -m venv .venv
pip install -r requirements.txt
python src/ingestion/load_to_duckdb.py --mode sample
python src/transformation/run_staging.py
python src/transformation/run_marts.py
python src/transformation/export_powerbi_tables.py
python -m pytest
python -m streamlit run app/streamlit_app.py
```

## Limitações

- Dataset histórico e público.
- Sem custo de produto ou mídia, portanto sem margem real ou ROI de marketing.
- Pipeline local e não incremental.
- Integração com Power BI baseada em arquivos exportados.

## Autor

Samuel Maia — Analista de Dados | Analytics Engineer

- LinkedIn: https://www.linkedin.com/in/samuelmaia-analytics/
- GitHub: https://github.com/samuelmaia-analytics
