# README do Trabalho - Pós-Graduação FIAP IA para Devs

## Visão geral

Este trabalho utiliza dados públicos do DATASUS, especificamente a base **SIH/SUS RD - AIH Reduzida** do estado do Rio de Janeiro no ano de 2025.

O objetivo geral é construir um fluxo de ciência de dados dividido em três partes:

1. Redução e organização inicial da base hospitalar.
2. Tratamento, validação e criação de variáveis derivadas.
3. Construção e avaliação de modelos de regressão para previsão do valor total da internação.

Os notebooks foram organizados em sequência para facilitar a apresentação do trabalho, a leitura técnica e a reprodução conceitual das etapas executadas.

## Estrutura dos notebooks

| Arquivo | Parte | Objetivo principal |
|---|---:|---|
| `trabalho/trabalho_parte_1.ipynb` | Parte 1 | Reduzir o volume da base consolidada e gerar a base reduzida. |
| `trabalho/trabalho_parte_2.ipynb` | Parte 2 | Tratar a base reduzida, validar campos e gerar a base tratada. |
| `trabalho/trabalho_parte_3.ipynb` | Parte 3 | Treinar e avaliar modelos para previsão de `VAL_TOT`. |

## Parte 1 - Redução do volume da base de dados

Arquivo: `trabalho/trabalho_parte_1.ipynb`

Este notebook apresenta a primeira etapa do trabalho. A base consolidada de 2025 é carregada, analisada estruturalmente e reduzida para manter apenas as colunas consideradas relevantes para as etapas seguintes.

### Principais ações executadas

- Carregamento do arquivo `2025_consolidado.parquet`.
- Visualização de amostra inicial da base.
- Análise descritiva geral.
- Conferência das dimensões da base consolidada.
- Verificação dos tipos de dados e uso de memória.
- Consulta do dicionário de dados da base SIH/SUS RD - AIH Reduzida.
- Definição das colunas mantidas para o recorte analítico.
- Remoção das colunas não utilizadas.
- Geração do arquivo `2025_reduzido.parquet`.
- Validação da base reduzida por colunas e shape final.

### Resultado da etapa

A base original consolidada contém **925.240 registros** e **114 colunas**. Após a seleção das variáveis de interesse, foi gerada a base reduzida com **925.240 registros** e **54 colunas**.

Essa etapa prepara os dados para o tratamento mais detalhado realizado na Parte 2.

## Parte 2 - Tratamento de dados

Arquivo: `trabalho/trabalho_parte_2.ipynb`

Este notebook realiza o tratamento da base reduzida. O foco é avaliar qualidade, consistência, tipos de dados, campos diagnósticos e criar variáveis derivadas que apoiem a análise exploratória e a modelagem.

### Principais ações executadas

- Carregamento do arquivo `2025_reduzido.parquet`.
- Atualização do dicionário de dados da base reduzida.
- Avaliação de nulos, vazios e tipos de dados.
- Recorte da base para internações com `DT_INTER` em 2025.
- Criação da variável `SEXO_LABEL`.
- Conversão da data de nascimento para `NASC_DT`.
- Criação de `ANO_NASC` e `IDADE_ANOS`.
- Avaliação de integridade e comparação geral por sexo.
- Remoção da coluna `ETNIA`.
- Validação de formato dos campos CID.
- Criação de representações numéricas para CIDs.
- Criação de `DIAG_PRINC_GRUPO`.
- Identificação e classificação de indícios de violência contra mulher em campos CID.
- Identificação e classificação de indícios de câncer de mama em campos CID.
- Avaliação da coluna `MES_CMPT`.
- Geração da base tratada final.
- Registro do dicionário da base tratada.

### Resultado da etapa

A base tratada contém **857.726 registros** após o recorte das internações de 2025.

O notebook documenta uma base tratada com **74 colunas analíticas**, incluindo variáveis originais preservadas e variáveis derivadas, como:

- `NASC_DT`
- `ANO_NASC`
- `IDADE_ANOS`
- `DIAG_PRINC_GRUPO`
- `VIOLENCIA_MULHER_NIVEL`
- `CANCER_MAMA_NIVEL`
- representações numéricas derivadas dos campos CID

Essa etapa gera a base utilizada na modelagem da Parte 3.

## Parte 3 - Previsão do valor total da internação

Arquivo: `trabalho/trabalho_parte_3.ipynb`

Este notebook apresenta a etapa de modelagem. O objetivo é prever o valor total da internação, representado pela variável `VAL_TOT`, a partir de variáveis clínicas, demográficas, administrativas e de permanência hospitalar.

### Principais ações executadas

- Carregamento da base tratada.
- Análise descritiva inicial.
- Seleção inicial de features.
- Avaliação de correlação entre variáveis.
- Separação entre treino e teste.
- Treinamento de modelo base com regressão linear.
- Avaliação do modelo base com métricas de regressão.
- Teste com PCA no modelo base.
- Avaliação de outliers em `VAL_TOT`.
- Aplicação de transformação logarítmica na variável-alvo.
- Avaliação das previsões na escala logarítmica e após reversão para escala original.
- Criação de features por faixas de idade.
- Criação de features por faixas de dias de internação.
- Criação de categorias para procedimentos realizados.
- Tratamento da complexidade do atendimento.
- Aplicação de target encoding para `DIAG_PRINC`.
- Treinamento do modelo melhorado.
- Comparação entre modelo base, transformação logarítmica, modelo com encoding e modelo com encoding + PCA.

### Métricas avaliadas

As métricas utilizadas para comparação dos modelos foram:

- **R²**: proporção da variabilidade explicada pelo modelo.
- **MAE**: erro médio absoluto.
- **RMSE**: raiz do erro quadrático médio, mais sensível a erros grandes.
- **MAPE**: erro percentual absoluto médio.

### Resultado geral da modelagem

O modelo base apresentou desempenho moderado, com **R² de 0,5664**. Após a engenharia de features e aplicação de técnicas de encoding, o modelo melhorado alcançou **R² de 0,6370**.

A transformação logarítmica apresentou desempenho inadequado após a reversão para a escala original, indicando que, neste conjunto de dados, o modelo em escala original foi mais estável para interpretação em reais.

O teste com PCA não trouxe ganho relevante de desempenho, pois os resultados permaneceram praticamente iguais aos do modelo sem redução de dimensionalidade.

## Fluxo resumido da entrega

```text
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
        |
        v
trabalho_parte_3.ipynb
        |
        v
avaliação dos modelos de regressão
```

## Considerações para apresentação

O trabalho demonstra um pipeline completo de ciência de dados aplicado a dados públicos de saúde:

- obtenção e consolidação de dados hospitalares;
- redução de dimensionalidade inicial por seleção de colunas;
- tratamento e validação de dados;
- criação de variáveis derivadas;
- avaliação de problemas de qualidade e consistência;
- preparação de features;
- treinamento e comparação de modelos;
- análise crítica dos resultados.

Como ponto de melhoria futura, recomenda-se aprofundar a validação das variáveis com apoio de especialista de domínio, principalmente para reduzir risco de uso de variáveis pós-evento e melhorar a interpretação clínica ou administrativa dos modelos.
