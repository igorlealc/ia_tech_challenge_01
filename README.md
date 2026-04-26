# README do Trabalho - Pós-Graduação FIAP IA para Devs

## Visão geral

Este trabalho utiliza dados públicos do DATASUS, especificamente a base **SIH/SUS RD - AIH Reduzida** do estado do Rio de Janeiro no ano de 2025.

O objetivo geral é construir um fluxo de ciência de dados dividido em quatro partes:

1. Redução e organização inicial da base hospitalar.
2. Tratamento, validação e criação de variáveis derivadas.
3. Construção e avaliação de modelos de regressão para previsão do valor total da internação.
4. Análise exploratória e agrupamento de perfis relacionados ao câncer de mama.

Os notebooks foram organizados em sequência para facilitar a apresentação do trabalho, a leitura técnica e a reprodução conceitual das etapas executadas.

## Dados

### Documentação de apoio

CERQUEIRA, Daniel R. C.; COELHO, Danilo S. C.; ALVES, Paloma P.; REIS, Milena V. M.; LIMA, Adriana S. **Uma análise da base de dados do Sistema de Informação Hospitalar entre 2001 e 2018: dicionário dinâmico, disponibilidade dos dados e aspectos metodológicos para a produção de indicadores sobre violência**. Brasília: Ipea, 2019. Disponível em: <https://www.ipea.gov.br/atlasviolencia/arquivos/artigos/9058-sistemahospitalar.pdf>. Acesso em: 26 abr. 2026.

As bases utilizadas neste trabalho referem-se a dados do DATASUS de pronto atendimento no estado do Rio de Janeiro durante 2025.

Arquivos originais em formato DBC:

- Ano 2025 dividio por mês: <https://1drv.ms/u/c/82e7decc796c67f4/IQCY5D37m4UjQKOhAzC1HWQOAa9sQesSOF7ZM0BD57WUdhk?e=Tw1Ib4>

Arquivos finais disponibilizados:

- Versão final consolidada: <https://1drv.ms/u/c/82e7decc796c67f4/IQAzoDEOMdnWQIdJivtSpFz_AanG6z7Cq5c6qFcp1soRwDM?e=hLqcXC>

## Estrutura dos notebooks

| Arquivo | Parte | Objetivo principal |
|---|---:|---|
| `trabalho/trabalho_parte_1.ipynb` | Parte 1 | Reduzir o volume da base consolidada e gerar a base reduzida. |
| `trabalho/trabalho_parte_2.ipynb` | Parte 2 | Tratar a base reduzida, validar campos e gerar a base tratada. |
| `trabalho/trabalho_parte_3.ipynb` | Parte 3 | Treinar e avaliar modelos para previsão de `VAL_TOT`. |
| `trabalho/trabalho_parte_4.ipynb` | Parte 4 | Explorar agrupamentos de perfis relacionados ao câncer de mama com KMeans e DBSCAN. |

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

## Parte 4 - Agrupamentos relacionados ao câncer de mama

Arquivo: `trabalho/trabalho_parte_4.ipynb`

Este notebook apresenta uma etapa de análise exploratória com técnicas de agrupamento não supervisionado. O foco é investigar se atributos pessoais e administrativos simples, com destaque para `IDADE_ANOS` e `RACA_COR`, permitem identificar perfis relevantes entre pacientes com algum nível de evidência de câncer de mama.

### Principais ações executadas

- Carregamento da base tratada com recorte para pacientes do sexo feminino e com `CANCER_MAMA_NIVEL > 0`.
- Análise descritiva inicial e recorte das colunas utilizadas no experimento.
- Conferência das dimensões da base e preparação de variáveis auxiliares.
- Registro interpretativo dos níveis de câncer de mama e da codificação de `RACA_COR`.
- Geração de distribuições gerais e estratificadas por nível de câncer de mama.
- Inspeção de boxplots, histogramas e correlação entre variáveis pessoais.
- Criação de faixas para dias de internação.
- Execução de experimentos com `KMeans` sem escalonamento.
- Avaliação da distribuição dos grupos, centróides e teste de diferentes valores de `k` com método elbow.
- Repetição do `KMeans` com padronização.
- Aplicação de one-hot encoding em `RACA_COR`.
- Aplicação de `PCA` e novos testes de clusterização com `KMeans`.
- Execução de `DBSCAN` para comparação com a abordagem baseada em centróides.
- Comparação final dos resultados com `silhouette score`.

### Resultado geral da análise de agrupamentos

O melhor resultado quantitativo do notebook foi obtido com **KMeans**, alcançando **silhouette score de 0,7763** após one-hot encoding e PCA. O **DBSCAN** apresentou **silhouette score de 0,6842**, ficando abaixo da melhor configuração do `KMeans`.

Apesar disso, a conclusão analítica do notebook é que os agrupamentos encontrados **não formaram perfis pessoais suficientemente significativos**. Na prática, os grupos ficaram definidos quase integralmente pela variável **idade**, enquanto `RACA_COR` teve contribuição limitada na segmentação.

Isso indica que, embora as técnicas tenham produzido separações matematicamente válidas, o conjunto de variáveis utilizado nesta etapa foi insuficiente para gerar uma leitura exploratória mais rica sobre perfis relacionados ao câncer de mama. O notebook registra como principal recomendação futura a repetição desse tipo de análise com **apoio de especialista do domínio**, para orientar a escolha de atributos mais informativos e clinicamente interpretáveis.

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
        |
        v
trabalho_parte_4.ipynb
        |
        v
análise exploratória e agrupamentos
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
- experimentos de agrupamento não supervisionado;
- análise crítica dos resultados.
