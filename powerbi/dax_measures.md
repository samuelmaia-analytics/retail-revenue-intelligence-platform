# Medidas DAX

## Configuracao

As medidas abaixo assumem que os CSVs de `powerbi/export/` foram importados com os
mesmos nomes das tabelas `marts`. Recomenda-se criar uma tabela vazia chamada
`_Measures` para centralizar as medidas no modelo.

As expressoes usam virgula como separador. Em instalacoes do Power BI configuradas
para usar ponto e virgula, substitua os separadores conforme a configuracao regional.

## Medidas Oficiais

### Gross Revenue

Usa o fato de itens para responder corretamente a filtros de produto, categoria,
seller, data e cliente.

```DAX
Gross Revenue =
SUM ( fact_order_items[item_price] )
```

Formato: moeda BRL.

### Freight Value

```DAX
Freight Value =
SUM ( fact_order_items[freight_value] )
```

Formato: moeda BRL.

### Total Payment Value

Usa a coluna consolidada no nivel de pedido para responder aos filtros de data e
cliente sem multiplicar pagamentos.

```DAX
Total Payment Value =
SUM ( fact_orders[total_payment_value] )
```

Para analise por `payment_type`, crie uma medida separada sobre
`fact_payments[payment_value]`.

### Total Orders

```DAX
Total Orders =
DISTINCTCOUNT ( fact_orders[order_id] )
```

Formato: numero inteiro.

### Delivered Orders

```DAX
Delivered Orders =
CALCULATE (
    [Total Orders],
    fact_orders[is_delivered] = TRUE ()
)
```

### Cancelled Orders

```DAX
Cancelled Orders =
CALCULATE (
    [Total Orders],
    fact_orders[is_cancelled] = TRUE ()
)
```

### Cancellation Rate

```DAX
Cancellation Rate =
DIVIDE ( [Cancelled Orders], [Total Orders] )
```

Formato: percentual.

### Average Order Value

```DAX
Average Order Value =
DIVIDE (
    SUM ( fact_orders[gross_revenue] ),
    [Total Orders]
)
```

Formato: moeda BRL.

Use `[Category Average Order Value]` para visuais filtrados por produto ou categoria.

### Late Delivery Rate

```DAX
Late Orders =
CALCULATE (
    [Total Orders],
    fact_orders[is_late_delivery] = TRUE ()
)
```

```DAX
Late Delivery Rate =
DIVIDE ( [Late Orders], [Delivered Orders] )
```

Formato: percentual.

### Average Delivery Days

```DAX
Average Delivery Days =
CALCULATE (
    AVERAGE ( fact_orders[delivery_days] ),
    fact_orders[is_delivered] = TRUE (),
    fact_orders[delivery_days] <> BLANK ()
)
```

Formato: numero decimal.

### Average Review Score

```DAX
Average Review Score =
AVERAGE ( fact_reviews[review_score] )
```

Formato: numero decimal com duas casas.

### Review Comment Rate

```DAX
Reviews with Comment =
CALCULATE (
    DISTINCTCOUNT ( fact_reviews[review_id] ),
    fact_reviews[has_review_comment] = TRUE ()
)
```

```DAX
Total Reviews =
DISTINCTCOUNT ( fact_reviews[review_id] )
```

```DAX
Review Comment Rate =
DIVIDE ( [Reviews with Comment], [Total Reviews] )
```

Formato: percentual.

### Repeat Customers

Retencao deve usar `customer_unique_id`, nunca `customer_id`.

```DAX
Repeat Customers =
CALCULATE (
    DISTINCTCOUNT ( fact_customer_retention[customer_unique_id] ),
    fact_customer_retention[total_orders] >= 2
)
```

### Repeat Purchase Rate

```DAX
Unique Customers =
DISTINCTCOUNT ( fact_customer_retention[customer_unique_id] )
```

```DAX
Repeat Purchase Rate =
DIVIDE ( [Repeat Customers], [Unique Customers] )
```

Formato: percentual.

### Total Sellers

```DAX
Total Sellers =
DISTINCTCOUNT ( dim_sellers[seller_id] )
```

### Average Installments

```DAX
Average Installments =
AVERAGE ( fact_payments[payment_installments] )
```

Formato: numero decimal.

## Medidas Auxiliares

Estas medidas complementam os visuais especificados para as cinco paginas.

### Items Sold

```DAX
Items Sold =
COUNTROWS ( fact_order_items )
```

### Item Fact Orders

```DAX
Item Fact Orders =
DISTINCTCOUNT ( fact_order_items[order_id] )
```

### Category Average Order Value

```DAX
Category Average Order Value =
DIVIDE ( [Gross Revenue], [Item Fact Orders] )
```

### Average Item Price

```DAX
Average Item Price =
AVERAGE ( fact_order_items[item_price] )
```

### Freight to Revenue Rate

```DAX
Freight to Revenue Rate =
DIVIDE ( [Freight Value], [Gross Revenue] )
```

### Average Freight per Order

```DAX
Average Freight per Order =
DIVIDE (
    SUM ( fact_orders[freight_value] ),
    [Total Orders]
)
```

### Customer Lifetime Revenue

Representa apenas a receita observada dentro da janela do dataset.

```DAX
Customer Lifetime Revenue =
SUM ( fact_customer_retention[gross_revenue] )
```

### Average Days Since Last Purchase

```DAX
Average Days Since Last Purchase =
AVERAGE ( fact_customer_retention[days_since_last_order] )
```

### Average Orders per Customer

```DAX
Average Orders per Customer =
AVERAGE ( fact_customer_retention[total_orders] )
```

### Seller Gross Revenue

```DAX
Seller Gross Revenue =
SUM ( fact_seller_performance[gross_revenue] )
```

### Seller Orders

```DAX
Seller Orders =
SUM ( fact_seller_performance[total_orders] )
```

Essa medida soma pedidos associados a sellers. Um pedido com mais de um seller pode
ser contado mais de uma vez no total agregado. Para pedidos globais, use
`[Total Orders]`.

### Seller Items Sold

```DAX
Seller Items Sold =
SUM ( fact_seller_performance[total_items] )
```

### Seller Late Deliveries

```DAX
Seller Late Deliveries =
SUM ( fact_seller_performance[late_deliveries] )
```

### Seller Late Delivery Rate

Usa media ponderada por pedidos, evitando a media simples das taxas dos sellers.

```DAX
Seller Late Delivery Rate =
DIVIDE ( [Seller Late Deliveries], [Seller Orders] )
```

### Seller Average Review Score

```DAX
Seller Average Review Score =
AVERAGEX (
    fact_seller_performance,
    fact_seller_performance[average_review_score]
)
```

A avaliacao pertence ao pedido e e associada aos sellers participantes; nao e uma
avaliacao individual do seller.

## Observacoes de Escopo

- Nao calcular margem real. O dataset Olist nao possui custo do produto, portanto
  margem bruta, margem liquida e rentabilidade exigiriam uma simulacao ou fonte
  externa claramente documentada.
- Nao calcular ROI de campanha. O dataset Olist nao possui campanhas, investimento
  em midia ou atribuicao.
- `payment_value` pode ter varios registros por pedido. Nao conte linhas de
  `fact_payments` como pedidos.
- Medidas de retencao usam `customer_unique_id`.
- Evite somar taxas e medias materializadas; recalcule-as a partir de numeradores e
  denominadores no contexto do visual.
