# Power BI

Este diretorio deve conter a documentacao e os artefatos relacionados ao dashboard.

Arquivos `.pbix` e `.pbit` ficam fora do Git por padrao para evitar versionamento de binarios grandes. Quando necessario, documente aqui as paginas, medidas DAX e fontes usadas no relatorio.

Os arquivos exportados para consumo no Power BI sao gerados em `powerbi/exports/` com:

```bash
python src/transformation/export_powerbi.py
```
