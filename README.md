# ia_tech_challenge_01

Pipeline local para processamento de arquivos do DATASUS no fluxo `DBC -> DBF -> Parquet`, com etapas auxiliares de unificação, redução de colunas e geração de dicionário de dados.

## Escopo

Este diretório contém scripts para:

- converter arquivos `.dbc` em `.dbf`
- converter arquivos `.dbf` em `.parquet` com validação
- unificar vários arquivos `.parquet` em um único arquivo consolidado
- remover colunas de um `.parquet` de forma incremental
- gerar um dicionário de dados a partir de um parquet consolidado
- apoiar a análise exploratória no notebook `trabalho.ipynb`

## Estrutura

- `dbc_to_dbf.py`: conversão em lote de arquivos DBC para DBF
- `dbf_to_parquet.py`: conversão em lote de arquivos DBF para Parquet
- `merge_parquet_files.py`: merge de vários arquivos Parquet
- `remove_parquet_columns.py`: remoção incremental de colunas de um Parquet
- `gerar_dicionario_dados_siasus_pa.py`: geração de dicionário de dados em CSV e Markdown
- `trabalho.ipynb`: notebook de análise

## Requisitos

- Python 3.11 ou superior
- ambiente virtual Python
- `pip`

Dependências principais do projeto:

- `pandas`
- `pyarrow`
- `dbfread`
- `duckdb`
- `matplotlib`
- `scikit-learn`
- `jupyter`

Para a etapa `DBC -> DBF`, o backend preferencial é `datasus-dbc`. Como fallback, o script também tenta usar `blast-dbf` ou `dbc2dbf` se estiverem disponíveis no `PATH`.

## Preparação do ambiente

Criar e ativar ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependências Python:

```bash
pip install pandas pyarrow dbfread duckdb matplotlib scikit-learn jupyter datasus-dbc
```

Verificar se os backends de conversão DBC estão disponíveis:

```bash
python -c "import datasus_dbc; print('datasus-dbc OK')"
which blast-dbf
which dbc2dbf
```

## Dados

As bases utilizadas neste trabalho referem-se a dados do DATASUS de pronto atendimento no estado do Rio de Janeiro durante 2025.

Arquivos originais em formato DBC:

- Primeiro semestre: <https://1drv.ms/u/c/82e7decc796c67f4/IQCY5D37m4UjQKOhAzC1HWQOAa9sQesSOF7ZM0BD57WUdhk?e=Tw1Ib4>
- Segundo semestre: <https://1drv.ms/u/c/82e7decc796c67f4/IQA4o-vCVVSRQoyicfgTubW5Adu19cQHQrAluSXVfpURer4?e=0NumT8>

Arquivos finais disponibilizados:

- Junho de 2025: <https://1drv.ms/u/c/82e7decc796c67f4/IQAJ6h9k__uPS6ATF-pJQJAtAb2Qhna2Y2WssjRIHhDhvOw?e=QL9dS2>
- Versão final consolidada: <https://drive.google.com/file/d/1w0wjsd0pOowVwLDOpOvJjKOAOsuXsJpB/view?usp=sharing>

## Fluxo recomendado

1. Converter os arquivos `.dbc` para `.dbf`
2. Converter os `.dbf` para `.parquet`
3. Unificar os parquets gerados
4. Analisar os dados no notebook

## Scripts

### `dbc_to_dbf.py`

Converte todos os arquivos `.dbc` de uma pasta para `.dbf`.

Entrada:

- pasta com arquivos `.dbc`

Saída:

- arquivos `.dbf` na pasta de destino
- log `conversao_dbc_dbf.log`

Exemplo:

```bash
python3 dbc_to_dbf.py \
  --pasta-origem /caminho/dbc_origem \
  --pasta-destino /caminho/dbf_destino
```

Comportamento relevante:

- prioriza o backend Python `datasus-dbc`
- usa `blast-dbf` como fallback
- usa `dbc2dbf` como segundo fallback
- registra sucesso e erro por arquivo no log

### `dbf_to_parquet.py`

Converte todos os arquivos `.dbf` de uma pasta para `.parquet`, em lotes, com validação do resultado.

Entrada:

- pasta com arquivos `.dbf`

Saída:

- um arquivo `.parquet` por `.dbf`
- log `conversao_dbf_parquet.log`
- relatório HTML `relatorio_validacao.html`

Exemplo:

```bash
python3 dbf_to_parquet.py \
  --pasta-entrada-dbf /caminho/entrada_dbf \
  --pasta-saida-parquet /caminho/saida_parquet
```

Validações executadas:

- leitura do DBF
- geração do Parquet
- comparação de quantidade de colunas
- comparação de quantidade de registros
- comparação dos 10 primeiros registros

### `merge_parquet_files.py`

Unifica todos os arquivos `.parquet` de uma pasta em um único arquivo, preservando colunas por nome com `union_by_name=true`.

Entrada:

- pasta com arquivos `.parquet`

Saída:

- arquivo consolidado `parquet_unificado.parquet`
- log `merge_parquet.log`
- relatório HTML `relatorio_validacao_merge.html`

Exemplo:

```bash
python3 merge_parquet_files.py \
  --pasta-origem /caminho/parquets \
  --pasta-destino /caminho/saida_merge
```

Observação:

- o nome do arquivo gerado por este script é `parquet_unificado.parquet`

### `remove_parquet_columns.py`

Remove colunas de um arquivo Parquet usando leitura e escrita incrementais, reduzindo uso de memória.

Entrada:

- arquivo `.parquet`
- lista de colunas a remover via CLI ou arquivo texto

Saída:

- novo arquivo `.parquet`
- arquivo de log com o mesmo nome base do arquivo de saída e extensão `.log`

Exemplo com colunas explicitadas:

```bash
python3 remove_parquet_columns.py \
  --arquivo-entrada /caminho/arquivo.parquet \
  --arquivo-saida /caminho/arquivo_reduzido.parquet \
  --coluna-remover CPF_PAC \
  --coluna-remover CNS_PAC
```

Exemplo com arquivo de colunas:

```bash
python3 remove_parquet_columns.py \
  --arquivo-entrada /caminho/arquivo.parquet \
  --arquivo-saida /caminho/arquivo_reduzido.parquet \
  --arquivo-colunas /caminho/colunas_remover.txt
```

Opções adicionais:

- `--batch-size`: quantidade de linhas por lote
- `--compression`: codec de compressão do parquet de saída, como `snappy`, `zstd` ou `gzip`

### `gerar_dicionario_dados_siasus_pa.py`

Gera um dicionário de dados em CSV e Markdown a partir de um parquet consolidado.

Comportamento atual do script:

- lê o arquivo fixo `/workspace/trabalho/parquet/merged.parquet`
- gera `/workspace/trabalho/dicionario_dados_merged.csv`
- gera `/workspace/trabalho/dicionario_dados_merged.md`

Execução:

```bash
python3 gerar_dicionario_dados_siasus_pa.py
```

Observação importante:

- este script usa caminhos fixos
- o parquet esperado por ele se chama `merged.parquet`
- isso não coincide com a saída padrão de `merge_parquet_files.py`, que gera `parquet_unificado.parquet`
- se necessário, ajuste o script ou renomeie/copiei o arquivo consolidado antes da execução

### `trabalho.ipynb`

Notebook para exploração, tratamento inicial dos dados, visualização e experimentos de machine learning.

Para abrir:

```bash
jupyter lab
```

ou

```bash
jupyter notebook
```

## Exemplo de pipeline completo

```bash
python3 dbc_to_dbf.py \
  --pasta-origem /dados/dbc \
  --pasta-destino /dados/dbf

python3 dbf_to_parquet.py \
  --pasta-entrada-dbf /dados/dbf \
  --pasta-saida-parquet /dados/parquet

python3 merge_parquet_files.py \
  --pasta-origem /dados/parquet \
  --pasta-destino /dados/merge

python3 remove_parquet_columns.py \
  --arquivo-entrada /dados/merge/parquet_unificado.parquet \
  --arquivo-saida /dados/merge/parquet_unificado_reduzido.parquet \
  --coluna-remover CPF_PAC \
  --coluna-remover CNS_PAC
```

## Observações

- os scripts foram escritos para uso local e processamento em lote
- os logs e relatórios HTML ajudam a validar a integridade das conversões
- a geração do dicionário de dados depende de um nome e caminho específicos no estado atual do script
