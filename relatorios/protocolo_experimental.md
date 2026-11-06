# Protocolo fixado antes da execução

Execução antecipada em 06/11/2026. Marcos acadêmicos: 13/11, 20/11, 27/11 e 04/12/2026.

1. Preservar o SHA-256 do bruto. Validar 210 linhas, oito campos numéricos, finitos, sete medidas positivas, compacidade entre 0 e 1 e classes 1, 2, 3. Interromper se houver falhas de esquema, ausências ou duplicatas em X. Não excluir extremos sem evidência de erro.
2. Divisão estratificada 80/20, `random_state=42`. EDA que orienta decisões somente nos 168 registros de treino. Teste de 42 registros reservado até congelar a configuração final.
3. Referência `DummyClassifier(strategy='most_frequent')`. Em empate a implementação escolhe o menor código. Árvores iniciais: todos os sete atributos e `SelectKBest(f_classif, k=3)`, com Gini e `random_state=42`.
4. Comparações de desenvolvimento: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` exclusivamente no treino. Seletor dentro de `Pipeline`, reajustado em cada fold. Métrica principal: F1 macro. Acurácia como métrica secundária. Sem normalização para árvores.
5. Refinamento por grade: k em [2,3,4,5,6,'all'], profundidade em [2,3,4,5,None], folhas mínimas em [1,2,4,6], `ccp_alpha` em [0,0.01]. Total: 240 configurações, cinco folds. Empates de F1 macro até 1e-12: maior acurácia, menos atributos, menor profundidade, maior folha mínima e maior poda. Este desempate não é a regra de um erro padrão.
6. Congelar parâmetros e modelo antes de prever o teste. Avaliar a referência, as duas árvores iniciais e a final no mesmo teste, como comparação descritiva predefinida. Nenhuma escolha posterior depende dessas métricas. Não repetir sementes em busca de melhor resultado.
7. Registrar acurácia, precisão, recall, F1, suporte, F1 macro, matriz de confusão, previsões e todos os erros com linha de origem. Intervalo de Wilson de 95% para a acurácia final é apenas uma medida aproximada da incerteza desse pequeno teste.
8. Exportar pipeline treinado em 168 registros para inferência local em lote. Não retreinar com teste. Monitoramento fica como plano operacional, pois não há novos lotes nem rótulos de produção.

As médias de CV da busca são critérios de escolha e podem ser otimistas por seleção entre várias configurações. O teste reservado fornece a avaliação final. A origem experimental limitada não permite afirmar desempenho universal ou causalidade.
