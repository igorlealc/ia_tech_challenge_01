# Prompt Padrão - Projeto

Use este prompt como base para manter o padrão técnico, analítico e narrativo do projeto inteiro.

```text
Contexto do projeto
Estamos desenvolvendo um Tech Challenge de Machine Learning com base em dados do DATASUS (SIH/SUS RJ 2025).
O pipeline do projeto é:
DBC -> DBF -> Parquet -> 2025_consolidado.parquet -> 2025_reduzido.parquet -> 2025_tratado.parquet

Objetivo geral
Construir análises e modelos aderentes ao material estudado na pós, mantendo coerência entre:
- preparação dos dados
- escolha das variáveis
- escolha dos algoritmos
- critérios de avaliação
- interpretação final

Princípios do projeto
1. Sempre partir do pipeline oficial:
   DBC -> DBF -> Parquet -> consolidado -> reduzido -> tratado

2. Sempre explicitar a origem da base usada em cada etapa:
   - 2025_consolidado.parquet
   - 2025_reduzido.parquet
   - 2025_tratado.parquet

3. Sempre justificar por que cada transformação foi feita.
   Não apenas mostrar o código, mas explicar:
   - o problema que a transformação resolve
   - o impacto esperado na análise ou no modelo

Padrão para tratamento de dados
4. Antes de modelar, fazer inspeção mínima da base:
   - dimensões
   - tipos de dados
   - nulos
   - distribuição inicial

5. Ao selecionar variáveis:
   - priorizar colunas relevantes ao problema
   - evitar vazamento de target
   - justificar exclusões por alta cardinalidade, irrelevância ou risco metodológico

6. Ao tratar base desbalanceada:
   - usar split com stratify quando houver target
   - considerar class_weight='balanced' em classificadores apropriados
   - não confiar apenas em accuracy

Padrão para modelagem
7. Em problemas supervisionados:
   - separar treino e teste
   - usar Pipeline e ColumnTransformer quando houver pré-processamento
   - aplicar StandardScaler em modelos sensíveis à escala, como KNN, PCA, SVM e Regressão Logística
   - aplicar encoding apropriado para categóricas

8. Escolher modelos aderentes ao conteúdo estudado.
   Exemplos alinhados às aulas:
   - Regressão Linear
   - Regressão Logística
   - KNN
   - SVM
   - Decision Tree
   - Random Forest
   - KMeans
   - DBSCAN
   - PCA

9. Se houver tuning, ele deve ser simples, explícito e justificável.
   Exemplos:
   - testar alguns valores de k no KNN
   - ajustar threshold em classificadores probabilísticos
   - usar validação cruzada para comparar modelos

Padrão para avaliação
10. Em regressão, priorizar métricas como:
   - R²
   - MAE
   - RMSE
   - MAPE, quando fizer sentido

11. Em classificação, priorizar:
   - accuracy
   - precision
   - recall
   - F1-score
   - matriz de confusão

12. Quando o modelo retornar probabilidade, incluir:
   - ROC
   - AUC
   - discussão de threshold

13. Quando possível, complementar com:
   - validação cruzada
   - comparação entre configurações e modelos

Padrão de interpretação
14. A interpretação final nunca deve ser só numérica.
   Explicar:
   - o que o resultado significa
   - qual métrica é mais relevante para o problema
   - quais trade-offs apareceram

15. Em contexto de saúde:
   - destacar quando falso negativo é mais grave que falso positivo
   - justificar priorização de recall quando a detecção de casos positivos for o objetivo

16. Se a base for fortemente desbalanceada:
   - explicar por que a accuracy pode enganar
   - discutir a relação entre recall, precision e volume de falsos positivos

Padrão de narrativa
17. Contar a história da etapa sempre nesta ordem:
   - qual era o objetivo
   - qual era a base utilizada
   - quais transformações foram feitas
   - por que essas transformações foram necessárias
   - quais modelos foram escolhidos
   - como foram avaliados
   - qual resultado foi obtido
   - qual conclusão faz mais sentido para o problema

18. Manter o texto técnico, claro e aderente às aulas.
   Evitar:
   - soluções fora do conteúdo estudado sem justificativa
   - uso de métricas sem interpretação
   - comparações sem critério

Entregáveis esperados
- notebooks organizados em seções claras
- código reprodutível
- explicação do racional técnico
- comparação entre abordagens
- interpretação final coerente com o domínio
- documentação atualizada no README quando a estrutura do projeto mudar
```
