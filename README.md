# Retail Revenue Intelligence Platform

Projeto de portfolio em Analytics Engineering para uma operacao brasileira de e-commerce, usando o dataset publico da Olist como fonte principal e DuckDB como banco analitico local.

O objetivo e demonstrar uma rotina profissional de dados: ingestao local, staging, modelagem dimensional, testes de qualidade, documentacao de metricas e exportacao para Power BI. O projeto roda localmente, sem credenciais e sem servicos pagos.

## Dataset

O dataset Olist cobre dados reais anonimizados de e-commerce brasileiro:

- Pedidos
- Clientes
- Produtos
- Vendedores
- Pagamentos
- Avaliacoes
- Localizacao
- Traducao de categorias de produto

O dataset nao possui dados reais de campanhas de marketing. Por isso, campanhas ficam fora do escopo principal do pipeline para evitar tabelas vazias ou analises artificiais.

## Problema de Negocio

Uma operacao de e-commerce precisa acompanhar crescimento de receita, rentabilidade, experiencia do cliente e eficiencia operacional. A plataforma organiza os dados em uma base analitica confiavel para responder perguntas como:

- Qual e a receita por categoria, UF, canal e periodo?
- Quais produtos e categorias concentram maior volume de vendas?
- Onde existem atrasos de entrega afetando a experiencia do cliente?
- Quais clientes compram mais de uma vez e quais estao em risco de churn?
- Como pagamentos, avaliacoes e operacao se conectam aos resultados comerciais?

## Stack

- Python para orquestracao local e scripts utilitarios.
- DuckDB como banco analitico local.
- SQL para staging e marts dimensionais.
- pytest, ruff e black para qualidade de codigo.
- Power BI Desktop para visualizacao.
- Markdown para documentacao de arquitetura, negocio, dicionario de dados e metricas.

## Estrutura do Projeto

```text
retail-revenue-intelligence-platform/
|-- data/
|   |-- raw/                 # Dataset Olist local, nao versionado
|   |-- processed/           # Banco DuckDB local
|   `-- sample/              # Pequenas amostras versionaveis
|-- notebooks/               # Exploracao e prototipacao
|-- src/
|   |-- ingestion/           # Carga de CSVs para DuckDB
|   |-- transformation/      # Execucao de staging, marts e exports
|   |-- quality/             # Testes de qualidade de dados
|   `-- utils/               # Funcoes compartilhadas
|-- sql/
|   |-- staging/             # Padronizacao das fontes raw
|   `-- marts/               # Modelo dimensional para BI
|-- powerbi/                 # Documentacao e exports para Power BI
|-- docs/                    # Arquitetura, negocio, dicionario e metricas
|-- tests/                   # Testes Python futuros
`-- .github/workflows/       # Integracao continua
```

## Camadas Analiticas

- Raw: arquivos Olist carregados no schema `raw`, preservando as entidades originais do dataset.
- Staging: limpeza tecnica, tipos de dados e nomes padronizados no schema `staging`.
- Marts: tabelas dimensionais e fatos no schema `marts`.
- Power BI: exports locais em CSV a partir das tabelas marts.

## Modelo Dimensional

Dimensoes:

- `marts.dim_customers`
- `marts.dim_products`
- `marts.dim_sellers`
- `marts.dim_dates`

Fatos:

- `marts.fact_orders`
- `marts.fact_order_items`
- `marts.fact_payments`
- `marts.fact_reviews`
- `marts.fact_revenue_daily`
- `marts.fact_customer_retention`
- `marts.fact_seller_performance`

## Principais Metricas

- GMV
- Receita liquida
- Ticket medio
- Pedidos aprovados e cancelados
- Margem bruta e margem percentual estimada
- Clientes ativos
- Frequencia de compra
- Retencao por cliente
- SLA e atraso de entrega

## Como Executar

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Para instalar tambem bibliotecas opcionais de notebooks, dbt e exploracao:

```bash
pip install -r requirements-optional.txt
```

### Baixar o dataset Olist

Baixe manualmente no Kaggle o **Brazilian E-Commerce Public Dataset by Olist**,
extraia os arquivos e coloque os nove CSVs em:

```text
data/raw/Brazilian E-commerce/
```

Arquivos esperados:

- `olist_customers_dataset.csv`
- `olist_geolocation_dataset.csv`
- `olist_orders_dataset.csv`
- `olist_order_items_dataset.csv`
- `olist_order_payments_dataset.csv`
- `olist_order_reviews_dataset.csv`
- `olist_products_dataset.csv`
- `olist_sellers_dataset.csv`
- `product_category_name_translation.csv`

Os CSVs completos nao sao versionados por causa do tamanho. O workflow de CI usa a
amostra Olist referencialmente consistente em `data/sample/olist/` quando os
arquivos completos nao estao disponiveis.

Execute o pipeline completo:

```bash
python src/ingestion/load_to_duckdb.py
python src/transformation/run_staging.py
python src/transformation/run_marts.py
python src/transformation/export_powerbi_tables.py
python src/quality/run_data_tests.py
```

Para executar apenas a camada staging:

```bash
python src/transformation/run_staging.py
```

Para executar apenas a camada marts:

```bash
python src/transformation/run_marts.py
```

Esse comando requer que a ingestao e a camada staging ja tenham sido executadas.

Para executar os testes automatizados de qualidade de dados:

```bash
pytest
```

Os testes usam o banco `data/processed/retail.duckdb`, portanto o pipeline deve ser
executado antes da suite.

## Integracao Continua

O workflow `.github/workflows/ci.yml` roda em `push` e `pull_request`. Ele instala
as dependencias, executa Ruff e Black, constroi as camadas `raw`, `staging` e
`marts`, exporta os CSVs para Power BI e executa pytest.

No GitHub Actions, o dataset completo normalmente nao esta presente. Nesse caso, o
workflow copia os arquivos de `data/sample/olist/` para a estrutura esperada em
`data/raw/`. Se a amostra estiver incompleta, o job falha com a lista de arquivos
ausentes.

Banco local gerado:

```text
data/processed/retail.duckdb
```

Exports para Power BI:

```text
powerbi/export/
```

## Future Improvements

- Enriquecer o dataset com dados simulados de campanhas de marketing.
- Criar analise de ROI por canal.
- Avaliar impacto de campanhas em recompra e receita.
