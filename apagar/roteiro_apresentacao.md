# Roteiro de Apresentação

## Arquivo principal

Usar o notebook [apresentacao_final.ipynb](/Users/paulomoreira/Documents/Projetos/Pós IA/ia_tech_challenge_01/apresentacao_final.ipynb).

Ele foi reorganizado para apresentação e já elimina boa parte das quebras de narrativa do material original.

## Informações gerais

**Tema:** Classificação supervisionada para detecção de indícios de câncer de mama em registros hospitalares do DATASUS SIH/SUS RJ 2025  
**Tempo total estimado:** 15 minutos  
**Tempo por apresentador:** até 3 minutos

## Estrutura sugerida

1. Igor: dados, redução da base e tratamento
2. Paulo Eduardo: target binário, baseline e KNN
3. Rod: SVM e Random Forest
4. Jonas: métricas e interpretação
5. Gustavo Lima: conclusão

---

## 1. Igor

### Objetivo

Explicar de onde vieram os dados, como a base foi reduzida e como o tratamento preparou o problema para a classificação.

### Células para abrir

- `5` e `6` para preparação do ambiente
- `8` para abertura da Parte 1
- `9` e `10` para mostrar as dimensões da base consolidada
- `11` e `12` para mostrar a validação da base reduzida
- `13`, `14` e `15` para nulos e campos vazios
- `16` e `17` para o recorte de 2025
- `18` e `19` para tratamento da idade
- `20` e `21` para tratamento dos campos CID
- `22` e `23` para a consolidação do indício de câncer de mama
- `24` e `25` para a base tratada final

### Fala sugerida

"A base usada no projeto veio do DATASUS, mais especificamente do SIH/SUS RD do estado do Rio de Janeiro, com recorte de 2025. Primeiro carregamos o ambiente da apresentação nas células 5 e 6, e depois avaliamos a estrutura da base. A base consolidada tinha 925.240 registros e 114 colunas, como aparece nas células 9 e 10.

Depois fizemos a redução da base para manter apenas as variáveis relevantes ao problema. A validação da base reduzida mostra que continuamos com 925.240 registros, mas passamos para 54 colunas, como aparece nas células 11 e 12.

Na etapa seguinte, tratamos os dados. Verificamos nulos e campos vazios, especialmente nos campos CID, fizemos o recorte das internações de 2025 e tratamos variáveis derivadas como idade. O ponto mais importante para a apresentação está nas células 20 a 23: foi no tratamento dos CIDs que consolidamos a informação clínica usada depois para gerar o target binário de indício de câncer de mama.

Ao final, chegamos a uma base tratada com 857.726 registros, pronta para a etapa de modelagem."

### Transição

"Com a base tratada, o próximo passo foi transformar esse problema em uma classificação supervisionada binária."

---

## 2. Paulo Eduardo

### Objetivo

Explicar o target binário, o motivo do desbalanceamento ser crítico, o baseline com Regressão Logística e por que o KNN foi ruim nesse cenário.

### Células para abrir

- `27` para por que accuracy sozinha engana
- `28` para abertura da Parte 4
- `29` para definição do target
- `30` e `31` para regra de decisão final dos modelos
- `32` e `33` para explicar como chegamos ao threshold da Regressão Logística
- `35` e `36` para preparação das features
- `37` para treino/teste
- `38` e `39` para pipeline e modelos
- `40`, `41` e `42` para avaliação e interpretação do KNN
- `43` para comparação dos resultados

### Fala sugerida

"Na modelagem, definimos um target binário: classe 0 para registros sem indício e classe 1 para registros com indício de câncer de mama. Isso aparece nas células 28 e 29.

O primeiro ponto crítico é o desbalanceamento. Temos 848.560 registros negativos e apenas 9.166 positivos. Isso significa que quase 99% da base está na classe 0. Nesse contexto, falso negativo é o erro mais grave, porque significa deixar passar um caso com indício real.

Antes de avaliar os resultados, vale destacar que a regra de decisão não foi escolhida no chute. Nas células 30 e 31 aparece a configuração final dos modelos: nos modelos probabilísticos, o threshold foi estimado na validação com base na curva precision-recall; no KNN, o que foi ajustado foi o valor de k.

Se alguém perguntar de onde saiu exatamente o 0.6314 da Regressão Logística, isso está nas células 32 e 33. O notebook mostra que avaliamos vários thresholds no conjunto de validação, filtramos os que mantinham recall de pelo menos 75% e, entre eles, escolhemos o de maior precision. Foi assim que chegamos ao threshold final.

Depois selecionamos as features com cuidado para evitar vazamento. Variáveis diretamente ligadas ao diagnóstico foram removidas da modelagem, e mantivemos idade, permanência, diárias, uso de UTI, sexo, raça/cor e variáveis administrativas.

Como baseline, usamos Regressão Logística, porque ela é simples, interpretável e serve como uma boa referência inicial. Também testamos KNN. O problema aparece nas células 40 a 43: o KNN teve accuracy muito alta, 98,80%, mas recall de apenas 2,07%. Na prática, ele quase não encontrou os casos positivos.

Então esse bloco mostra duas coisas: accuracy sozinha pode enganar e, para triagem em saúde, o foco precisa estar em reduzir falsos negativos."

### Transição

"Depois do baseline e do KNN, o grupo comparou modelos mais robustos para esse tipo de problema."

---

## 3. Rod

### Objetivo

Apresentar SVM, Random Forest e o tuning leve aplicado na Parte 3.

### Células para abrir

- `45` para abertura da Parte 3
- `46` para target binário
- `47` para seleção de features
- `48` para treino/teste
- `49` para pré-processamento
- `50` e `51` para tuning do SVM
- `52` e `53` para tuning do Random Forest
- `54` e `55` para avaliação e comparação
- `56` para a conclusão da Parte 3

### Fala sugerida

"Na Parte 3, seguimos com o mesmo target binário e com a mesma preocupação com o desbalanceamento. Por isso, o critério principal continuou sendo recall.

O SVM foi treinado com padronização das variáveis numéricas, porque esse modelo é sensível à escala. Já o Random Forest entrou como uma alternativa baseada em árvores, capaz de capturar relações não lineares.

Foi feito um tuning leve para os dois modelos. No SVM, testamos valores diferentes de C. No Random Forest, variamos parâmetros como número de árvores, profundidade e tamanho mínimo das folhas.

Na avaliação final, os dois modelos tiveram recall alto. O SVM chegou a 0,9274 e o Random Forest a 0,9214. Isso significa que ambos conseguiram capturar a maior parte dos casos positivos, embora com baixa precision e muitos falsos positivos.

Para o objetivo de triagem, isso é aceitável até certo ponto, porque o custo maior está em deixar passar casos positivos."

### Transição

"Com os modelos treinados, a leitura correta passa a depender principalmente das métricas."

---

## 4. Jonas

### Objetivo

Explicar por que recall foi a métrica principal e como interpretar os resultados finais.

### Células para abrir

- `58`, `59` e `60` para avaliação dos modelos
- `61` para comparação final
- `62` e `63` para matrizes de confusão
- `64` e `65` para validação cruzada
- `66` e `67` para ROC e AUC
- `68` para a conclusão da Parte 4

### Fala sugerida

"A parte de avaliação é central porque a base é fortemente desbalanceada. Em uma base assim, accuracy não basta. Um modelo pode acertar quase tudo prevendo a classe majoritária e ainda assim ser inútil.

Por isso, a métrica principal foi recall. Em saúde, recall responde à pergunta mais importante: quantos dos casos realmente positivos o modelo conseguiu identificar. Isso é fundamental porque o falso negativo é o erro mais crítico.

Os resultados mostram bem essa diferença. O KNN teve accuracy alta, mas recall muito baixo. Já a Regressão Logística e o Random Forest tiveram desempenho mais coerente com o objetivo do projeto. Entre eles, o Random Forest apresentou o melhor equilíbrio geral no teste, com recall de 0,7741, F1 de 0,0954 e AUC de 0,8962.

As matrizes de confusão ajudam a traduzir isso em contagens reais, e por isso vale abrir explicitamente as células 62 e 63. No fim, a conclusão é que o modelo precisa ser escolhido pelo objetivo de triagem, e não pela taxa geral de acerto."

### Transição

"Com essa interpretação das métricas, a conclusão do projeto fica mais consistente."

---

## 5. Gustavo Lima

### Objetivo

Fechar a apresentação com uma síntese do pipeline, dos resultados, das limitações e das melhorias futuras.

### Células para abrir

- `68` para a conclusão da Parte 4
- `70` para limitações e próximos passos

### Fala sugerida

"Para concluir, o projeto demonstrou um pipeline completo de ciência de dados aplicado a uma base pública de saúde. Começamos com dados brutos do DATASUS, fizemos consolidação, redução da base, tratamento, definição do target binário e comparação de modelos supervisionados.

O principal aprendizado foi que, em um problema de triagem com base desbalanceada, não faz sentido olhar apenas para accuracy. A interpretação correta depende do custo do erro, especialmente do falso negativo.

Entre os modelos avaliados, o Random Forest teve o melhor comportamento geral na Parte 4, enquanto o SVM mostrou recall ainda mais alto na Parte 3, com o custo de muitos falsos positivos. Isso reforça que a escolha do modelo depende do objetivo da aplicação.

Como limitações, o trabalho ainda enfrenta forte desbalanceamento, baixa precision e necessidade de validação com especialista de domínio. Como próximos passos, faria sentido testar estratégias de balanceamento, calibração de threshold, validação temporal e explicabilidade."

### Fechamento

"Em resumo, o trabalho mostra que aplicar machine learning em saúde exige não só treinar modelos, mas alinhar dados, métricas e objetivo clínico de forma coerente."
