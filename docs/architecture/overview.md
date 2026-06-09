# Architecture Overview

## Objetivo

Organizar um pipeline analitico local para transformar o dataset Olist em modelos confiaveis para analise e Power BI.

## Fluxo

```text
data/raw -> Python ingestion -> DuckDB raw -> SQL staging -> SQL marts -> Power BI exports
```

## Principios

- Execucao local e reproduzivel.
- Sem credenciais ou servicos pagos.
- Separacao clara entre dados brutos, modelos intermediarios e tabelas finais.
- Definicoes de metricas documentadas antes do consumo em dashboard.
- Campanhas de marketing ficam fora do escopo principal porque o dataset Olist nao possui essa entidade.
