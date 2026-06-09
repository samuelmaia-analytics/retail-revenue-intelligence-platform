# Resumo para Recrutadores

## O que e o projeto

Retail Revenue Intelligence Platform e um projeto de portfolio que simula uma
solucao analitica para e-commerce. Ele organiza um pipeline local de dados, desde a
ingestao dos arquivos ate a criacao de tabelas para analise e consumo no Power BI.

O projeto utiliza o **Brazilian E-Commerce Public Dataset by Olist**, um conjunto
publico de dados anonimizados. Nao foi desenvolvido para uma empresa real e nao
representa uma implementacao em ambiente de producao.

## Problema de negocio

A solucao organiza dados de e-commerce para apoiar perguntas como:

- Como receita e pedidos evoluem ao longo do tempo?
- Quais produtos, categorias, estados e vendedores geram mais receita?
- Onde entregas atrasadas ou cancelamentos afetam a operacao?
- Qual e a relacao entre prazo de entrega e avaliacao do cliente?
- Quantos clientes realizam novas compras?
- Quais segmentos de clientes e vendedores merecem maior atencao?

O resultado e uma camada analitica consistente para acompanhamento comercial,
operacional e de experiencia do cliente.

## Dados utilizados

O dataset publico da Olist inclui:

- pedidos e itens;
- clientes e localizacao;
- produtos e categorias;
- vendedores;
- pagamentos;
- avaliacoes;
- datas estimadas e realizadas de entrega.

Campanhas de marketing nao fazem parte do escopo principal, pois o dataset nao
possui esses dados. O conjunto tambem nao fornece custo dos produtos, portanto o
projeto nao apresenta margem real como metrica oficial.

## Ferramentas

- **Python:** ingestao, orquestracao, exportacao e validacoes.
- **SQL:** limpeza, transformacao, modelagem dimensional e consultas analiticas.
- **DuckDB:** banco analitico local.
- **pytest:** testes automatizados de qualidade de dados.
- **Power BI:** especificacao do dashboard, modelo de dados e medidas DAX.
- **Git e GitHub:** versionamento e organizacao das entregas.
- **Markdown:** documentacao de arquitetura, metricas e regras de negocio.

## Habilidades demonstradas

- Estruturacao de pipeline em camadas `raw`, `staging` e `marts`.
- Modelagem dimensional com dimensoes e tabelas fato.
- Definicao de granularidade, relacionamentos e metricas de negocio.
- Tratamento de dados financeiros, operacionais e de clientes.
- Criacao de consultas para receita, produtos, entregas, retencao e sellers.
- Desenvolvimento de testes de nulidade, unicidade, integridade referencial e
  limites de valores.
- Preparacao de dados e medidas para dashboards no Power BI.
- Documentacao tecnica com premissas e limitacoes do dataset.

## Relevancia para as vagas

Para vagas de **Analista de Dados**, o projeto demonstra capacidade de transformar
dados em metricas, perguntas de negocio e analises acionaveis.

Para vagas de **BI**, demonstra organizacao de um modelo dimensional, preparacao de
fontes para Power BI, definicao de medidas DAX e planejamento de dashboards.

Para vagas de **Analytics Engineering**, demonstra fundamentos de pipelines
reproduziveis, transformacoes SQL em camadas, testes de qualidade, documentacao e
controle de versao.

O projeto foi construido como exercicio pratico de portfolio e evidencia uma base
tecnica aplicada a problemas comuns de dados, sem atribuir resultados a uma
operacao empresarial real ou exagerar o nivel de senioridade envolvido.
