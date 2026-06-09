# Metricas de Negocio

## Visao Geral

Este documento define as metricas oficiais da Retail Revenue Intelligence Platform,
construida sobre o Brazilian E-Commerce Public Dataset by Olist. As definicoes
consideram a granularidade das tabelas da camada `marts` e devem orientar consultas
SQL, dashboards e validacoes de negocio.

Campanhas de marketing nao fazem parte do escopo principal. O dataset Olist nao
possui investimento em midia, impressoes, cliques, atribuicao ou identificadores de
campanha; portanto, metricas como ROI, CAC e conversao por campanha nao podem ser
calculadas de forma confiavel.

## Premissas de Interpretacao

- O Olist nao fornece custo do produto. Margem real nao deve ser calculada sem uma
  fonte externa de custos ou uma simulacao claramente identificada.
- O campo `price` da fonte `order_items` e padronizado como `item_price` na camada
  staging e representa o valor do item, sem o frete.
- O campo `freight_value` representa o valor de frete associado ao item.
- O campo `payment_value` pode possuir multiplos registros por pedido, inclusive
  quando o cliente utiliza pagamentos divididos.
- Metricas de retencao devem usar `customer_unique_id`, nunca apenas `customer_id`.
- Um pedido pode conter varios itens, categorias e vendedores. Contagens de pedidos
  em fatos no nivel de item devem usar `COUNT(DISTINCT order_id)`.
- Os valores observados representam apenas a janela temporal coberta pelo dataset.

## Catalogo de Metricas

### 1. Gross Revenue

- **Nome tecnico:** `gross_revenue`
- **Nome de negocio:** Gross Revenue
- **Descricao:** valor bruto das mercadorias vendidas, calculado a partir do preco
  dos itens.
- **Formula:** `SUM(marts.fact_order_items.item_price)`.
- **Tabela de origem:** `marts.fact_order_items`. Tambem esta materializada em
  `marts.fact_orders`, `marts.fact_revenue_daily`,
  `marts.fact_customer_retention` e `marts.fact_seller_performance`.
- **Granularidade recomendada:** item, pedido, data do pedido, categoria, vendedor
  ou UF do cliente.
- **Observacoes importantes:** `item_price` deriva do campo `price` de
  `order_items` e nao inclui `freight_value`.
- **Possiveis armadilhas de interpretacao:** nao tratar Gross Revenue como receita
  liquida, margem ou valor total pago. O dataset nao possui descontos e custos
  suficientes para essas interpretacoes.

### 2. Freight Revenue

- **Nome tecnico:** `freight_revenue`
- **Nome de negocio:** Freight Revenue
- **Descricao:** valor total de frete associado aos itens vendidos.
- **Formula:** `SUM(marts.fact_order_items.freight_value)`.
- **Tabela de origem:** `marts.fact_order_items`. O valor tambem esta agregado em
  `marts.fact_orders`, `marts.fact_revenue_daily` e
  `marts.fact_seller_performance`.
- **Granularidade recomendada:** item, pedido, data, categoria, vendedor, UF do
  vendedor ou UF do cliente.
- **Observacoes importantes:** o Olist registra o frete no nivel do item do pedido.
- **Possiveis armadilhas de interpretacao:** frete nao e receita de mercadoria nem
  custo logistico real. O campo representa o valor cobrado no pedido, nao o custo
  efetivamente incorrido pela operacao.

### 3. Total Payment Value

- **Nome tecnico:** `total_payment_value`
- **Nome de negocio:** Total Payment Value
- **Descricao:** valor total registrado nos eventos de pagamento dos pedidos.
- **Formula:** `SUM(marts.fact_payments.payment_value)`.
- **Tabela de origem:** `marts.fact_payments`; no nivel de pedido, usar
  `marts.fact_orders.total_payment_value`.
- **Granularidade recomendada:** pagamento, pedido ou tipo de pagamento.
- **Observacoes importantes:** um pedido pode possuir varios registros de
  `payment_value`, identificados por `payment_sequential`.
- **Possiveis armadilhas de interpretacao:** contar pagamentos nao equivale a
  contar pedidos. O valor pago tambem nao deve ser comparado diretamente com
  `gross_revenue`, pois pode incluir frete e combinacoes de pagamentos.

### 4. Total Orders

- **Nome tecnico:** `total_orders`
- **Nome de negocio:** Total Orders
- **Descricao:** quantidade de pedidos distintos.
- **Formula:** `COUNT(DISTINCT marts.fact_orders.order_id)`.
- **Tabela de origem:** `marts.fact_orders`; existe agregado no grain de
  `marts.fact_revenue_daily`.
- **Granularidade recomendada:** data do pedido, status, cidade ou UF do cliente.
- **Observacoes importantes:** `fact_orders` ja possui uma linha por pedido, mas
  `COUNT(DISTINCT)` torna a regra segura em consultas com joins.
- **Possiveis armadilhas de interpretacao:** contar linhas de `fact_order_items` ou
  `fact_payments` superestima o numero de pedidos.

### 5. Delivered Orders

- **Nome tecnico:** `delivered_orders`
- **Nome de negocio:** Delivered Orders
- **Descricao:** quantidade de pedidos cujo status foi classificado como entregue.
- **Formula:** `COUNT(DISTINCT CASE WHEN is_delivered THEN order_id END)`.
- **Tabela de origem:** `marts.fact_orders`; existe agregado em
  `marts.fact_revenue_daily`.
- **Granularidade recomendada:** data do pedido, cidade ou UF do cliente.
- **Observacoes importantes:** `is_delivered` deriva de
  `order_status = 'delivered'`.
- **Possiveis armadilhas de interpretacao:** nao inferir entrega apenas pela
  existencia de `delivered_customer_date`; a definicao oficial utiliza o status.

### 6. Cancelled Orders

- **Nome tecnico:** `cancelled_orders`
- **Nome de negocio:** Cancelled Orders
- **Descricao:** quantidade de pedidos classificados como cancelados.
- **Formula:** `COUNT(DISTINCT CASE WHEN is_cancelled THEN order_id END)`.
- **Tabela de origem:** `marts.fact_orders`; existe agregado em
  `marts.fact_revenue_daily`.
- **Granularidade recomendada:** data do pedido, cidade ou UF do cliente.
- **Observacoes importantes:** `is_cancelled` deriva de
  `order_status = 'canceled'`, conforme a grafia da fonte Olist.
- **Possiveis armadilhas de interpretacao:** pedidos cancelados podem possuir itens
  ou pagamentos registrados devido ao momento do cancelamento no ciclo operacional.

### 7. Cancellation Rate

- **Nome tecnico:** `cancellation_rate`
- **Nome de negocio:** Cancellation Rate
- **Descricao:** percentual de pedidos classificados como cancelados.
- **Formula:** `Cancelled Orders / Total Orders`.
- **Tabela de origem:** `marts.fact_orders`.
- **Granularidade recomendada:** data do pedido, mes, cidade ou UF do cliente.
- **Observacoes importantes:** numerador e denominador devem contar pedidos
  distintos dentro do mesmo contexto de filtro.
- **Possiveis armadilhas de interpretacao:** calcular a taxa no nivel de item pode
  dar peso maior a pedidos com mais produtos.

### 8. Late Delivery Rate

- **Nome tecnico:** `late_delivery_rate`
- **Nome de negocio:** Late Delivery Rate
- **Descricao:** percentual de pedidos entregues depois da data estimada.
- **Formula:** `COUNT(DISTINCT CASE WHEN is_late_delivery THEN order_id END) /
  COUNT(DISTINCT CASE WHEN is_delivered THEN order_id END)`.
- **Tabela de origem:** `marts.fact_orders`.
- **Granularidade recomendada:** data do pedido, mes, cidade ou UF do cliente.
- **Observacoes importantes:** um pedido e atrasado quando
  `delivered_customer_date > estimated_delivery_date`. Pedidos sem data de entrega
  nao entram no numerador.
- **Possiveis armadilhas de interpretacao:** a coluna `late_deliveries` de
  `fact_revenue_daily` e uma contagem, nao uma taxa. Somar pedidos entre categorias
  tambem pode duplicar pedidos com itens em mais de uma categoria.

### 9. Average Delivery Days

- **Nome tecnico:** `average_delivery_days`
- **Nome de negocio:** Average Delivery Days
- **Descricao:** media de dias corridos entre a compra e a entrega ao cliente.
- **Formula:** `AVG(marts.fact_orders.delivery_days)`.
- **Tabela de origem:** `marts.fact_orders`.
- **Granularidade recomendada:** data do pedido, mes, cidade ou UF do cliente.
- **Observacoes importantes:** aplicar `is_delivered = TRUE` e
  `delivery_days IS NOT NULL` para uma populacao comparavel.
- **Possiveis armadilhas de interpretacao:** incluir pedidos cancelados ou ainda nao
  entregues distorce o denominador e pode produzir uma leitura operacional incorreta.

### 10. Average Order Value

- **Nome tecnico:** `average_order_value`
- **Nome de negocio:** Average Order Value
- **Descricao:** valor medio de mercadorias por pedido.
- **Formula:** `SUM(gross_revenue) / COUNT(DISTINCT order_id)`.
- **Tabela de origem:** `marts.fact_orders`; tambem materializada em
  `marts.fact_revenue_daily`.
- **Granularidade recomendada:** data do pedido, mes, cidade ou UF do cliente.
- **Observacoes importantes:** o numerador utiliza apenas valor de itens, sem frete.
  Em `fact_revenue_daily`, a metrica esta no grain data, UF e categoria.
- **Possiveis armadilhas de interpretacao:** medias por categoria nao sao aditivas.
  Um pedido com varias categorias pode participar de mais de um grupo.

### 11. Average Review Score

- **Nome tecnico:** `average_review_score`
- **Nome de negocio:** Average Review Score
- **Descricao:** media das notas atribuidas pelos clientes aos pedidos avaliados.
- **Formula:** `AVG(marts.fact_reviews.review_score)`.
- **Tabela de origem:** `marts.fact_reviews`; existe uma media associada ao seller
  em `marts.fact_seller_performance`.
- **Granularidade recomendada:** avaliacao, data da avaliacao, data do pedido, UF do
  cliente ou indicador de atraso.
- **Observacoes importantes:** as notas do Olist variam de 1 a 5 e nem todo pedido
  possui avaliacao.
- **Possiveis armadilhas de interpretacao:** a media por seller associa a review do
  pedido aos sellers participantes; a fonte nao oferece uma avaliacao individual
  para cada vendedor.

### 12. Review Comment Rate

- **Nome tecnico:** `review_comment_rate`
- **Nome de negocio:** Review Comment Rate
- **Descricao:** percentual de avaliacoes que possuem titulo ou mensagem textual.
- **Formula:** `COUNT(CASE WHEN has_review_comment THEN review_id END) /
  COUNT(review_id)`.
- **Tabela de origem:** `marts.fact_reviews`.
- **Granularidade recomendada:** data da avaliacao, nota, UF do cliente ou indicador
  de atraso.
- **Observacoes importantes:** `has_review_comment` e verdadeiro quando existe
  titulo ou mensagem nao vazia.
- **Possiveis armadilhas de interpretacao:** ausencia de comentario nao significa
  avaliacao negativa; a nota deve ser analisada separadamente.

### 13. Repeat Customers

- **Nome tecnico:** `repeat_customers`
- **Nome de negocio:** Repeat Customers
- **Descricao:** quantidade de compradores unicos com dois ou mais pedidos.
- **Formula:** `COUNT(CASE WHEN total_orders >= 2 THEN customer_unique_id END)`.
- **Tabela de origem:** `marts.fact_customer_retention`.
- **Granularidade recomendada:** cliente unico, segmento ou coorte da primeira
  compra.
- **Observacoes importantes:** a identidade obrigatoria e `customer_unique_id`.
- **Possiveis armadilhas de interpretacao:** usar `customer_id` subestima recompra,
  pois esse identificador esta associado ao cliente de um pedido especifico no
  modelo Olist.

### 14. Repeat Purchase Rate

- **Nome tecnico:** `repeat_purchase_rate`
- **Nome de negocio:** Repeat Purchase Rate
- **Descricao:** percentual de compradores unicos que realizaram pelo menos dois
  pedidos.
- **Formula:** `Repeat Customers / COUNT(customer_unique_id)`.
- **Tabela de origem:** `marts.fact_customer_retention`.
- **Granularidade recomendada:** segmento ou coorte da primeira compra.
- **Observacoes importantes:** numerador e denominador devem usar
  `customer_unique_id` no mesmo periodo de observacao.
- **Possiveis armadilhas de interpretacao:** clientes adquiridos perto do fim do
  dataset tiveram menos tempo para recomprar, gerando censura temporal.

### 15. Customer Lifetime Revenue

- **Nome tecnico:** `customer_lifetime_revenue`
- **Nome de negocio:** Customer Lifetime Revenue
- **Descricao:** receita bruta de mercadorias acumulada por comprador dentro da
  janela do dataset.
- **Formula:** `SUM(gross_revenue) BY customer_unique_id`.
- **Tabela de origem:** `marts.fact_customer_retention`.
- **Granularidade recomendada:** `customer_unique_id` ou segmento de cliente.
- **Observacoes importantes:** representa receita historica observada, nao valor
  futuro esperado.
- **Possiveis armadilhas de interpretacao:** nao chamar a metrica de LTV financeiro
  sem horizonte projetado, margem, churn e custo de aquisicao. O Olist nao fornece
  custo do produto para calcular margem real.

### 16. Days Since Last Purchase

- **Nome tecnico:** `days_since_last_purchase`
- **Nome de negocio:** Days Since Last Purchase
- **Descricao:** numero de dias entre a ultima compra do cliente e a maior data de
  pedido disponivel no dataset.
- **Formula:** `DATE_DIFF('day', last_order_date, dataset_max_order_date)`.
- **Tabela de origem:** `marts.fact_customer_retention`, coluna
  `days_since_last_order`.
- **Granularidade recomendada:** `customer_unique_id` ou segmento de cliente.
- **Observacoes importantes:** a referencia e a maior `order_date` do dataset, nao
  a data atual do sistema.
- **Possiveis armadilhas de interpretacao:** usar a data corrente em uma base
  historica faria todos os clientes parecerem artificialmente inativos.

### 17. Revenue by State

- **Nome tecnico:** `revenue_by_state`
- **Nome de negocio:** Revenue by State
- **Descricao:** Gross Revenue agrupada pela UF do cliente.
- **Formula:** `SUM(gross_revenue) GROUP BY customer_state`.
- **Tabela de origem:** `marts.fact_orders` ou `marts.fact_revenue_daily`.
- **Granularidade recomendada:** UF do cliente e data do pedido.
- **Observacoes importantes:** a dimensao geografica representa o destino do pedido,
  nao a localizacao do vendedor.
- **Possiveis armadilhas de interpretacao:** nao misturar `customer_state` com
  `seller_state`. Ao usar `fact_revenue_daily`, categorias podem ser somadas para
  receita, mas nao para contagens globais de pedidos.

### 18. Revenue by Product Category

- **Nome tecnico:** `revenue_by_product_category`
- **Nome de negocio:** Revenue by Product Category
- **Descricao:** Gross Revenue agrupada pela categoria traduzida do produto.
- **Formula:** `SUM(item_price) GROUP BY product_category_name_english`.
- **Tabela de origem:** `marts.fact_order_items` ou
  `marts.fact_revenue_daily`.
- **Granularidade recomendada:** categoria, data do pedido e UF do cliente.
- **Observacoes importantes:** quando a traducao nao existe, a categoria original e
  mantida em `product_category_name_english`.
- **Possiveis armadilhas de interpretacao:** um pedido pode aparecer em varias
  categorias. Receita e aditiva entre categorias, mas a contagem de pedidos exige
  deduplicacao no nivel desejado.

### 19. Revenue by Seller State

- **Nome tecnico:** `revenue_by_seller_state`
- **Nome de negocio:** Revenue by Seller State
- **Descricao:** Gross Revenue agrupada pela UF do vendedor.
- **Formula:** `SUM(item_price) GROUP BY seller_state`.
- **Tabela de origem:** `marts.fact_order_items`; para valores ja agregados por
  vendedor, usar `marts.fact_seller_performance`.
- **Granularidade recomendada:** UF do vendedor, vendedor e data do pedido.
- **Observacoes importantes:** descreve a origem geografica dos sellers, nao a
  distribuicao da demanda dos clientes.
- **Possiveis armadilhas de interpretacao:** em
  `fact_seller_performance.gross_revenue`, cada linha ja representa o total de um
  seller. Nao fazer join com itens antes de agregar, pois isso duplicaria valores.

### 20. Seller Late Delivery Rate

- **Nome tecnico:** `seller_late_delivery_rate`
- **Nome de negocio:** Seller Late Delivery Rate
- **Descricao:** percentual dos pedidos associados ao seller que foram entregues
  depois da data estimada.
- **Formula:** `late_deliveries / total_orders`.
- **Tabela de origem:** `marts.fact_seller_performance`, coluna
  `late_delivery_rate`.
- **Granularidade recomendada:** seller ou UF do seller.
- **Observacoes importantes:** `late_deliveries` e `total_orders` contam pedidos
  distintos por seller. Ao agregar sellers, usar
  `SUM(late_deliveries) / SUM(total_orders)`, e nao a media simples das taxas.
- **Possiveis armadilhas de interpretacao:** o denominador implementado inclui todos
  os pedidos do seller, enquanto pedidos sem entrega nao entram como atrasados.
  Sellers com poucos pedidos tambem apresentam taxas mais volateis.

### 21. Payment Method Share

- **Nome tecnico:** `payment_method_share`
- **Nome de negocio:** Payment Method Share
- **Descricao:** participacao de cada meio de pagamento no valor total pago.
- **Formula:** `SUM(payment_value) BY payment_type / SUM(payment_value)`.
- **Tabela de origem:** `marts.fact_payments`.
- **Granularidade recomendada:** tipo de pagamento.
- **Observacoes importantes:** a definicao oficial e baseada em valor. Uma versao
  baseada em quantidade de registros deve receber outro nome e explicitar esse
  denominador.
- **Possiveis armadilhas de interpretacao:** pedidos com pagamento dividido aparecem
  em mais de uma linha e podem usar mais de um tipo. Participacao por contagem de
  registros nao equivale a participacao por pedidos ou por valor.

### 22. Average Installments

- **Nome tecnico:** `average_installments`
- **Nome de negocio:** Average Installments
- **Descricao:** numero medio de parcelas informado nos registros de pagamento.
- **Formula:** `AVG(marts.fact_payments.payment_installments)`.
- **Tabela de origem:** `marts.fact_payments`.
- **Granularidade recomendada:** tipo de pagamento.
- **Observacoes importantes:** a analise e mais representativa quando filtrada para
  meios de pagamento que suportam parcelamento, como cartao de credito.
- **Possiveis armadilhas de interpretacao:** meios como boleto e voucher podem
  registrar zero ou uma parcela por definicao. A media por registro tambem nao e
  necessariamente a media por pedido quando existem pagamentos divididos.

## Metricas Fora do Escopo

Metricas de campanhas de marketing nao integram o escopo principal porque nao
existem dados reais de campanha na fonte Olist. Qualquer exercicio futuro com
campanhas simuladas deve ser separado das metricas oficiais e identificar claramente
suas premissas.

Da mesma forma, margem bruta, margem liquida e rentabilidade real nao devem ser
publicadas sem dados de custo. Caso custos simulados sejam adicionados no futuro, as
metricas resultantes devem ser identificadas como estimativas.
