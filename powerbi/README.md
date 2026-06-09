# Power BI

Este diretorio contem a documentacao e os arquivos locais usados pelo dashboard.

Arquivos `.pbix`, `.pbit` e CSVs exportados ficam fora do Git para evitar o
versionamento de artefatos grandes ou gerados.

## Gerar os CSVs

Execute primeiro as camadas de ingestao, staging e marts. Depois, gere os arquivos:

```bash
python src/transformation/export_powerbi_tables.py
```

O script cria `powerbi/export/` automaticamente e exporta as quatro dimensoes e os
sete fatos principais do schema `marts`. Cada CSV usa cabecalho, delimitador por
virgula e encoding UTF-8. A execucao informa a quantidade de linhas exportadas por
tabela.

Tabelas de campanhas nao sao exportadas porque campanhas de marketing nao fazem
parte do dataset Olist nem do modelo principal.

## Importar no Power BI Desktop

1. Abra o Power BI Desktop.
2. Selecione **Obter dados > Texto/CSV**.
3. Escolha um arquivo em `powerbi/export/`.
4. Confirme **Origem do arquivo: 65001 (Unicode UTF-8)** e delimitador por virgula.
5. Selecione **Transformar dados** para revisar tipos de datas, numeros e textos.
6. Repita o processo para os demais CSVs e aplique as alteracoes.

## Relacionamentos Recomendados

- `dim_customers[customer_id]` com `fact_orders[customer_id]` e
  `fact_order_items[customer_id]`.
- `dim_products[product_id]` com `fact_order_items[product_id]`.
- `dim_sellers[seller_id]` com `fact_order_items[seller_id]` e
  `fact_seller_performance[seller_id]`.
- `dim_dates[full_date]` com as colunas de data usadas em cada fato.
- `fact_orders[order_id]` com `fact_order_items[order_id]`,
  `fact_payments[order_id]` e `fact_reviews[order_id]`.

Evite relacionamentos muitos-para-muitos entre fatos. Para indicadores globais de
pedidos, use `fact_orders`; para produto, categoria e seller, use
`fact_order_items`.
