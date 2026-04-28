# Prompt Padrão - Parte 6

Use este prompt como base para manter o padrão da Parte 6 do projeto.

```text
Contexto do projeto
Estamos desenvolvendo um Tech Challenge de Machine Learning com base em dados do DATASUS (SIH/SUS RJ 2025).
O pipeline do projeto é:
DBC -> DBF -> Parquet -> 2025_consolidado.parquet -> 2025_reduzido.parquet -> 2025_tratado.parquet

Minha responsabilidade é a Parte 6, voltada para classificação supervisionada.

Objetivo
Implementar uma etapa de classificação supervisionada para detectar indícios de câncer de mama a partir da base tratada.

Requisitos funcionais
1. Criar o target binário:
   TARGET = (CANCER_MAMA_NIVEL > 0)
   0 = sem indício
   1 = com indício

2. Selecionar features sem vazamento de target.
   Evitar colunas diagnósticas diretamente relacionadas à resposta, como:
   - CANCER_MAMA_NIVEL
   - DIAG_PRINC
   - DIAGSEC*
   - CID_MORTE
   - DIAG_PRINC_GRUPO

3. Usar separação treino/teste com stratify:
   train_test_split(..., stratify=y)

4. Aplicar pré-processamento com Pipeline e ColumnTransformer:
   - numéricas: SimpleImputer + StandardScaler
   - categóricas: SimpleImputer + OneHotEncoder

5. Comparar modelos alinhados às aulas:
   - Logistic Regression como baseline
   - KNN com ajuste simples de k
   - Random Forest como modelo baseado em árvores

6. Mitigar o desbalanceamento da classe positiva:
   - usar class_weight='balanced' ou equivalente quando fizer sentido
   - priorizar recall

7. Ajustar threshold de modelos probabilísticos com critério objetivo:
   - usar validação
   - preferir precision_recall_curve ou critério claramente justificado
   - não escolher threshold no chute

8. Avaliar com:
   - accuracy
   - precision
   - recall
   - F1-score
   - matriz de confusão
   - validation cross score
   - ROC e AUC quando o modelo retornar probabilidade

9. Considerar o contexto de saúde:
   - falso negativo é mais grave que falso positivo
   - a narrativa deve justificar a priorização de recall

10. Se houver restrição de RAM no Colab:
   - limitar categorias de alta cardinalidade
   - amostrar o treino do KNN de forma estratificada

Entregáveis esperados
- Notebook organizado em seções claras
- Comparativo final entre os modelos
- Explicação do racional das escolhas
- Interpretação final aderente ao contexto de saúde

Tom esperado
- técnico
- objetivo
- aderente às aulas da pós
- sem usar modelos fora do conteúdo estudado, salvo justificativa explícita
```
