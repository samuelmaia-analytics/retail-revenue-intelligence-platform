# Resumo Tecnico

## Visao Geral

Retail Revenue Intelligence Platform e um projeto de portfolio de Analytics
Engineering voltado a um caso de e-commerce. A solucao implementa um pipeline local
e reproduzivel para ingestao, transformacao, teste, analise e disponibilizacao de
dados para Power BI.

O projeto prioriza separacao de responsabilidades, granularidades explicitas,
metricas documentadas e validacoes automatizadas. Ele nao representa uma
implementacao de producao da Olist.

## Fonte de Dados

A fonte principal e o **Brazilian E-Commerce Public Dataset by Olist**, composto por
arquivos CSV publicos e anonimizados sobre:

- pedidos e itens de pedidos;
- clientes e localizacao;
- produtos e traducao de categorias;
- vendedores;
- pagamentos;
- avaliacoes;
- eventos e previsoes de entrega.

Os arquivos de origem nao sao versionados no Git. O pipeline espera os CSVs em
`data/raw/Brazilian E-commerce/` e materializa o banco local em
`data/processed/retail.duckdb`.

## Arquitetura

O fluxo implementado e:

```text
CSV Olist
  -> Python ingestion
  -> DuckDB raw
  -> SQL staging
  -> SQL marts
  -> CSV UTF-8
  -> Power BI
```

### Raw

O schema `raw` preserva as entidades da fonte com pouca interferencia. A ingestao e
executada por `src/ingestion/load_to_duckdb.py`, que:

- verifica a disponibilidade dos arquivos esperados;
- cria ou substitui as tabelas da fonte;
- valida chaves obrigatorias;
- registra a quantidade de linhas carregadas.

### Staging

O schema `staging` aplica limpeza tecnica e padronizacao por meio de scripts SQL em
`sql/staging/`. Essa camada:

- converte datas, timestamps e valores numericos;
- normaliza textos, cidades e UFs;
- corrige nomes tecnicos da fonte;
- cria atributos reutilizaveis, como `order_date`, `delivery_days`,
  `is_late_delivery`, `has_review_comment` e `product_volume_cm3`.

O executor `src/transformation/run_staging.py` processa os modelos em ordem
deterministica e informa as contagens geradas.

### Marts

O schema `marts` materializa dimensoes e fatos em DuckDB. Os scripts ficam em
`sql/marts/` e sao executados por `src/transformation/run_marts.py`.

O executor:

- respeita a ordem de dependencias;
- executa cada modelo em transacao;
- interrompe o pipeline em caso de erro;
- rejeita tabelas criadas sem linhas;
- registra a quantidade de linhas de cada mart.

### Power BI

`src/transformation/export_powerbi_tables.py` exporta as tabelas principais para
`powerbi/export/` em CSV com cabecalho e encoding UTF-8. O processo valida a
existencia dos marts, escreve em arquivo temporario e substitui o destino somente
apos a exportacao ser concluida.

A pasta `powerbi/` tambem documenta relacionamentos, cinco paginas de dashboard e
medidas DAX sugeridas.

## Uso de DuckDB

DuckDB foi escolhido como banco analitico local por permitir:

- leitura eficiente de CSVs;
- transformacoes SQL sem dependencia de servidor;
- suporte a tipos analiticos, funcoes de janela e agregacoes;
- persistencia em um unico arquivo;
- execucao reproduzivel com baixo custo operacional;
- exportacao direta para CSV.

Essa escolha e adequada ao escopo de portfolio e ao volume do dataset. Ela reduz a
infraestrutura necessaria, mas nao substitui uma avaliacao de warehouse, seguranca,
concorrencia e orquestracao para um ambiente corporativo.

## Modelagem Dimensional

O modelo possui quatro dimensoes:

- `marts.dim_customers`
- `marts.dim_products`
- `marts.dim_sellers`
- `marts.dim_dates`

E sete fatos:

- `marts.fact_orders`
- `marts.fact_order_items`
- `marts.fact_payments`
- `marts.fact_reviews`
- `marts.fact_revenue_daily`
- `marts.fact_customer_retention`
- `marts.fact_seller_performance`

Os principais grains sao:

- uma linha por pedido em `fact_orders`;
- uma linha por item do pedido em `fact_order_items`;
- uma linha por evento de pagamento em `fact_payments`;
- uma linha por avaliacao em `fact_reviews`;
- uma linha por data, UF do cliente e categoria em `fact_revenue_daily`;
- uma linha por `customer_unique_id` em `fact_customer_retention`;
- uma linha por seller em `fact_seller_performance`.

A separacao de grains evita que pedidos, pagamentos e itens sejam tratados como a
mesma unidade analitica. Retencao usa `customer_unique_id`, pois `customer_id` nao
representa adequadamente o comprador ao longo de pedidos distintos no Olist.

## Metricas Documentadas

O catalogo em `docs/metrics/business_metrics.md` define formula, origem,
granularidade e riscos de interpretacao para metricas como:

- Gross Revenue e Freight Revenue;
- Total Payment Value;
- pedidos totais, entregues e cancelados;
- Cancellation Rate e Late Delivery Rate;
- Average Order Value e Average Delivery Days;
- Average Review Score e Review Comment Rate;
- Repeat Customers e Repeat Purchase Rate;
- receita por cliente, categoria, UF e seller;
- Payment Method Share e Average Installments.

As definicoes diferenciam valor dos itens, frete e pagamentos. Tambem registram
cuidados contra dupla contagem ao combinar fatos com grains diferentes.

## Testes de Qualidade

A suite `tests/test_data_quality.py` utiliza pytest e DuckDB em modo somente leitura.
Ela cobre:

- nulidade e unicidade de identificadores;
- integridade referencial entre pedidos, clientes, produtos, sellers e pagamentos;
- validade de status e tipos no staging;
- valores financeiros nao negativos;
- faixa valida de review score;
- unicidade dos fatos no grain esperado;
- limites da taxa de atraso por seller;
- existencia de todas as dimensoes e fatos esperados.

O projeto mantem tambem `src/quality/run_data_tests.py` como verificador executavel
do pipeline. Os testes nao incluem entidades de campanhas.

## Exportacao e Consumo

As quatro dimensoes e os sete fatos sao exportados para CSV. O script:

- cria `powerbi/export/` quando necessario;
- valida se todas as tabelas existem;
- informa a quantidade de linhas por arquivo;
- valida a leitura dos arquivos em UTF-8;
- nao exporta tabelas de campanhas.

No Power BI, o desenho recomendado usa dimensoes compartilhadas e relacionamentos
`1:*` com filtro simples. Fatos nao devem ser relacionados diretamente sem uma
dimensao ou ponte apropriada, para evitar caminhos ambiguos e multiplicacao de
metricas.

## Decisoes Tecnicas

- **Pipeline em camadas:** raw preserva a fonte, staging concentra limpeza e marts
  concentra regras analiticas.
- **SQL materializado:** tabelas sao recriadas para tornar a execucao local simples
  e previsivel.
- **Transacoes nos marts:** uma falha reverte a criacao do modelo corrente.
- **Grains explicitos:** cada fato documenta sua unidade de analise.
- **Receita baseada em itens:** `gross_revenue` usa `item_price`; frete e pagamentos
  permanecem metricas separadas.
- **Retencao por identidade unica:** `customer_unique_id` e usado para reconhecer
  recompra.
- **Referencia historica para recencia:** `days_since_last_order` usa a maior data
  do dataset, nao a data atual.
- **Media de review por seller sem peso por item:** uma review e contada uma vez por
  seller e pedido.
- **CSV como contrato com Power BI:** simplifica a demonstracao local e desacopla o
  dashboard do arquivo DuckDB.
- **Artefatos gerados fora do Git:** CSVs brutos, banco DuckDB, exports e arquivos
  Power BI nao sao versionados.

## Limitacoes Conhecidas

- O dataset nao possui custo de produto. Portanto, margem real, rentabilidade e
  lucro nao foram calculados.
- O dataset nao possui campanhas, investimento em midia ou atribuicao. Portanto,
  ROI de marketing ficou fora do escopo principal.
- O dataset e historico e publico; ele nao representa a operacao atual da Olist.
- Os dados sao anonimizados e cobrem apenas a janela disponibilizada pela fonte.
- Recencia, recompra e receita por cliente representam o periodo observado, nao o
  ciclo de vida completo do cliente.
- Reviews pertencem ao pedido como um todo, nao diretamente a cada seller.
- A taxa de atraso por seller associa o resultado de entrega aos sellers do pedido,
  mas nao isola toda a responsabilidade logistica.
- O pipeline e local e executado por scripts; nao possui scheduler, monitoramento,
  controle de acesso ou processamento incremental.
- A integracao com Power BI ocorre por CSV, sem atualizacao automatica por gateway.

## Melhorias Futuras

- Adicionar CI para executar pytest e validacoes de estilo a cada alteracao.
- Implementar carga incremental e controle de execucoes.
- Adicionar observabilidade, logs estruturados e historico de qualidade.
- Evoluir para dbt ou outra ferramenta de transformacao com lineage e testes
  declarativos.
- Criar dimensoes ou tabelas ponte para cenarios mais complexos no Power BI.
- Enriquecer cidades e UFs com dados publicos socioeconomicos e geograficos.
- Adicionar custos externos ou simulados, claramente identificados, para estimar
  margem.
- Avaliar campanhas simuladas em uma extensao separada do modelo oficial.
- Automatizar publicacao e atualizacao do dashboard quando houver infraestrutura
  apropriada.
