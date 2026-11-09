# SalesInsight PY

## Sobre o projeto
Análise e visualização de dados de vendas desenvolvida em Python. O projeto carrega, limpa, transforma, agrega e visualiza um dataset de vendas, gerando métricas por período, produto, categoria e região, além de uma segmentação simples de clientes por faixa de gasto.

**Autor:** Josivaldo Luis Coelho

## O que o projeto analisa
- Receita total e volume de vendas por mês e por trimestre
- Top produtos e categorias por receita
- Desempenho por região
- Segmentação de clientes por nível de gasto (Bronze, Prata, Ouro)
- Relação entre quantidade vendida e receita por transação
- Exportação de relatórios em CSV e JSON e de gráficos em PNG

## Conceitos aplicados (Módulo 01 - Semanas 01 a 08)
- **Lógica de programação:** variáveis, tipos, operadores, condicionais
- **Estruturas de dados:** listas, tuplas, dicionários e compostas
- **Funções:** parâmetros, retorno, lambda, ordem superior
- **Leitura e escrita:** arquivos CSV e JSON
- **Módulo datetime:** conversão de tipos (cast)
- **Pandas:** DataFrames, filtros, groupby, transformações vetorizadas
- **Matplotlib e Seaborn:** linha, barra, dispersão, subplots, exportação
- **Git e GitHub:** branches, commits e GitFlow simplificado

## Como executar

### Google Colab (Recomendado para otimização de memória)
1. Faça upload do arquivo `salesinsight.py` para o Colab.
2. Execute em uma célula: `!python salesinsight.py`
3. Ou copie o conteúdo diretamente para a célula do notebook e execute.

### Localmente com VS Code
1. Instale o Python 3.10+ e as dependências:
   ```bash
   pip install pandas numpy matplotlib seaborn
   ```
2. Execute no terminal:
   ```bash
   python salesinsight.py
   ```

## Estrutura do projeto
```text
salesinsight-py/
|-- salesinsight.py          # fluxo principal
|-- vendas.csv               # dataset (gerado pelo próprio script)
|-- README.md                # documentação
|-- outputs/
    |-- metricas_por_mes.csv
    |-- segmentacao_clientes.csv
    |-- estatisticas_gerais.json
    |-- graficos/
        |-- receita_por_mes.png
        |-- top_produtos.png
        |-- quantidade_vs_receita.png
        |-- painel_resumo.png
```

## Decisões técnicas
- **Tratamento de Datas:** Optou-se por aplicar `errors='coerce'` no parseamento de datas e remover (drop) os registros inválidos usando `dropna()`, garantindo precisão em vez de mascarar os dados preenchendo as falhas com médias.
- **Encapsulamento POO:** A transformação de dados foi consolidada dentro de uma classe `AnalisadorDeVendas` para facilitar o gerenciamento de estado entre o dataframe bruto e o dataframe limpo.

## Ferramentas utilizadas
- **Linguagem:** Python 3.10+
- **Ambiente:** Google Colab / VS Code
- **Bibliotecas:** pandas, numpy, matplotlib, seaborn, json, datetime, os, random
