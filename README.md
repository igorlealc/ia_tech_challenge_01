# README do Trabalho - Pós-Graduação FIAP IA para Devs

## Visão geral

Este projeto utiliza dados públicos do DATASUS, especificamente a base **SIH/SUS RD - AIH Reduzida** do estado do Rio de Janeiro no ano de 2025.

O objetivo do trabalho é construir um fluxo completo de ciência de dados, desde a preparação da base até análises supervisionadas e não supervisionadas.

## Dados

As bases utilizadas referem-se a dados do DATASUS de pronto atendimento no estado do Rio de Janeiro durante 2025.

Arquivos originais em formato DBC:

- Ano 2025 dividido por mês: <https://1drv.ms/u/c/82e7decc796c67f4/IQCY5D37m4UjQKOhAzC1HWQOAa9sQesSOF7ZM0BD57WUdhk?e=Tw1Ib4>

Arquivo consolidado disponibilizado:

- Versão consolidada em Parquet: <https://1drv.ms/u/c/82e7decc796c67f4/IQAzoDEOMdnWQIdJivtSpFz_AanG6z7Cq5c6qFcp1soRwDM?e=hLqcXC>

## Estrutura do repositório

| Caminho | Finalidade |
|---|---|
| `trabalho_parte_1.ipynb` | Redução inicial da base consolidada. |
| `trabalho_parte_2.ipynb` | Tratamento da base e criação de variáveis derivadas. |
| `trabalho_parte_3.ipynb` | Classificação supervisionada com SVM e Random Forest. |
| `trabalho_parte_4.ipynb` | Classificação supervisionada para indícios de câncer de mama. |
| `analise_complementar_1.ipynb` | Regressão para previsão de `VAL_TOT`. |
| `analise_complementar_2.ipynb` | Agrupamentos relacionados ao câncer de mama. |
| `dbc_to_dbf.py` | Conversão de `.dbc` para `.dbf`. |
| `dbf_to_parquet.py` | Conversão de `.dbf` para `.parquet`. |
| `merge_parquet_files.py` | Consolidação de múltiplos arquivos Parquet. |
| `remove_parquet_columns.py` | Remoção incremental de colunas em Parquet. |
| `README_SCRIPTS_AUXILIARES.md` | Uso detalhado dos scripts auxiliares. |
| `material_aulas/` | PDFs das aulas usados como referência conceitual. |
| `PROMPT_PADRAO_PROJETO.md` | Prompt-base para manter o padrão técnico e narrativo do projeto inteiro. |

## Material de aula

Os PDFs de apoio da pós foram organizados em `material_aulas/`.

Os tópicos mais diretamente usados nas Partes 3 e 4 foram:

- **Aula 1 - Modelos de Classificação**: definição de problema supervisionado, target e separação treino/teste.
- **Aula 2 - KNN, SVM**: uso de `KNN` e ajuste de `k`.
- **Aula 4 - Modelos Baseados em Árvores**: `DecisionTree` e `RandomForest`.
- **Aula 5 - Validação Cruzada e Pipeline no Sklearn**: `Pipeline`, `cross_val_score` e seleção de hiperparâmetros.
- **Aula 6 - Classification report e métricas de classificação**: matriz de confusão, `accuracy`, `precision`, `recall` e `F1`.
- **Aula 7 - AUC score e ROC Curve**: avaliação probabilística via `ROC` e `AUC`.

## Fluxo do pipeline de dados

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
arquivos .parquet mensais
    |
    v
merge_parquet_files.py
    |
    v
2025_consolidado.parquet
    |
    v
trabalho_parte_1.ipynb
    |
    v
2025_reduzido.parquet
    |
    v
trabalho_parte_2.ipynb
    |
    v
2025_tratado.parquet
```

## Parte 1 - Redução do volume da base

Arquivo: `trabalho_parte_1.ipynb`

Principais ações:

- leitura de `2025_consolidado.parquet`
- inspeção estrutural e estatística inicial
- seleção das colunas de interesse
- geração de `2025_reduzido.parquet`

Resultado documentado:

- base consolidada com **925.240 registros** e **114 colunas**
- base reduzida com **925.240 registros** e **54 colunas**

## Parte 2 - Tratamento de dados

Arquivo: `trabalho_parte_2.ipynb`

Principais ações:

- leitura de `2025_reduzido.parquet`
- avaliação de nulos, tipos e integridade
- recorte para internações de 2025
- criação de variáveis derivadas
- tratamento de CIDs
- identificação de indícios de violência contra mulher e câncer de mama
- geração de `2025_tratado.parquet`

Resultado documentado:

- base tratada com **857.726 registros**
- base analítica com variáveis derivadas como `IDADE_ANOS`, `DIAG_PRINC_GRUPO`, `VIOLENCIA_MULHER_NIVEL` e `CANCER_MAMA_NIVEL`

## Parte 3 - Classificação supervisionada com SVM e Random Forest

Arquivo: `trabalho_parte_3.ipynb`

Objetivo:

- construir classificadores supervisionados com `SVM` e `RandomForestClassifier`

Principais ações:

- criação do `TARGET` binário
- seleção de features e prevenção de vazamento
- separação treino/teste
- pré-processamento com `ColumnTransformer`
- tuning leve do `SVM`
- tuning leve do `Random Forest`
- comparação dos modelos no conjunto de teste

Observações metodológicas:

- o `SVM` foi treinado com padronização via `StandardScaler`
- o `Random Forest` foi usado como alternativa baseada em árvores
- o `recall` foi mantido como métrica central por causa do contexto de saúde

## Parte 4 - Classificação supervisionada para indícios de câncer de mama

Arquivo: `trabalho_parte_4.ipynb`

Objetivo:

- construir um classificador binário a partir de `CANCER_MAMA_NIVEL > 0`

Racional:

- a classificação supervisionada foi construída com foco em **detecção de casos positivos**
- no contexto de saúde, **falsos negativos são mais graves do que falsos positivos**
- por isso, a análise prioriza `recall`, matriz de confusão e avaliação probabilística

Principais ações:

- criação do `TARGET` binário
- seleção de features sem vazamento de target
- separação treino/teste com `stratify=y`
- pré-processamento com `Pipeline` e `ColumnTransformer`
- treinamento de `Logistic Regression`, `KNN` e `Random Forest`
- tuning simples de `k` no KNN
- escolha de `threshold` com base em validação para modelos probabilísticos
- avaliação com `accuracy`, `precision`, `recall`, `F1`, matriz de confusão, validação cruzada e `ROC/AUC`

Observações metodológicas:

- `class_weight='balanced'` foi usado na regressão logística para mitigar o desbalanceamento da classe positiva
- o `KNN` foi treinado em amostra estratificada por custo computacional no Colab
- `PROC_REA` foi excluída da modelagem por alta cardinalidade

## Análise Complementar 1 - Previsão do valor total da internação

Arquivo: `analise_complementar_1.ipynb`

Objetivo:

- prever `VAL_TOT` com modelos de regressão

Principais ações:

- seleção de features
- treino/teste
- regressão linear
- testes com PCA
- engenharia de features
- comparação entre versões do modelo

Resultado documentado:

- modelo base com **R² = 0,5664**
- modelo melhorado com **R² = 0,6370**

## Análise Complementar 2 - Agrupamentos relacionados ao câncer de mama

Arquivo: `analise_complementar_2.ipynb`

Objetivo:

- investigar agrupamentos não supervisionados em pacientes com indícios de câncer de mama

Principais ações:

- recorte da base tratada
- análise exploratória
- testes com `KMeans`
- testes com `DBSCAN`
- avaliação com `silhouette score`

Resultado documentado:

- melhor configuração quantitativa com `KMeans`
- conclusão analítica de que os grupos ficaram fortemente definidos por idade e pouco interpretáveis do ponto de vista clínico

## Como reproduzir as Partes 3 e 4

Pré-requisito mínimo:

- ter o arquivo `2025_tratado.parquet` no diretório atual do notebook ou em um dos caminhos configurados na primeira célula das Partes 3 e 4

Ordem mínima de execução:

1. gerar `2025_consolidado.parquet` ou obtê-lo a partir do link do README
2. rodar `trabalho_parte_1.ipynb`
3. rodar `trabalho_parte_2.ipynb`
4. rodar `trabalho_parte_3.ipynb`
5. rodar `trabalho_parte_4.ipynb`

## Considerações finais

O repositório representa um pipeline completo aplicado a dados públicos de saúde:

- obtenção e consolidação de dados
- redução e tratamento da base
- criação de variáveis analíticas
- regressão supervisionada
- agrupamentos não supervisionados
- classificação supervisionada com foco em métricas aderentes ao contexto de saúde
