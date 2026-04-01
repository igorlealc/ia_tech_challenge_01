# README

## Pré-requisitos

Para executar os scripts e o notebook, é recomendado usar:

- Python 3.11 ou superior
- ambiente virtual Python
- Jupyter Notebook ou JupyterLab para abrir o arquivo `.ipynb`

Criar e ativar ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar bibliotecas usadas no projeto:

```bash
pip install pandas pyarrow dbfread duckdb matplotlib scikit-learn jupyter
```

Bibliotecas identificadas nos arquivos:

- `pandas`
- `pyarrow`
- `dbfread`
- `duckdb`
- `matplotlib`
- `scikit-learn`
- `jupyter` para executar o notebook

## Bases de dados

As bases deste trabalho referem-se aos dados do DATASUS de pronto atendimentos realizados no estado do Rio de Janeiro em junho de 2025.

Arquivos originais em formato DBC:

- `PARJ2506A`: <https://1drv.ms/u/c/82e7decc796c67f4/IQB1czQjsw1aSoibWrbeKlnKAWbz00z8jFiJjElQTJzVHX4?e=sBgOse>
- `PARJ2506B`: <https://1drv.ms/u/c/82e7decc796c67f4/IQB2gUSRh1E3ToU0BpbBEV3AAVyPM1YPh-Wgt-f825MPrj8?e=NCbKHu>

Arquivo final consolidado em Parquet:

- `parquet final`: <https://1drv.ms/u/c/82e7decc796c67f4/IQAJ6h9k__uPS6ATF-pJQJAtAb2Qhna2Y2WssjRIHhDhvOw?e=QL9dS2>

## Arquivos

### `dbf_to_parquet.py`

Converte arquivos `.dbf` para `.parquet`, processa em lotes, valida o resultado e gera log/relatório.

Exemplo:

```bash
python3 dbf_to_parquet.py \
  --pasta-entrada-dbf /caminho/entrada \
  --pasta-saida-parquet /caminho/saida
```

### `merge_parquet_files.py`

Une vários arquivos `.parquet` em um único arquivo consolidado e valida colunas e quantidade de registros.

Exemplo:

```bash
python3 merge_parquet_files.py \
  --pasta-origem /caminho/origem \
  --pasta-destino /caminho/destino
```

### `gerar_dicionario_dados_siasus_pa.py`

Lê um arquivo Parquet consolidado e gera um dicionário de dados em CSV e Markdown com descrição das colunas.

### `trabalho.ipynb`

Notebook para análise de dados, inspeção de colunas, tratamento simples, visualização com gráficos e um exemplo de machine learning com `scikit-learn`.
# ia_tech_challenge_01
