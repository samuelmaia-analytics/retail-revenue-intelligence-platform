# Perguntas de Negocio

## Visao Geral

As queries em `sql/analysis/` traduzem o modelo dimensional Olist em perguntas
praticas para gestao, operacoes e construcao de dashboards. Todas consultam apenas a
camada `marts` e respeitam a granularidade de pedidos, itens, pagamentos, clientes e
vendedores.

Campanhas de marketing nao fazem parte deste catalogo porque o dataset Olist nao
possui dados de campanha, investimento ou atribuicao.

## Catalogo

### Visao executiva

- **Pergunta de negocio:** quais sao os principais indicadores comerciais,
  operacionais, de satisfacao e retencao no periodo analisado?
- **Query relacionada:** `sql/analysis/executive_summary.sql`
- **Decisao apoiada:** acompanhar a saude geral da operacao e priorizar os temas que
  exigem investigacao detalhada.

### Evolucao mensal da receita

- **Pergunta de negocio:** como receita, pedidos e ticket medio evoluem a cada mes?
- **Query relacionada:** `sql/analysis/revenue_by_month.sql`
- **Decisao apoiada:** identificar crescimento, contracao e sazonalidade para
  planejamento comercial.

### Receita por estado

- **Pergunta de negocio:** quais UFs de clientes concentram receita e quais
  apresentam maior cancelamento ou atraso?
- **Query relacionada:** `sql/analysis/revenue_by_state.sql`
- **Decisao apoiada:** priorizar regioes para capacidade operacional, atendimento e
  expansao.

### Receita por categoria

- **Pergunta de negocio:** quais categorias geram mais receita, itens e pedidos?
- **Query relacionada:** `sql/analysis/revenue_by_category.sql`
- **Decisao apoiada:** orientar gestao de portfolio, sortimento e destaque de
  categorias.

### Meios de pagamento

- **Pergunta de negocio:** como o valor pago e os pedidos se distribuem entre os
  meios de pagamento?
- **Query relacionada:** `sql/analysis/payment_method_analysis.sql`
- **Decisao apoiada:** avaliar relevancia das modalidades e necessidades de
  integracao ou conciliacao financeira.

### Parcelamento

- **Pergunta de negocio:** quais quantidades de parcelas sao mais utilizadas e
  quanto valor financeiro representam?
- **Query relacionada:** `sql/analysis/installments_analysis.sql`
- **Decisao apoiada:** apoiar politicas de parcelamento e analise de comportamento
  de pagamento.

### Impacto do atraso

- **Pergunta de negocio:** pedidos atrasados recebem notas menores ou apresentam
  maior tempo de entrega?
- **Query relacionada:** `sql/analysis/late_delivery_impact.sql`
- **Decisao apoiada:** quantificar o impacto da logistica na experiencia do cliente
  e priorizar melhorias de SLA.

### Distribuicao das avaliacoes

- **Pergunta de negocio:** como as notas se distribuem e qual sua relacao com
  comentarios e atrasos?
- **Query relacionada:** `sql/analysis/review_score_analysis.sql`
- **Decisao apoiada:** monitorar satisfacao e identificar fatores associados a
  avaliacoes negativas.

### Segmentos de retencao

- **Pergunta de negocio:** qual e o tamanho, valor e recencia dos segmentos de
  clientes?
- **Query relacionada:** `sql/analysis/customer_retention_segments.sql`
- **Decisao apoiada:** definir estrategias diferenciadas para compradores unicos,
  recorrentes, de alto valor e inativos.

### Taxa de recompra

- **Pergunta de negocio:** como a taxa de recompra varia entre coortes de primeira
  compra?
- **Query relacionada:** `sql/analysis/repeat_purchase_rate.sql`
- **Decisao apoiada:** comparar a qualidade das coortes e acompanhar a evolucao da
  retencao, considerando a janela limitada do dataset.

### Produtos lideres

- **Pergunta de negocio:** quais produtos individuais geram mais receita e volume?
- **Query relacionada:** `sql/analysis/top_products_by_revenue.sql`
- **Decisao apoiada:** priorizar produtos para disponibilidade, acompanhamento e
  gestao de catalogo.

### Vendedores lideres

- **Pergunta de negocio:** quais sellers lideram receita e como seu desempenho
  operacional se compara?
- **Query relacionada:** `sql/analysis/top_sellers_by_revenue.sql`
- **Decisao apoiada:** identificar parceiros estrategicos e sellers que combinam
  escala com boa experiencia.

### Atraso por vendedor

- **Pergunta de negocio:** quais sellers apresentam maior taxa de atraso entre
  aqueles com volume minimo relevante?
- **Query relacionada:** `sql/analysis/seller_late_delivery_rate.sql`
- **Decisao apoiada:** direcionar planos de melhoria e acompanhamento de sellers.

### Pedidos cancelados

- **Pergunta de negocio:** em quais meses e UFs os cancelamentos se concentram e
  qual valor esta associado a eles?
- **Query relacionada:** `sql/analysis/cancelled_orders_analysis.sql`
- **Decisao apoiada:** investigar causas operacionais e priorizar regioes ou
  periodos com maior incidencia.

### Impacto do frete

- **Pergunta de negocio:** quais categorias possuem maior peso de frete em relacao
  ao valor das mercadorias?
- **Query relacionada:** `sql/analysis/freight_impact_analysis.sql`
- **Decisao apoiada:** orientar revisoes logisticas, de embalagem e de politica de
  frete.
