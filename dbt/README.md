# dbt Project

Este diretorio concentra a modelagem analitica em SQL/dbt.

## Camadas

- `models/staging`: padronizacao tecnica das fontes.
- `models/intermediate`: regras de negocio reutilizaveis.
- `models/marts`: tabelas finais para consumo analitico e Power BI.

## Perfil Local

O `profiles.yml` nao deve ser versionado. Para desenvolvimento local com DuckDB, use um perfil semelhante a:

```yaml
retail_revenue_intelligence:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/processed/retail.duckdb
      threads: 4
```
