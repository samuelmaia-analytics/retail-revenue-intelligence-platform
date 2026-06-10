# Retail Revenue Intelligence Platform

Projeto de portfolio de **Data Analytics, Business Intelligence e Analytics
Engineering** desenvolvido por **Samuel Maia - Data Analyst / Analytics Engineer**.

## Resumo Executivo

O Retail Revenue Intelligence Platform transforma dados publicos de e-commerce em
uma base analitica local, testada e preparada para consumo no Power BI. O projeto
demonstra um fluxo completo de dados: ingestao de CSVs, padronizacao, modelagem
dimensional, documentacao de metricas, testes automatizados, consultas analiticas e
exportacao para dashboard.

A solucao usa o **Brazilian E-Commerce Public Dataset by Olist** apenas como fonte
publica de estudo. Este e um projeto independente de portfolio: nao foi desenvolvido para a
Olist, nao representa sua operacao atual e nao declara impacto comercial real.

## Entregaveis

- Pipeline reproduzivel em Python e SQL, com modos `full`, `sample` e `auto`.
- Banco analitico DuckDB organizado em `raw`, `staging` e `marts`.
- Modelo dimensional com quatro dimensoes e sete fatos.
- 15 queries analiticas para receita, operacao, clientes, pagamentos e sellers.
- Suite de qualidade de dados executada por pytest e GitHub Actions.
- Exportacao das tabelas finais para CSV em formato compativel com Power BI.
- Especificacao de dashboard com cinco paginas e catalogo de medidas DAX.
- Documentacao de arquitetura, metricas, perguntas de negocio e limitacoes.

## Aderencia Profissional

- **Analista de Dados:** perguntas de negocio, SQL analitico, metricas, investigacao
  de receita, clientes, pagamentos, reviews e entregas.
- **BI Analyst:** modelo dimensional, especificacao de dashboard, medidas DAX,
  relacionamentos e consumo no Power BI.
- **Analytics Engineer:** pipeline em camadas, grains explicitos, testes de dados,
  CI, documentacao e contratos de exportacao.

O repositorio demonstra competencias aplicadas a um projeto de portfolio. Ele nao
substitui experiencia em uma operacao produtiva nem afirma resultados de negocio
obtidos em uma empresa.

## Execucao Rapida

O modo sample usa os arquivos versionados e nao exige download do Kaggle:

```bash
git clone https://github.com/samuelmaia-analytics/retail-revenue-intelligence-platform.git
cd retail-revenue-intelligence-platform
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/ingestion/load_to_duckdb.py --mode sample
python src/transformation/run_staging.py
python src/transformation/run_marts.py
python src/transformation/export_powerbi_tables.py
python -m pytest
```

O exemplo acima usa Windows PowerShell. Os comandos de ativacao para Linux e macOS
estao na secao [Como Rodar Localmente](#como-rodar-localmente).

## Problema de Negocio

Uma operacao de marketplace precisa combinar informacoes comerciais, logisticas e
de experiencia do cliente para responder perguntas como:

- Como receita, pedidos e ticket medio evoluem ao longo do tempo?
- Quais categorias, produtos, estados e sellers concentram receita?
- Onde atrasos e cancelamentos apresentam maior incidencia?
- Qual e a relacao entre prazo de entrega e avaliacao do cliente?
- Quantos clientes voltam a comprar e quais segmentos concentram valor?
- Como meios de pagamento, parcelamento e frete se distribuem na operacao?

O projeto organiza essas perguntas em marts dimensionais, queries SQL documentadas e
uma especificacao de dashboard com cinco paginas.

## Fonte de Dados

A fonte e o **Brazilian E-Commerce Public Dataset by Olist**, disponibilizado
publicamente no Kaggle. Os arquivos sao anonimizados e incluem:

- pedidos;
- itens de pedidos;
- clientes;
- produtos e traducao de categorias;
- sellers;
- pagamentos;
- reviews;
- geolocalizacao.

O dataset completo nao e versionado neste repositorio. Uma amostra
referencialmente consistente com aproximadamente 1.000 pedidos fica em
`data/sample/olist/` para testes locais e integracao continua.

## Arquitetura

```text
Olist CSVs
    |
    v
Python ingestion
    |
    v
DuckDB: raw
    |
    v
DuckDB: staging (SQL)
    |
    v
DuckDB: marts (SQL)
    |
    +--> SQL analytical queries
    |
    +--> UTF-8 CSV exports
              |
              v
           Power BI
```

- **Raw:** preserva as entidades recebidas da fonte.
- **Staging:** aplica tipagem, limpeza e padronizacao.
- **Marts:** materializa dimensoes, fatos e agregados de negocio.
- **Analysis:** disponibiliza queries SQL para perguntas recorrentes.
- **Power BI:** consome CSVs exportados a partir do schema `marts`.

O banco local e criado em `data/processed/retail.duckdb`.

## Stack Tecnica

- **Python 3.11+** para ingestao, execucao do pipeline e exportacao.
- **DuckDB** como banco analitico local.
- **SQL** para staging, modelagem dimensional e analises.
- **Power BI** para visualizacao e camada semantica em DAX.
- **pytest** para testes automatizados de dados.
- **Ruff** e **Black** para qualidade e formatacao de codigo.
- **GitHub Actions** para integracao continua.
- **Markdown** para documentacao tecnica e de negocio.

## Estrutura do Repositorio

```text
.
|-- .github/workflows/       # Pipeline de integracao continua
|-- data/
|   |-- raw/                 # Dataset completo local, fora do Git
|   |-- processed/           # Banco DuckDB gerado
|   `-- sample/olist/        # Amostra Olist versionada
|-- docs/
|   |-- architecture/        # Arquitetura e modelo dimensional
|   |-- business/            # Contexto e perguntas de negocio
|   |-- data_dictionary/     # Dicionario de dados
|   `-- metrics/             # Definicoes de metricas
|-- powerbi/
|   |-- dashboard_specification.md
|   |-- dax_measures.md
|   `-- export/              # CSVs gerados, fora do Git
|-- app/
|   |-- streamlit_app.py     # Pagina inicial do app
|   |-- pages/               # Cinco paginas analiticas
|   `-- utils/               # Carregamento e graficos reutilizaveis
|-- sql/
|   |-- staging/             # Limpeza e padronizacao
|   |-- marts/               # Dimensoes e fatos
|   `-- analysis/            # Queries analiticas
|-- src/
|   |-- ingestion/           # Carga e geracao da amostra
|   |-- transformation/      # Execucao de modelos e exports
|   `-- quality/             # Validacoes executaveis
|-- tests/                   # Testes automatizados
|-- requirements.txt
`-- pyproject.toml
```

## Modelo Dimensional

### Dimensoes

- `marts.dim_customers`: cliente e localizacao.
- `marts.dim_products`: produto, categoria e atributos fisicos.
- `marts.dim_sellers`: seller e localizacao.
- `marts.dim_dates`: calendario analitico.

### Fatos

- `marts.fact_orders`: uma linha por pedido.
- `marts.fact_order_items`: uma linha por item do pedido.
- `marts.fact_payments`: uma linha por evento de pagamento.
- `marts.fact_reviews`: uma linha por review.
- `marts.fact_revenue_daily`: agregado por data, UF e categoria.
- `marts.fact_customer_retention`: uma linha por `customer_unique_id`.
- `marts.fact_seller_performance`: uma linha por seller.

Os grains sao documentados para evitar dupla contagem. Indicadores globais de
pedidos usam `fact_orders`; analises por produto, categoria ou seller usam
`fact_order_items`; retencao usa `customer_unique_id`.

## Metricas de Negocio

As definicoes, formulas, fontes e cuidados de interpretacao estao documentados em
[business_metrics.md](docs/metrics/business_metrics.md) e
[dax_measures.md](powerbi/dax_measures.md).

Principais metricas:

- Gross Revenue;
- Freight Value;
- Total Payment Value;
- Total Orders;
- Delivered Orders;
- Cancelled Orders e Cancellation Rate;
- Average Order Value;
- Late Delivery Rate;
- Average Delivery Days;
- Average Review Score;
- Review Comment Rate;
- Repeat Customers e Repeat Purchase Rate;
- receita por periodo, UF, categoria, produto e seller;
- mix de pagamentos e Average Installments.

`Gross Revenue` representa a soma de `item_price`. Frete e valor pago permanecem
separados porque representam conceitos diferentes.

> Receita bruta nao representa margem. O dataset nao possui custo de produto, por
> isso nenhuma medida de margem real foi criada.

## Data Quality e Testes

A suite em [test_data_quality.py](tests/test_data_quality.py) valida o banco DuckDB
em modo somente leitura. A cobertura inclui:

- nulidade e unicidade de identificadores;
- integridade referencial entre entidades;
- status de pedidos permitidos;
- tipos e faixas de valores;
- valores financeiros nao negativos;
- review score entre 1 e 5;
- unicidade no grain esperado dos marts;
- existencia das dimensoes e fatos obrigatorios;
- taxa de atraso por seller entre 0 e 1.

O workflow de CI roda em `push` e `pull_request`, executando Ruff, Black, pipeline
completo sobre a amostra Olist, exportacao para Power BI e pytest.

## Power BI Dashboard

O entregavel versionado e a especificacao para construcao do dashboard, acompanhada
das medidas DAX e dos CSVs gerados pelo pipeline. O arquivo `.pbix` nao faz parte do
repositorio.

O relatorio foi planejado em cinco paginas:

1. **Executive Overview**
2. **Revenue & Products**
3. **Delivery & Operations**
4. **Customers & Retention**
5. **Sellers & Reviews**

A especificacao de objetivos, tabelas, KPIs, visuais, filtros e insights esta em
[dashboard_specification.md](powerbi/dashboard_specification.md). As medidas DAX
recomendadas estao em [dax_measures.md](powerbi/dax_measures.md).

Campanhas de marketing nao fazem parte do dashboard principal porque o dataset nao
possui dados de campanha, investimento ou atribuicao.

## Streamlit App

O repositorio inclui uma aplicacao Streamlit para apresentar os principais
indicadores sem depender do Power BI Desktop. Ela usa exclusivamente os 11 CSVs
gerados em `powerbi/export/` e organiza a navegacao nas mesmas cinco areas
analiticas:

1. Visao Executiva
2. Receita e Produtos
3. Entrega e Operacao
4. Clientes e Retencao
5. Vendedores e Avaliacoes

Depois de executar o pipeline e exportar os marts, inicie a aplicacao:

```bash
streamlit run app/streamlit_app.py
```

Se o executavel `streamlit` nao estiver disponivel no `PATH`, use:

```bash
python -m streamlit run app/streamlit_app.py
```

Se os CSVs ainda nao existirem, o app informa o comando necessario:

```bash
python src/transformation/export_powerbi_tables.py
```

O Streamlit apresenta receita, pedidos, produtos, entregas, clientes, sellers e
reviews. Nao inclui campanhas de marketing e nao calcula margem real, pois essas
informacoes nao existem no dataset publico.

Na camada visual, o app traduz categorias, status e segmentos para nomes amigaveis
em portugues. IDs extensos de produtos e vendedores sao exibidos como rotulos
sequenciais, enquanto o identificador original permanece disponivel no tooltip.
Essas transformacoes sao apenas de apresentacao: os CSVs e o modelo analitico
preservam os valores originais.

## Como Rodar Localmente

### Pre-requisitos

- Python 3.11 ou superior.
- Git.
- Power BI Desktop, opcional, para construir o dashboard.

### Instalacao

```bash
git clone https://github.com/samuelmaia-analytics/retail-revenue-intelligence-platform.git
cd retail-revenue-intelligence-platform
python -m venv .venv
```

Ative o ambiente virtual:

```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux ou macOS
source .venv/bin/activate
```

Instale as dependencias:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Dependencias opcionais para notebooks e experimentacao:

```bash
pip install -r requirements-optional.txt
```

## Como Baixar o Dataset

1. Acesse o Kaggle e procure por **Brazilian E-Commerce Public Dataset by Olist**.
2. Baixe e extraia o dataset.
3. Coloque os nove arquivos abaixo em `data/raw/Brazilian E-commerce/`:

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_orders_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

Os CSVs completos permanecem fora do Git por causa do tamanho. O modo sample pode
ser executado sem download adicional.

## Como Executar o Pipeline

### Modo full

Usa os arquivos completos em `data/raw/Brazilian E-commerce/`:

```bash
python src/ingestion/load_to_duckdb.py --mode full
python src/transformation/run_staging.py
python src/transformation/run_marts.py
python src/transformation/export_powerbi_tables.py
```

### Modo sample

Usa a amostra versionada em `data/sample/olist/`:

```bash
python src/ingestion/load_to_duckdb.py --mode sample
python src/transformation/run_staging.py
python src/transformation/run_marts.py
python src/transformation/export_powerbi_tables.py
```

### Modo automatico

O comando sem argumentos usa o dataset completo quando os nove arquivos estao
disponiveis e faz fallback para a amostra:

```bash
python src/ingestion/load_to_duckdb.py
```

Para regenerar a amostra a partir do dataset completo:

```bash
python src/ingestion/generate_olist_sample.py --orders 1000
```

## Como Rodar os Testes

Execute primeiro ingestao, staging e marts. Depois:

```bash
python -m pytest
```

Validacoes adicionais:

```bash
python src/quality/run_data_tests.py
python -m ruff check src tests app main.py
python -m black --check src tests app main.py
```

## Limitacoes Conhecidas

- O dataset nao possui custo de produto. Portanto, margem real, lucro e
  rentabilidade nao foram calculados.
- O dataset nao possui campanhas, investimento em midia ou atribuicao. ROI de
  marketing ficou fora do escopo principal.
- O dataset e historico e publico; nao representa a operacao atual da Olist.
- A janela observada nao representa o ciclo de vida completo dos clientes.
- Reviews pertencem ao pedido e nao avaliam individualmente cada seller.
- A taxa de atraso por seller associa o resultado do pedido aos sellers
  participantes, sem isolar toda a responsabilidade logistica.
- O pipeline e local e usa carga completa, sem processamento incremental.
- A integracao com Power BI usa CSVs e nao possui atualizacao automatica por
  gateway.

## Melhorias Futuras

- Implementar carga incremental e controle de execucoes.
- Adicionar observabilidade, logs estruturados e historico de qualidade.
- Evoluir as transformacoes para dbt com lineage e testes declarativos.
- Adicionar testes de contrato para queries analiticas e exports do Power BI.
- Enriquecer cidades e UFs com fontes publicas geograficas e socioeconomicas.
- Automatizar publicacao e atualizacao do dashboard.
- Incorporar custos somente quando houver uma fonte confiavel e documentada.

## Contato Profissional

**Samuel Maia**<br>
Data Analyst / Analytics Engineer<br>
E-mail: `smaia2@gmail.com`
