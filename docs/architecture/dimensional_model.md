# Modelo Dimensional

## Visao Geral

O projeto transforma o Brazilian E-Commerce Public Dataset by Olist em um modelo
dimensional materializado no DuckDB e preparado para consumo por ferramentas de BI.
O modelo combina dimensoes descritivas com fatos transacionais e tabelas agregadas.

Os principais dominios analiticos sao:

- receita de mercadorias e frete;
- pedidos, itens e pagamentos;
- clientes e retencao;
- produtos e categorias;
- vendedores e desempenho operacional;
- entregas e avaliacoes.

As tabelas possuem granularidades diferentes. Por isso, joins entre fatos devem
respeitar suas chaves e grains para evitar duplicacao de receita, pedidos ou
avaliacoes. Por exemplo, `fact_orders` possui uma linha por pedido, enquanto
`fact_order_items` possui uma linha por item do pedido.

O dataset Olist nao possui dados de campanhas de marketing, investimento em midia,
atribuicao ou canal de aquisicao. Consequentemente, campanhas nao fazem parte do
escopo principal e o modelo nao cria `dim_campaigns`, `fact_campaigns` ou metricas
artificiais de campanha.

## Camadas de Dados

### Raw

A camada `raw` armazena os CSVs da Olist no DuckDB com estrutura proxima a fonte.
Ela funciona como registro dos dados recebidos e ponto de entrada reproduzivel para
o pipeline.

Responsabilidades:

- preservar os dados de origem;
- manter rastreabilidade entre arquivo e tabela;
- evitar regras de negocio prematuras;
- fornecer a entrada para a camada staging.

Principais tabelas:

- `raw.customers`
- `raw.geolocation`
- `raw.orders`
- `raw.order_items`
- `raw.order_payments`
- `raw.order_reviews`
- `raw.products`
- `raw.sellers`
- `raw.product_category_translation`

### Staging

A camada `staging` aplica limpeza tecnica e padronizacao sem alterar
desnecessariamente a granularidade das entidades de origem.

Responsabilidades:

- converter datas, timestamps e valores numericos;
- padronizar identificadores, textos, cidades e UFs;
- corrigir nomes tecnicos inconsistentes da fonte;
- calcular atributos reutilizaveis, como `order_date`, `is_late_delivery`,
  `delivery_days`, `has_review_comment` e `product_volume_cm3`;
- disponibilizar nomes de colunas estaveis para a camada marts.

As tabelas seguem o padrao `staging.stg_<entidade>`, incluindo
`stg_customers`, `stg_orders`, `stg_order_items`, `stg_products` e as demais
entidades da Olist.

### Marts

A camada `marts` organiza os dados para analise de negocio. As dimensoes oferecem
contexto descritivo; os fatos registram eventos ou metricas em grains explicitamente
definidos.

Responsabilidades:

- reduzir a complexidade de joins para consumidores analiticos;
- centralizar definicoes de receita, entrega, retencao e desempenho;
- oferecer tabelas transacionais para analises detalhadas;
- materializar agregados para dashboards recorrentes;
- manter grains previsiveis e testaveis.

## Dimensoes

### `marts.dim_customers`

**Objetivo:** descrever o cliente associado a cada pedido e disponibilizar sua
localizacao.

**Granularidade:** uma linha por `customer_id`.

**Principais colunas:**

- `customer_id`: identificador do cliente associado ao pedido;
- `customer_unique_id`: identificador usado para reconhecer o mesmo comprador em
  diferentes pedidos;
- `customer_zip_prefix`: prefixo do CEP;
- `customer_city`;
- `customer_state`.

**Analises permitidas:**

- distribuicao de clientes por cidade e UF;
- receita e pedidos por localizacao do cliente;
- relacionamento entre pedidos e clientes;
- consolidacao de compras recorrentes por `customer_unique_id`.

No Olist, `customer_id` nao deve ser usado sozinho para medir retencao. A entidade
adequada para esse objetivo e `customer_unique_id`.

### `marts.dim_products`

**Objetivo:** descrever produtos, categorias e atributos fisicos. A categoria em
ingles vem da tabela de traducao; quando nao existe traducao, a categoria original e
mantida.

**Granularidade:** uma linha por `product_id`.

**Principais colunas:**

- `product_id`;
- `product_category_name`;
- `product_category_name_english`;
- `product_name_length`;
- `product_description_length`;
- `product_photos_qty`;
- `product_weight_g`;
- `product_length_cm`;
- `product_height_cm`;
- `product_width_cm`;
- `product_volume_cm3`.

**Analises permitidas:**

- receita e quantidade vendida por produto ou categoria;
- composicao do catalogo;
- relacao entre atributos fisicos, frete e desempenho comercial;
- identificacao de categorias sem traducao.

### `marts.dim_sellers`

**Objetivo:** descrever os vendedores do marketplace e sua localizacao.

**Granularidade:** uma linha por `seller_id`.

**Principais colunas:**

- `seller_id`;
- `seller_zip_prefix`;
- `seller_city`;
- `seller_state`.

**Analises permitidas:**

- distribuicao geografica de vendedores;
- receita e volume por vendedor ou UF de origem;
- comparacao entre estado do vendedor e estado do cliente;
- segmentacao geografica da performance operacional.

### `marts.dim_dates`

**Objetivo:** fornecer um calendario analitico continuo entre a menor e a maior
`order_date` disponivel no dataset.

**Granularidade:** uma linha por data.

**Principais colunas:**

- `date_id`;
- `full_date`;
- `year`;
- `quarter`;
- `month`;
- `month_name`;
- `week`;
- `day`;
- `day_of_week`;
- `day_name`;
- `is_weekend`.

**Analises permitidas:**

- tendencias diarias, semanais, mensais e trimestrais;
- sazonalidade de pedidos e receita;
- comparacao entre dias uteis e fins de semana;
- filtros temporais consistentes em dashboards.

## Fatos

### `marts.fact_orders`

**Objetivo:** consolidar o ciclo do pedido, os dados do cliente e as principais
metricas financeiras e operacionais no nivel do pedido.

**Granularidade:** uma linha por `order_id`.

**Principais colunas:**

- identificadores: `order_id`, `customer_id`, `customer_unique_id`;
- localizacao: `customer_state`, `customer_city`;
- ciclo do pedido: `order_status`, `order_date`, `approved_date`,
  `delivered_customer_date`, `estimated_delivery_date`;
- indicadores: `is_delivered`, `is_cancelled`, `is_late_delivery`,
  `delivery_days`;
- metricas: `gross_revenue`, `freight_value`, `total_payment_value`,
  `total_items`.

**Analises permitidas:**

- receita bruta e ticket medio por pedido;
- pedidos entregues, cancelados e atrasados;
- prazo medio de entrega;
- receita e operacao por periodo, cidade ou UF;
- diferenca entre valor de mercadorias, frete e valor pago.

`gross_revenue` corresponde a soma de `item_price`. `total_payment_value`
corresponde a soma dos registros de pagamento e pode incluir frete ou mais de uma
forma de pagamento. As duas metricas representam conceitos diferentes e nao devem
ser tratadas como equivalentes.

### `marts.fact_order_items`

**Objetivo:** representar a venda no nivel mais detalhado disponivel, conectando
pedido, produto, vendedor e cliente.

**Granularidade:** uma linha por combinacao de `order_id` e `order_item_id`.

**Principais colunas:**

- `order_id`;
- `order_item_id`;
- `product_id`;
- `seller_id`;
- `customer_id`;
- `order_date`;
- `item_price`;
- `freight_value`;
- `product_category_name_english`;
- `seller_state`;
- `customer_state`.

**Analises permitidas:**

- receita e volume por produto, categoria ou vendedor;
- frete por produto, categoria e rota geografica;
- comparacao entre origem do vendedor e destino do cliente;
- composicao dos pedidos e base para agregacoes diarias.

Contagens de pedidos realizadas a partir desta tabela devem usar
`COUNT(DISTINCT order_id)`, pois um pedido pode conter varios itens.

### `marts.fact_payments`

**Objetivo:** registrar os eventos de pagamento vinculados aos pedidos.

**Granularidade:** uma linha por pagamento do pedido, identificado por `order_id` e
`payment_sequential`.

**Principais colunas:**

- `order_id`;
- `payment_sequential`;
- `payment_type`;
- `payment_installments`;
- `payment_value`.

**Analises permitidas:**

- mix de meios de pagamento;
- valor pago por modalidade;
- comportamento de parcelamento;
- identificacao de pedidos com pagamentos divididos.

Uma linha de pagamento nao representa necessariamente um pedido unico. Contagens de
pedidos devem deduplicar `order_id`.

### `marts.fact_reviews`

**Objetivo:** relacionar a avaliacao do cliente ao pedido, ao desempenho de entrega
e a localizacao do consumidor.

**Granularidade:** uma linha por avaliacao.

**Principais colunas:**

- `review_id`;
- `order_id`;
- `review_score`;
- `has_review_comment`;
- `review_creation_date`;
- `review_answer_timestamp`;
- `order_date`;
- `is_late_delivery`;
- `customer_state`.

**Analises permitidas:**

- nota media por periodo e UF;
- relacao entre atraso de entrega e satisfacao;
- percentual de avaliacoes com comentario;
- tempo e volume de respostas a avaliacoes;
- experiencia do cliente associada ao ciclo do pedido.

### `marts.fact_revenue_daily`

**Objetivo:** materializar indicadores diarios de receita e operacao para consumo
eficiente em dashboards.

**Granularidade:** uma linha por `order_date`, `customer_state` e
`product_category_name_english`.

**Principais colunas:**

- dimensoes: `order_date`, `customer_state`,
  `product_category_name_english`;
- volume: `total_orders`, `total_items`;
- financeiro: `gross_revenue`, `freight_value`, `average_order_value`;
- operacao: `delivered_orders`, `cancelled_orders`, `late_deliveries`.

**Analises permitidas:**

- tendencia diaria de receita;
- desempenho por UF do cliente e categoria;
- ticket medio no grain da tabela;
- acompanhamento de entregas, cancelamentos e atrasos;
- priorizacao de regioes ou categorias com maior impacto.

Como um pedido pode conter itens de varias categorias, somar contagens de pedidos
entre categorias pode duplicar pedidos. Para totais globais de pedidos, a fonte
preferencial e `fact_orders`.

### `marts.fact_customer_retention`

**Objetivo:** consolidar recorrencia, valor e recencia de cada comprador durante a
janela observada no dataset.

**Granularidade:** uma linha por `customer_unique_id`.

**Principais colunas:**

- `customer_unique_id`;
- `first_order_date`;
- `last_order_date`;
- `total_orders`;
- `gross_revenue`;
- `total_items`;
- `days_between_first_and_last_order`;
- `days_since_last_order`;
- `customer_segment`.

**Analises permitidas:**

- clientes de compra unica e recorrentes;
- identificacao de clientes de alto valor;
- clientes inativos;
- receita e volume por segmento;
- recencia e intervalo entre primeira e ultima compra.

Os segmentos materializados sao `one_time_buyer`, `repeat_buyer`,
`high_value_customer` e `inactive_customer`. `days_since_last_order` usa a maior
data do dataset como referencia, e nao a data corrente, preservando a coerencia de
uma base historica.

### `marts.fact_seller_performance`

**Objetivo:** consolidar desempenho comercial, operacional e reputacional por
vendedor.

**Granularidade:** uma linha por `seller_id`.

**Principais colunas:**

- `seller_id`;
- `seller_state`;
- `total_orders`;
- `total_items`;
- `gross_revenue`;
- `freight_value`;
- `average_item_price`;
- `unique_products`;
- `unique_customers`;
- `late_deliveries`;
- `late_delivery_rate`;
- `average_review_score`.

**Analises permitidas:**

- ranking de vendedores por receita, pedidos ou itens;
- amplitude do catalogo e base de clientes;
- desempenho de entrega;
- comparacao entre atraso e avaliacao media;
- performance agregada por UF do vendedor.

A avaliacao media evita ponderar uma review pela quantidade de itens do mesmo
vendedor no pedido. Ainda assim, a review pertence ao pedido como um todo e nao
avalia individualmente cada seller, uma limitacao importante do dataset.

## Relacionamentos e Uso

Os principais relacionamentos analiticos sao:

- `dim_customers.customer_id` com `fact_orders.customer_id` e
  `fact_order_items.customer_id`;
- `dim_products.product_id` com `fact_order_items.product_id`;
- `dim_sellers.seller_id` com `fact_order_items.seller_id` e
  `fact_seller_performance.seller_id`;
- `dim_dates.full_date` com as colunas de data dos fatos;
- `fact_orders.order_id` com `fact_order_items`, `fact_payments` e
  `fact_reviews`.

Ao combinar fatos, a agregacao deve ocorrer antes do join ou usar chaves distintas
compativeis com o grain desejado. Essa pratica evita relacionamentos
muitos-para-muitos e inflacao de metricas financeiras.

## Fora do Escopo Principal

Campanhas de marketing nao integram o modelo principal porque a fonte Olist nao
oferece dados de campanha, investimento, impressoes, cliques, canal de aquisicao ou
atribuicao de pedidos.

Criar tabelas vazias ou inferir essas informacoes reduziria a confiabilidade do
projeto. Por esse motivo, ROI de campanha, CAC, conversao por canal e metricas
equivalentes nao sao apresentados como resultados reais da Olist.

## Future Improvements

- Adicionar campanhas simuladas, separadas dos dados reais e acompanhadas de
  premissas documentadas.
- Calcular ROI por canal quando existirem investimento e atribuicao confiaveis.
- Enriquecer clientes e vendedores com dados publicos de municipios e UFs.
- Adicionar margem estimada caso dados de custo de produto estejam disponiveis no
  futuro.
