# Especificacao do Dashboard Power BI

## Objetivo

O dashboard apresenta uma visao executiva e analitica da operacao de e-commerce
representada pelo dataset Olist. O relatorio deve permitir acompanhar receita,
produtos, entregas, clientes, vendedores e avaliacoes usando os CSVs gerados em
`powerbi/export/`.

O escopo possui cinco paginas:

1. Executive Overview
2. Revenue & Products
3. Delivery & Operations
4. Customers & Retention
5. Sellers & Reviews

Nao deve existir pagina de campanhas de marketing. O dataset Olist nao possui
campanhas, investimento em midia ou atribuicao.

## Modelo Recomendado

Use relacionamentos `1:*`, com direcao de filtro simples da dimensao para o fato:

- `dim_dates[full_date]` -> `fact_orders[order_date]`
- `dim_dates[full_date]` -> `fact_order_items[order_date]`
- `dim_dates[full_date]` -> `fact_reviews[order_date]`
- `dim_customers[customer_id]` -> `fact_orders[customer_id]`
- `dim_customers[customer_id]` -> `fact_order_items[customer_id]`
- `dim_products[product_id]` -> `fact_order_items[product_id]`
- `dim_sellers[seller_id]` -> `fact_order_items[seller_id]`
- `dim_sellers[seller_id]` -> `fact_seller_performance[seller_id]`

Marque `dim_dates` como tabela de datas usando `full_date`. Classifique
`dim_dates[month_name]` por `dim_dates[month]`.

Evite relacionamentos bidirecionais e muitos-para-muitos entre fatos. As tabelas
`fact_customer_retention` e `fact_seller_performance` sao snapshots acumulados e
nao devem receber o mesmo filtro temporal dos fatos transacionais sem uma regra
explicita.

## Convencoes Visuais

- Formatar valores monetarios em BRL.
- Formatar taxas como percentual com uma ou duas casas decimais.
- Usar cores semanticas consistentes: verde para entregue/positivo, vermelho para
  cancelado/critico e amarelo para atraso/atencao.
- Exibir a data de atualizacao dos CSVs no relatorio.
- Manter filtros de periodo e UF sincronizados apenas nas paginas em que o fato
  responde corretamente a esses filtros.
- Incluir tooltips com denominador, volume e contexto das taxas.

## Pagina 1 - Executive Overview

### Objetivo da pagina

Apresentar a saude geral da operacao em uma unica tela, combinando desempenho
comercial, volume de pedidos, entrega e satisfacao do cliente.

### Tabelas usadas

- `fact_orders`
- `fact_order_items`
- `fact_reviews`
- `dim_dates`
- `dim_customers`

### KPIs principais

- Gross Revenue
- Total Orders
- Average Order Value
- Delivered Orders
- Cancelled Orders
- Late Delivery Rate
- Average Review Score

### Visuais recomendados

- Sete cartoes para os KPIs principais.
- Grafico de linha com Gross Revenue por ano e mes.
- Mapa preenchido ou barras horizontais com Gross Revenue por UF do cliente.
- Grafico de colunas empilhadas com pedidos entregues e cancelados por mes.
- Tooltip de pagina com pedidos, ticket medio e taxa de atraso da UF selecionada.

### Filtros recomendados

- Periodo por `dim_dates[full_date]`.
- Ano e mes.
- UF do cliente.
- Status do pedido.

### Medidas DAX sugeridas

- `[Gross Revenue]`
- `[Total Orders]`
- `[Average Order Value]`
- `[Delivered Orders]`
- `[Cancelled Orders]`
- `[Cancellation Rate]`
- `[Late Delivery Rate]`
- `[Average Review Score]`

### Insights esperados

- Meses de maior e menor receita.
- UFs com maior concentracao de vendas.
- Evolucao do ticket medio.
- Diferenca entre crescimento comercial e desempenho de entrega.
- Periodos com aumento simultaneo de cancelamentos ou atrasos.

## Pagina 2 - Revenue & Products

### Objetivo da pagina

Explicar a composicao da receita por categoria, produto e geografia, incluindo o
peso do frete e o volume de itens vendidos.

### Tabelas usadas

- `fact_order_items`
- `dim_products`
- `dim_dates`
- `dim_customers`

### KPIs principais

- Gross Revenue
- Items Sold
- Freight Value
- Category Average Order Value
- Total Orders at Item Grain

### Visuais recomendados

- Barras horizontais com Gross Revenue por categoria.
- Tabela ou matriz de top produtos por Gross Revenue, itens e pedidos.
- Grafico combinado com Gross Revenue e Freight Value por categoria.
- Mapa ou barras com Gross Revenue por UF do cliente.
- Treemap para participacao de receita por categoria.
- Grafico de dispersao com Gross Revenue, Freight Value e itens por categoria.

### Filtros recomendados

- Periodo.
- Categoria traduzida.
- Produto.
- UF do cliente.
- UF do vendedor.

### Medidas DAX sugeridas

- `[Gross Revenue]`
- `[Freight Value]`
- `[Items Sold]`
- `[Item Fact Orders]`
- `[Category Average Order Value]`
- `[Average Item Price]`
- `[Freight to Revenue Rate]`

### Insights esperados

- Categorias e produtos que concentram receita.
- Categorias com alto volume e baixo ticket.
- Produtos com maior contribuicao comercial.
- Categorias em que o frete representa maior proporcao do valor vendido.
- Diferencas regionais no mix de produtos.

Nao some Average Order Value entre categorias. Um pedido pode conter produtos de
mais de uma categoria.

## Pagina 3 - Delivery & Operations

### Objetivo da pagina

Monitorar eficiencia operacional, prazo de entrega, atrasos, cancelamentos e sua
relacao com a experiencia do cliente.

### Tabelas usadas

- `fact_orders`
- `fact_reviews`
- `fact_order_items`
- `dim_dates`
- `dim_customers`

### KPIs principais

- Late Delivery Rate
- Average Delivery Days
- Delivered Orders
- Cancelled Orders
- Cancellation Rate
- Average Freight per Order

### Visuais recomendados

- Cartoes com taxa de atraso, dias medios de entrega e frete medio.
- Mapa ou barras com Late Delivery Rate por UF do cliente.
- Grafico de colunas com pedidos por `order_status`.
- Colunas agrupadas com Average Review Score para entregas no prazo e atrasadas.
- Grafico de linha com Late Delivery Rate por mes.
- Matriz por UF com pedidos, atraso, dias de entrega e frete.

### Filtros recomendados

- Periodo.
- UF e cidade do cliente.
- Status do pedido.
- Situacao de atraso.
- Review score.

### Medidas DAX sugeridas

- `[Late Delivery Rate]`
- `[Average Delivery Days]`
- `[Delivered Orders]`
- `[Cancelled Orders]`
- `[Cancellation Rate]`
- `[Average Review Score]`
- `[Average Freight per Order]`

### Insights esperados

- Regioes com maior risco de atraso.
- Periodos de degradacao do prazo de entrega.
- Diferenca de avaliacao entre pedidos no prazo e atrasados.
- Status operacionais com maior volume.
- Relacao entre frete, distancia geografica e nivel de servico.

## Pagina 4 - Customers & Retention

### Objetivo da pagina

Avaliar tamanho da base, recorrencia, valor dos segmentos e recencia de compra dos
clientes usando `customer_unique_id`.

### Tabelas usadas

- `fact_customer_retention`
- `fact_orders`
- `dim_customers`

### KPIs principais

- Unique Customers
- Repeat Customers
- Repeat Purchase Rate
- Customer Lifetime Revenue
- Average Days Since Last Purchase
- Average Orders per Customer

### Visuais recomendados

- Cartoes com clientes unicos, recorrentes e taxa de recompra.
- Barras com Gross Revenue por `customer_segment`.
- Colunas com clientes por segmento.
- Histograma ou faixas de `days_since_last_order`.
- Histograma de `total_orders` por cliente.
- Matriz por segmento com clientes, pedidos, receita e recencia.

### Filtros recomendados

- Segmento do cliente.
- Faixa de dias desde a ultima compra.
- Faixa de receita acumulada.
- Faixa de quantidade de pedidos.
- Mes da primeira compra, caso seja criada uma dimensao de coorte.

### Medidas DAX sugeridas

- `[Unique Customers]`
- `[Repeat Customers]`
- `[Repeat Purchase Rate]`
- `[Customer Lifetime Revenue]`
- `[Average Days Since Last Purchase]`
- `[Average Orders per Customer]`

### Insights esperados

- Participacao de compradores recorrentes na base.
- Segmentos que concentram receita.
- Clientes ou grupos com maior recencia de inatividade.
- Distribuicao de frequencia de compra.
- Diferencas entre compradores unicos, recorrentes, de alto valor e inativos.

`fact_customer_retention` representa a janela completa do dataset. Um filtro de data
transacional nao deve ser aplicado automaticamente a essa tabela. Para analise de
coorte, use `first_order_date` com uma relacao ou dimensao especifica.

## Pagina 5 - Sellers & Reviews

### Objetivo da pagina

Comparar desempenho comercial, escala, atrasos e avaliacao dos sellers.

### Tabelas usadas

- `fact_seller_performance`
- `fact_order_items`
- `dim_sellers`

### KPIs principais

- Seller Gross Revenue
- Total Sellers
- Seller Orders
- Seller Late Delivery Rate
- Seller Average Review Score
- Seller Items Sold

### Visuais recomendados

- Tabela ranqueada de sellers com receita, pedidos, atraso e nota media.
- Barras com Gross Revenue por seller.
- Mapa ou barras com Gross Revenue por UF do seller.
- Grafico de dispersao com Seller Late Delivery Rate no eixo X, Seller Average
  Review Score no eixo Y, Gross Revenue no tamanho e Total Orders no tooltip.
- Barras com volume de pedidos por seller.
- Matriz por UF com sellers, receita, pedidos, atraso e avaliacao.

### Filtros recomendados

- Seller.
- UF do seller.
- Faixa de total de pedidos.
- Faixa de Gross Revenue.
- Faixa de Late Delivery Rate.
- Faixa de Average Review Score.

### Medidas DAX sugeridas

- `[Seller Gross Revenue]`
- `[Total Sellers]`
- `[Seller Orders]`
- `[Seller Items Sold]`
- `[Seller Late Deliveries]`
- `[Seller Late Delivery Rate]`
- `[Seller Average Review Score]`

### Insights esperados

- Sellers que concentram receita e pedidos.
- Sellers de alto volume com atraso acima da media.
- Relacao entre atraso e avaliacao.
- UFs com maior concentracao de vendedores e receita.
- Parceiros que combinam escala, baixa taxa de atraso e boa avaliacao.

As reviews pertencem ao pedido, nao individualmente ao seller. A nota media por
seller e uma associacao com os pedidos em que ele participou e deve ser apresentada
com essa limitacao.

## Fora do Escopo

- Margem real nao deve ser calculada porque o dataset Olist nao possui custo do
  produto.
- ROI de campanha nao deve ser calculado porque o dataset nao possui campanhas,
  investimento ou atribuicao.
- Nao criar pagina, filtro ou KPI de campanhas de marketing.
