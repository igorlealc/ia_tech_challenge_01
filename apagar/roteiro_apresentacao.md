# Roteiro de Apresentação

## Informações gerais

**Tema:** Classificação supervisionada para detecção de indícios de câncer de mama em registros hospitalares do DATASUS SIH/SUS RJ 2025  
**Objetivo:** Apresentar o pipeline de ciência de dados, desde a obtenção e tratamento da base até a comparação de modelos de machine learning para triagem de indícios de câncer de mama.  
**Tempo total estimado:** 15 minutos  
**Tempo por apresentador:** 3 minutos  

**Apresentadores:**

- Igor
- Paulo Eduardo
- Rod
- Jonas
- Gustavo Lima

---

## Sumário

1. Igor - Partes 1 e 2: Dados, EDA e Targets
2. Paulo Eduardo - Target, Baseline e KNN
3. Rod - SVM, Random Forest e Tuning Leve
4. Jonas - Métricas e Interpretação dos Resultados
5. Gustavo Lima - Considerações Finais

---

## 1. Igor - Partes 1 e 2: Dados, EDA e Targets

### Tempo estimado

3 minutos

### Objetivo da fala

Apresentar a origem dos dados, o fluxo de obtenção e consolidação da base, a redução inicial de colunas, os tratamentos realizados e a criação das variáveis que sustentam a modelagem.

### Trecho do notebook a ser mostrado

- Notebook: `trabalho_parte_1.ipynb`
- Seções/células: célula 1; Item 1; Item 2; Item 3; Item 4
- O que destacar visualmente: fonte DATASUS, formato DBC, fluxo DBC -> DBF -> Parquet, base `2025_consolidado.parquet`, redução de 114 para 54 colunas e validação da base reduzida.

- Notebook: `trabalho_parte_2.ipynb`
- Seções/células: célula 1; Item 2; Item 3; Item 5; Item 6; Item 9
- O que destacar visualmente: recorte para internações de 2025, avaliação de nulos/vazios, criação de `IDADE_ANOS`, tratamento dos campos CID e criação de `CANCER_MAMA_NIVEL`.

### Roteiro de fala

"A base usada no trabalho vem do DATASUS, mais especificamente do SIH/SUS RD, que é a base de AIH reduzida. O recorte foi o estado do Rio de Janeiro no ano de 2025. Os arquivos originais vieram em formato DBC e estavam separados por mês. Antes dos notebooks principais, eles foram convertidos para DBF, depois para Parquet, e por fim consolidados no arquivo `2025_consolidado.parquet`.

Na Parte 1, o objetivo foi reduzir o volume da base. A base consolidada tinha 925.240 registros e 114 colunas. Depois da análise estrutural, da consulta ao dicionário de dados e da seleção das variáveis relevantes, geramos a base `2025_reduzido.parquet`, mantendo os mesmos 925.240 registros, mas com 54 colunas.

Na Parte 2, entramos no tratamento dos dados. Primeiro avaliamos tipos, nulos e campos vazios. O notebook mostra que não havia nulos formais, mas havia campos vazios principalmente relacionados a CIDs, que foram tratados em uma etapa própria. Depois fizemos o recorte das internações de 2025, chegando a 857.726 registros.

Também criamos variáveis derivadas importantes, como `SEXO_LABEL`, `NASC_DT`, `ANO_NASC`, `IDADE_ANOS` e `DIAG_PRINC_GRUPO`. Uma parte central foi o tratamento dos CIDs, porque os indícios de câncer de mama foram identificados a partir desses campos. Com isso, foi criada a variável `CANCER_MAMA_NIVEL`, que depois serviu como base para o target binário da classificação."

### Pontos que não podem faltar

- Fonte: DATASUS SIH/SUS RD - AIH Reduzida, RJ, 2025.
- Arquivos originais em DBC, convertidos para DBF e Parquet.
- Base consolidada: 925.240 registros e 114 colunas.
- Base reduzida: 925.240 registros e 54 colunas.
- Base tratada: 857.726 registros.
- Tratamento dos CIDs e criação de `CANCER_MAMA_NIVEL`.

### Transição

"Com a base tratada e o target derivado dos indícios de câncer de mama, a próxima etapa foi transformar isso em um problema supervisionado e começar pelos modelos de referência."

---

## 2. Paulo Eduardo - Target, Baseline e KNN

### Tempo estimado

3 minutos

### Objetivo da fala

Explicar a definição do target binário, a preparação das features, o baseline com Regressão Logística e o teste com KNN.

### Trecho do notebook a ser mostrado

- Notebook: `trabalho_parte_4.ipynb`
- Seções/células: Item 1; Item 2; Item 3; Item 4; início do Item 5
- O que destacar visualmente: `TARGET = (CANCER_MAMA_NIVEL > 0)`, distribuição das classes, features selecionadas, exclusão de variáveis com vazamento, `train_test_split(..., stratify=y)`, `Pipeline`, `ColumnTransformer`, Regressão Logística e KNN.

### Roteiro de fala

"Na etapa de modelagem, transformamos a variável `CANCER_MAMA_NIVEL` em um target binário. A regra foi simples: quando `CANCER_MAMA_NIVEL` era maior que zero, o registro entrava como classe 1, com indício; quando era zero, entrava como classe 0, sem indício.

O primeiro ponto importante é o desbalanceamento. O notebook mostra 848.560 registros na classe 0 e 9.166 na classe 1. Em proporção, isso dá aproximadamente 98,93% sem indício e 1,07% com indício. Por isso, desde o início, a modelagem não poderia ser avaliada apenas por accuracy.

Depois selecionamos as features com cuidado para evitar vazamento de target. Colunas como `CANCER_MAMA_NIVEL`, diagnósticos CID e `DIAG_PRINC_GRUPO` foram excluídas da modelagem porque carregariam informação muito próxima da resposta. As variáveis usadas incluíram idade, permanência, diárias, uso de UTI, sexo, raça/cor e algumas variáveis administrativas.

Como baseline, usamos Regressão Logística. Ela é um bom ponto de comparação porque é simples, interpretável e permite trabalhar com probabilidades e ajuste de threshold. Também usamos `class_weight='balanced'`, justamente para dar mais peso à classe positiva, que é minoria.

O KNN foi testado como outro modelo clássico de classificação. Como ele depende de distância, o uso de `StandardScaler` no pipeline é importante. O notebook testou valores de k como 3, 5, 9 e 15. O melhor k ficou em 3, mas o resultado final mostrou uma limitação forte: no teste, o KNN teve accuracy alta, 0,9880, mas recall de apenas 0,0207. Isso significa que ele quase não encontrou os casos positivos."

### Pontos que não podem faltar

- Target: `CANCER_MAMA_NIVEL > 0`.
- Distribuição: 848.560 negativos e 9.166 positivos.
- Problema fortemente desbalanceado.
- Uso de `stratify=y` no treino/teste.
- Baseline com Regressão Logística e `class_weight='balanced'`.
- KNN com `k=3`, mas recall final muito baixo: 0,0207.

### Transição

"Depois desses primeiros modelos, o grupo comparou abordagens mais robustas, incluindo SVM com escala padronizada e Random Forest com um tuning leve."

---

## 3. Rod - SVM, Random Forest e Tuning Leve

### Tempo estimado

3 minutos

### Objetivo da fala

Apresentar o uso de SVM com scaler, o Random Forest, o tuning leve com `GridSearchCV` e os principais resultados da Parte 3.

### Trecho do notebook a ser mostrado

- Notebook: `trabalho_parte_3.ipynb`
- Seções/células: Item 1; Item 2; Item 3; Item 4; Item 5; Item 6; Item 7; Conclusão
- O que destacar visualmente: target binário, features selecionadas, `ColumnTransformer`, `StandardScaler`, `LinearSVC`, `RandomForestClassifier`, parâmetros testados e tabela de comparação final.

### Roteiro de fala

"Na Parte 3, seguimos com o mesmo target binário baseado em `CANCER_MAMA_NIVEL > 0`. A distribuição permaneceu muito desbalanceada: 848.560 registros negativos e 9.166 positivos. Por isso, o tuning foi orientado por recall, e não por accuracy.

O primeiro modelo desta etapa foi o SVM. Como o SVM é sensível à escala das variáveis, ele foi treinado dentro de um pipeline com `StandardScaler` para as variáveis numéricas e one-hot encoding para as categóricas. Foi usado `LinearSVC` com `class_weight='balanced'`.

O tuning do SVM foi leve, com `GridSearchCV`, 3 folds e uma grade pequena. Os parâmetros testados envolveram `C` igual a 0,5, 1,0 e 2,0, com `loss='squared_hinge'`. O melhor resultado médio de recall na validação cruzada foi 0,9270.

Depois testamos Random Forest, que é um modelo baseado em árvores. A vantagem é que ele consegue capturar relações não lineares e interações entre variáveis sem depender tanto da escala. O tuning também foi leve, com combinações de `n_estimators`, `max_depth` e `min_samples_leaf`. O melhor conjunto foi `n_estimators=150`, `max_depth=8` e `min_samples_leaf=5`, com recall médio de 0,8567 na validação.

No teste final, o SVM teve recall de 0,9274, accuracy de 0,6962 e F1 de 0,0612. O Random Forest teve recall de 0,9214, accuracy de 0,7250 e F1 de 0,0668. Ou seja, os dois modelos conseguiram capturar a maior parte dos positivos, mas com baixa precision, o que mostra muitos falsos positivos. Dentro do objetivo de triagem em saúde, isso é aceitável até certo ponto, porque o foco é reduzir falsos negativos."

### Pontos que não podem faltar

- SVM exige scaler por ser sensível à escala.
- `LinearSVC` com `class_weight='balanced'`.
- Tuning SVM: `C` em 0,5, 1,0 e 2,0; melhor recall CV 0,9270.
- Random Forest captura relações não lineares.
- Tuning Random Forest: `n_estimators`, `max_depth`, `min_samples_leaf`.
- Resultado teste Parte 3: SVM recall 0,9274; Random Forest recall 0,9214.

### Transição

"Com os modelos treinados, a interpretação correta depende das métricas. Por isso, a próxima parte foca em recall, F1, accuracy, matriz de confusão e comparação final."

---

## 4. Jonas - Métricas e Interpretação dos Resultados

### Tempo estimado

3 minutos

### Objetivo da fala

Explicar por que o recall foi a métrica principal, como interpretar as métricas em base desbalanceada e como os resultados apoiaram a comparação dos modelos.

### Trecho do notebook a ser mostrado

- Notebook: `trabalho_parte_4.ipynb`
- Seções/células: Item 5; Item 6; Item 7; Item 8; Conclusão
- O que destacar visualmente: classification reports, matrizes de confusão, tabela comparativa, validação cruzada, ROC/AUC.

- Notebook: `trabalho_parte_3.ipynb`
- Seções/células: Item 7 e Item 8
- O que destacar visualmente: tabela final SVM vs Random Forest e matrizes de confusão.

### Roteiro de fala

"A parte de avaliação é central porque a base é extremamente desbalanceada. Como quase 99% dos registros são negativos, um modelo que marcasse tudo como sem indício teria accuracy muito alta, mas seria inútil para triagem. Por isso, a accuracy aparece como métrica de apoio, mas não como critério principal.

O recall foi definido como métrica principal porque responde à pergunta mais importante: dos casos que realmente tinham indício, quantos o modelo conseguiu identificar? No contexto de saúde, falso negativo é o erro mais crítico, porque significa deixar passar um possível caso positivo.

O F1-score entra como uma métrica de equilíbrio entre precision e recall. Ele ajuda a observar se o modelo está apenas aumentando recall às custas de falsos positivos demais. Mesmo assim, neste trabalho, o recall tem prioridade por causa do objetivo de triagem.

Na Parte 4, o resultado no conjunto de teste mostrou que a Regressão Logística teve recall de 0,7436, precision de 0,0365 e F1 de 0,0697. O KNN teve accuracy de 0,9880, mas recall de só 0,0207, identificando apenas 38 dos 1.833 positivos reais. Isso mostra por que accuracy sozinha engana. Já o Random Forest teve o melhor comportamento geral no teste: recall de 0,7741, precision de 0,0508, F1 de 0,0954 e AUC de 0,8962.

A matriz de confusão ajuda a traduzir isso em contagens. No Random Forest da Parte 4, foram 1.419 positivos encontrados e 414 falsos negativos. Na Regressão Logística, foram 1.363 positivos encontrados e 470 falsos negativos. O KNN deixou passar 1.795 positivos, por isso não foi adequado para o objetivo.

Sobre feature importance do Random Forest, não encontrei esse resultado registrado nos notebooks ou relatórios disponíveis. Então essa parte deve ser preenchida depois, caso o grupo gere o gráfico ou a tabela no notebook: [PREENCHER COM RESULTADO DO NOTEBOOK/ARQUIVO]."

### Pontos que não podem faltar

- Recall é principal porque falsos negativos são mais graves em saúde.
- Accuracy é insuficiente em base com aproximadamente 99% de negativos.
- KNN teve accuracy alta, mas recall muito baixo.
- Random Forest Parte 4 teve melhor desempenho geral no teste: recall 0,7741, F1 0,0954 e AUC 0,8962.
- Feature importance não foi encontrada nos arquivos: [PREENCHER COM RESULTADO DO NOTEBOOK/ARQUIVO].

### Transição

"Com essa leitura das métricas, a conclusão do trabalho é que o modelo precisa ser escolhido pelo objetivo de triagem, e não apenas pela taxa geral de acerto."

---

## 5. Gustavo Lima - Considerações Finais

### Tempo estimado

3 minutos

### Objetivo da fala

Fechar a apresentação sintetizando o pipeline, os resultados, as limitações e as melhorias futuras.

### Trecho do notebook a ser mostrado

- Notebook: `trabalho_parte_4.ipynb`
- Seções/células: Item 6; Item 7; Item 8; Conclusão
- O que destacar visualmente: comparação final dos modelos, validação cruzada, AUC e conclusão.

- Notebook: `trabalho_parte_3.ipynb`
- Seções/células: Conclusão da Parte 3
- O que destacar visualmente: uso de recall como métrica central e comparação entre SVM e Random Forest.

### Roteiro de fala

"Para concluir, o trabalho demonstrou um pipeline completo de ciência de dados aplicado a dados públicos de saúde. Começamos com dados brutos do DATASUS, fizemos conversão, consolidação, redução da base, tratamento de campos, criação de variáveis derivadas e depois modelagem supervisionada.

O principal aprendizado foi que, em problemas de saúde e com base desbalanceada, a escolha da métrica muda completamente a interpretação. Se olhássemos apenas para accuracy, o KNN pareceria bom, porque teve 98,80% de acerto. Mas ele praticamente não encontrou a classe positiva. Por isso, recall, matriz de confusão, F1 e AUC foram mais importantes para avaliar utilidade real.

Entre os modelos avaliados na Parte 4, o Random Forest apresentou o melhor comportamento geral no conjunto de teste. Ele teve recall de 77,41%, F1 de 9,54% e AUC de 89,62%, capturando 1.419 dos 1.833 casos positivos reais. A Regressão Logística também foi competitiva em recall e teve bom resultado na validação cruzada. O SVM da Parte 3 alcançou recall ainda maior, 92,74%, mas com baixa precision e grande volume de falsos positivos, o que precisa ser analisado conforme o custo operacional de uma triagem.

As principais limitações foram o forte desbalanceamento da classe positiva, a baixa precision dos modelos, o risco de vazamento de target em variáveis diagnósticas e a necessidade de validação com especialista de domínio. Também há limitações naturais dos dados administrativos: eles foram gerados para registro hospitalar, não necessariamente para predição clínica.

Como melhorias futuras, o grupo poderia testar estratégias de balanceamento, calibrar thresholds com critérios definidos junto a especialistas, incluir validação temporal, avaliar explicabilidade do Random Forest e documentar a feature importance no notebook. Mesmo com essas limitações, o trabalho mostrou na prática como aplicar machine learning de forma crítica: não basta treinar modelos, é preciso alinhar dados, métrica e objetivo do problema."

### Pontos que não podem faltar

- Pipeline completo: obtenção, consolidação, tratamento, target e modelos.
- Accuracy isolada não resolve o problema.
- Random Forest Parte 4 teve melhor comportamento geral no teste.
- SVM Parte 3 teve recall alto, mas muitos falsos positivos.
- Limitações: desbalanceamento, baixa precision, validação de domínio e risco de leakage.
- Melhorias: balanceamento, threshold, validação temporal, explicabilidade e feature importance.

### Fechamento

"Assim, o trabalho cumpre o objetivo acadêmico de aplicar machine learning em um problema real de saúde, mostrando não só os resultados dos modelos, mas também as decisões metodológicas necessárias para interpretar esses resultados com responsabilidade."

---

## Considerações finais

Este roteiro foi construído com base nos arquivos existentes do projeto, especialmente `README.md`, `trabalho_parte_1.ipynb`, `trabalho_parte_2.ipynb`, `trabalho_parte_3.ipynb`, `trabalho_parte_4.ipynb` e `RELATORIO_EXPLICATIVO_PARTE_4.md`.

Informações não localizadas nos arquivos foram mantidas como pendência explícita:

- Feature importance do Random Forest: [PREENCHER COM RESULTADO DO NOTEBOOK/ARQUIVO]
