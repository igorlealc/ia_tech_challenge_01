## Papel do agente

Você é um especialista em ciência de dados, comunicação acadêmica, storytelling técnico e geração de documentos acadêmicos em PDF.

Sua tarefa é analisar os arquivos da pasta do projeto e montar um **roteiro de apresentação acadêmica** para um trabalho de machine learning, considerando que a apresentação será feita diretamente a partir dos **notebooks Python do projeto**, e não por slides.

Ao final, gere um **arquivo PDF com o roteiro final**.

---

## Contexto do trabalho

O trabalho envolve análise de dados e aplicação de modelos de machine learning, incluindo:

- Obtenção dos dados;
- Análise exploratória de dados — EDA;
- Definição e preparação dos targets;
- Modelos supervisionados:
  - Baseline com Regressão Logística;
  - KNN;
  - SVM com scaler;
  - Random Forest;
  - Tuning leve;
- Avaliação com métricas:
  - Recall como métrica principal;
  - F1-score;
  - Accuracy;
  - Matriz de confusão;
  - Feature importance com Random Forest;
- Considerações finais.

---

## Objetivo

Gerar um **roteiro de apresentação oral**, dividido por apresentador, com tempo aproximado de **3 minutos para cada pessoa**, utilizando como apoio visual os próprios **notebooks Python**.

A apresentação deve ser clara, objetiva e adequada para um trabalho acadêmico de pós-graduação.

---

## Divisão da apresentação

### Igor — 3 minutos

Responsável por apresentar:

1. Parte 1;
2. Parte 2;
3. Obtenção dos dados;
4. Análise exploratória dos dados — EDA;
5. Definição inicial dos targets.

O roteiro deve explicar:

- Qual foi a fonte dos dados;
- Como os dados foram obtidos;
- Qual foi o objetivo da análise;
- Quais variáveis foram observadas;
- Quais tratamentos iniciais foram realizados;
- Quais insights surgiram na EDA;
- Como os targets foram pensados ou construídos.

---

### Paulo Eduardo — 3 minutos

Responsável por apresentar:

1. Target da parte 3;
2. Modelo baseline com Regressão Logística;
3. Modelo KNN.

O roteiro deve explicar:

- Qual target foi utilizado na parte 3;
- Por que esse target foi escolhido;
- Como foi montado o baseline;
- Por que a Regressão Logística foi usada como comparação inicial;
- Como o KNN foi aplicado;
- Quais cuidados foram necessários com variáveis numéricas/categóricas;
- Quais foram os principais resultados ou limitações.

---

### Rod — 3 minutos

Responsável por apresentar:

1. SVM com scaler;
2. Random Forest;
3. Tuning leve.

O roteiro deve explicar:

- Por que o SVM exigiu uso de scaler;
- Como o SVM foi aplicado;
- Como o Random Forest foi utilizado;
- Por que Random Forest pode capturar relações não lineares;
- O que foi feito no tuning leve;
- Quais hiperparâmetros foram testados;
- Qual foi o objetivo do tuning: melhorar desempenho sem overengineering.

---

### Jonas — 3 minutos

Responsável por apresentar:

1. Métricas de avaliação;
2. Recall como métrica principal;
3. F1-score;
4. Accuracy;
5. Matriz de confusão;
6. Feature importance do Random Forest.

O roteiro deve explicar:

- Por que o recall foi definido como métrica principal;
- O que significa recall no contexto do problema;
- Por que accuracy sozinha pode ser insuficiente;
- Como interpretar F1-score;
- Como interpretar a matriz de confusão;
- O que a feature importance mostrou;
- Como as métricas ajudaram a comparar os modelos.

---

### Gustavo Lima — 3 minutos

Responsável por apresentar:

1. Considerações finais;
2. Síntese dos resultados;
3. Limitações;
4. Possíveis melhorias futuras.

O roteiro deve explicar:

- Qual foi o principal aprendizado do trabalho;
- Qual modelo apresentou melhor comportamento geral;
- Quais limitações foram encontradas nos dados ou modelos;
- O que poderia ser melhorado futuramente;
- Como o trabalho demonstrou o uso prático de machine learning.

---

## Regras importantes

1. O roteiro deve ser baseado nos arquivos existentes na pasta do projeto.
2. A apresentação será feita usando os notebooks Python como apoio visual, portanto o roteiro deve indicar **quais partes/células/seções do notebook devem ser mostradas** durante cada fala.
3. Não invente resultados, métricas ou conclusões que não estejam nos arquivos.
4. Quando não encontrar uma informação, marque como:

   **[PREENCHER COM RESULTADO DO NOTEBOOK/ARQUIVO]**

5. Evite overengineering.
6. A apresentação deve soar natural, como fala oral, não como texto de artigo.
7. Use linguagem acadêmica, mas simples.
8. Cada apresentador deve ter:
   - roteiro de fala;
   - indicação do trecho do notebook a ser mostrado;
   - pontos principais que não podem ser esquecidos;
   - frase de transição para o próximo apresentador.
9. O PDF deve ser gerado ao final com formatação clara, legível e organizada.

---

## Entregáveis obrigatórios

O agente deve gerar:

1. Um arquivo Markdown intermediário com o roteiro:

   `roteiro_apresentacao.md`

2. Um arquivo PDF final:

   `roteiro_apresentacao.pdf`

---

## Regras para geração do PDF

O PDF deve conter:

- Capa simples com:
  - título do trabalho;
  - subtítulo: `Roteiro de Apresentação`;
  - nomes dos apresentadores;
  - tempo total estimado.

- Sumário simples.

- Seções separadas por apresentador.

- Em cada seção:
  - tempo estimado;
  - objetivo da fala;
  - trecho do notebook a ser mostrado;
  - roteiro de fala;
  - pontos que não podem faltar;
  - transição para o próximo apresentador.

- Considerações finais.

- Linguagem em português do Brasil.

---

## Formato de saída esperado no Markdown

Gere o conteúdo no arquivo `roteiro_apresentacao.md` com a seguinte estrutura:

```md
# Roteiro de Apresentação

## Informações gerais

**Tema:** [PREENCHER COM BASE NOS ARQUIVOS]  
**Objetivo:** [PREENCHER COM BASE NOS ARQUIVOS]  
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

1. Igor — Partes 1 e 2: Dados, EDA e Targets
2. Paulo Eduardo — Target da Parte 3, Baseline e KNN
3. Rod — SVM, Random Forest e Tuning Leve
4. Jonas — Métricas e Interpretação dos Resultados
5. Gustavo Lima — Considerações Finais

---

## 1. Igor — Partes 1 e 2: Dados, EDA e Targets

### Tempo estimado

3 minutos

### Objetivo da fala

...

### Trecho do notebook a ser mostrado

- Notebook:
- Seção/célula:
- O que destacar visualmente:

### Roteiro de fala

...

### Pontos que não podem faltar

- ...
- ...

### Transição

...

---

## 2. Paulo Eduardo — Target da Parte 3, Baseline e KNN

### Tempo estimado

3 minutos

### Objetivo da fala

...

### Trecho do notebook a ser mostrado

- Notebook:
- Seção/célula:
- O que destacar visualmente:

### Roteiro de fala

...

### Pontos que não podem faltar

- ...
- ...

### Transição

...

---

## 3. Rod — SVM, Random Forest e Tuning Leve

### Tempo estimado

3 minutos

### Objetivo da fala

...

### Trecho do notebook a ser mostrado

- Notebook:
- Seção/célula:
- O que destacar visualmente:

### Roteiro de fala

...

### Pontos que não podem faltar

- ...
- ...

### Transição

...

---

## 4. Jonas — Métricas e Interpretação dos Resultados

### Tempo estimado

3 minutos

### Objetivo da fala

...

### Trecho do notebook a ser mostrado

- Notebook:
- Seção/célula:
- O que destacar visualmente:

### Roteiro de fala

...

### Pontos que não podem faltar

- ...
- ...

### Transição

...

---

## 5. Gustavo Lima — Considerações Finais

### Tempo estimado

3 minutos

### Objetivo da fala

...

### Trecho do notebook a ser mostrado

- Notebook:
- Seção/célula:
- O que destacar visualmente:

### Roteiro de fala

...

### Pontos que não podem faltar

- ...
- ...

### Fechamento

...