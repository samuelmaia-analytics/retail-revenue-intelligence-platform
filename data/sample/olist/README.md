# Olist Sample

Este diretorio contem uma amostra referencialmente consistente do Brazilian
E-Commerce Public Dataset by Olist para execucao local e no GitHub Actions.

A amostra possui aproximadamente 1.000 pedidos e somente os clientes, itens, pagamentos, reviews,
produtos, sellers, categorias e registros geograficos relacionados. Ela preserva os
nomes e schemas dos CSVs originais, mas nao substitui o dataset completo em analises
locais.

Para regenerar a amostra a partir dos CSVs completos:

```bash
python src/ingestion/generate_olist_sample.py --orders 1000
```

Campanhas de marketing nao fazem parte da amostra nem do pipeline principal.
