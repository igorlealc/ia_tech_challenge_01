# Scripts Auxiliares do Pipeline DATASUS

Este documento descreve os scripts auxiliares presentes nesta pasta para processamento local de arquivos DATASUS no fluxo `DBC -> DBF -> Parquet`, com validação, consolidação e redução de colunas.

## Escopo

Os scripts documentados aqui são:

| Script | Finalidade |
|---|---|
| `dbc_to_dbf.py` | Converter arquivos `.dbc` em `.dbf`. |
| `dbf_to_parquet.py` | Converter arquivos `.dbf` em `.parquet` com validação. |
| `merge_parquet_files.py` | Unificar vários arquivos `.parquet` em um único Parquet consolidado. |
| `remove_parquet_columns.py` | Remover colunas de um arquivo Parquet de forma incremental. |

## Requisitos

- Python 3.11 ou superior.
- Ambiente virtual Python.
- `pip`.

Dependências usadas pelos scripts:

- `datasus-dbc`
- `dbfread`
- `duckdb`
- `pandas`
- `pyarrow`

Instalação sugerida:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install datasus-dbc dbfread duckdb pandas pyarrow
```

Para a conversão `DBC -> DBF`, o script `dbc_to_dbf.py` tenta usar, nesta ordem:

1. pacote Python `datasus-dbc`;
2. executável `blast-dbf`, se estiver disponível no `PATH`;
3. executável `dbc2dbf`, se estiver disponível no `PATH`.

## Fluxo recomendado dos scripts

```text
arquivos .dbc
    |
    v
dbc_to_dbf.py
    |
    v
arquivos .dbf
    |
    v
dbf_to_parquet.py
    |
    v
arquivos .parquet mensais ou por lote
    |
    v
merge_parquet_files.py
    |
    v
parquet_unificado.parquet
    |
    v
remove_parquet_columns.py
    |
    v
parquet reduzido
```

## `dbc_to_dbf.py`

Converte arquivos DATASUS no formato `.dbc` para `.dbf`.

### Entrada

- Pasta de origem contendo arquivos `.dbc` ou `.DBC`.
- Pasta de destino onde os arquivos `.dbf` serão gravados.

### Saída

- Um arquivo `.dbf` para cada arquivo `.dbc` convertido.
- Log de execução: `conversao_dbc_dbf.log`, gravado na pasta de destino.

### Uso

```bash
python3 dbc_to_dbf.py \
  --pasta-origem /caminho/dbc_origem \
  --pasta-destino /caminho/dbf_destino
```

### Comportamento relevante

- Cria a pasta de destino, se ela não existir.
- Localiza arquivos com extensão `.dbc` e `.DBC`.
- Registra sucesso ou erro por arquivo no log.
- Interrompe com erro se nenhum backend de conversão estiver disponível.

## `dbf_to_parquet.py`

Converte arquivos `.dbf` para `.parquet` em lote, com validação de integridade.

### Entrada

- Pasta contendo arquivos `.dbf`.
- Pasta de saída para os arquivos `.parquet`.

### Saída

- Um arquivo `.parquet` para cada `.dbf` processado.
- Log de execução: `conversao_dbf_parquet.log`.
- Relatório HTML de validação: `relatorio_validacao.html`.

### Uso

```bash
python3 dbf_to_parquet.py \
  --pasta-entrada-dbf /caminho/dbf_origem \
  --pasta-saida-parquet /caminho/parquet_saida
```

### Validações executadas

- Localização do arquivo DBF.
- Leitura do DBF.
- Gravação do Parquet.
- Comparação da quantidade de colunas.
- Comparação da quantidade de registros.
- Comparação dos 10 primeiros registros.
- Marcação final de conversão íntegra.

### Comportamento relevante

- Lê os DBFs em lotes internos de 50.000 registros.
- Testa os encodings `latin1`, `cp1252` e `utf-8`.
- Grava Parquet com compressão `snappy`.
- Converte colunas de texto para o tipo `string` antes da gravação.

## `merge_parquet_files.py`

Unifica arquivos `.parquet` de uma pasta em um único arquivo consolidado.

### Entrada

- Pasta de origem contendo arquivos `.parquet`.
- Pasta de destino para o Parquet consolidado.

### Saída

- Arquivo consolidado: `parquet_unificado.parquet`.
- Log de execução: `merge_parquet.log`.
- Relatório HTML de validação: `relatorio_validacao_merge.html`.

### Uso

```bash
python3 merge_parquet_files.py \
  --pasta-origem /caminho/parquets \
  --pasta-destino /caminho/merge_saida
```

### Validações executadas

- Validação da pasta de origem.
- Criação ou validação da pasta de destino.
- Localização dos arquivos `.parquet`.
- Leitura de metadados dos arquivos de origem.
- Geração do arquivo final.
- Conferência da união das colunas.
- Conferência da soma total de registros.
- Marcação final de integridade.

### Comportamento relevante

- Usa DuckDB para executar o merge.
- Lê os arquivos com `union_by_name=true`, preservando colunas por nome quando houver diferenças de schema.
- Grava o arquivo final com compressão `snappy`.

## `remove_parquet_columns.py`

Remove colunas de um arquivo Parquet e grava uma nova versão reduzida.

### Entrada

- Arquivo Parquet de entrada.
- Arquivo Parquet de saída.
- Lista de colunas a remover, informada pela linha de comando ou por arquivo texto.

### Saída

- Arquivo Parquet reduzido.
- Log de execução com o mesmo nome base do arquivo de saída e extensão `.log`.

### Uso com colunas informadas diretamente

```bash
python3 remove_parquet_columns.py \
  --arquivo-entrada /caminho/entrada.parquet \
  --arquivo-saida /caminho/saida_reduzida.parquet \
  --coluna-remover CPF_PAC \
  --coluna-remover CNS_PAC
```

### Uso com arquivo de colunas

```bash
python3 remove_parquet_columns.py \
  --arquivo-entrada /caminho/entrada.parquet \
  --arquivo-saida /caminho/saida_reduzida.parquet \
  --arquivo-colunas /caminho/colunas_remover.txt
```

O arquivo informado em `--arquivo-colunas` deve conter uma coluna por linha.

### Opções adicionais

```bash
--batch-size 100000
--compression snappy
```

- `--batch-size`: quantidade de linhas por lote na escrita incremental. Valor padrão: `100000`.
- `--compression`: codec de compressão do Parquet de saída. Valor padrão: `snappy`.

### Comportamento relevante

- Valida se o arquivo de entrada existe e possui extensão `.parquet`.
- Exige pelo menos uma coluna para remoção.
- Interrompe com erro se alguma coluna informada não existir no arquivo de entrada.
- Impede a remoção de todas as colunas do arquivo.
- Processa os dados de forma incremental com `pyarrow.dataset`.

## Exemplo de execução completa

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

## Arquivos de log e relatórios

| Script | Log | Relatório |
|---|---|---|
| `dbc_to_dbf.py` | `conversao_dbc_dbf.log` | Não gera HTML. |
| `dbf_to_parquet.py` | `conversao_dbf_parquet.log` | `relatorio_validacao.html` |
| `merge_parquet_files.py` | `merge_parquet.log` | `relatorio_validacao_merge.html` |
| `remove_parquet_columns.py` | Mesmo nome do arquivo de saída com extensão `.log` | Não gera HTML. |

## Observações finais

- Os scripts foram escritos para processamento local e em lote.
- Os caminhos usados nos exemplos são ilustrativos.
- Os scripts de conversão e merge criam as pastas de destino quando necessário.
