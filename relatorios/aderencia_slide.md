# Conferência do slide e adequações do plano

Material: `slide-machine-learning.pdf`, 130 páginas. Consulta da página física 10 à 130, incluindo o conteúdo visual das páginas sem texto sobre PCA/LDA. O arquivo foi preservado.

| Página | Orientação verificada | Aplicação no Seeds |
| --- | --- | --- |
| 52 e 130 | Ciclo completo inclui definição, coleta, preparação, modelagem, avaliação, implantação e monitoramento | Acrescentar exportação Joblib, inferência local em lote e plano de monitoramento à entrega de 04/12. Não afirmar implantação em produção real. |
| 55-60, 64-65 | Conferir faltantes, duplicatas, inconsistências, extremos e escalas | Auditar esquema e tipos. Investigar extremos via IQR do treino sem remover automaticamente. Não padronizar a árvore, que usa cortes em cada atributo. |
| 66-67 | EDA, engenharia, seleção e redução de atributos | Histogramas, boxplots, dispersão e correlação no treino. Seleção de colunas originais por ANOVA. PCA e LDA são opções explicadas no material, não requisitos universais. |
| 68-70 e 81 | Teste somente após o modelo pronto, validação para ajustes | Dividir antes da EDA orientada a decisões e da seleção supervisionada. Validação estratificada de cinco folds só no treino. Seleção dentro do Pipeline em cada fold. |
| 74 | Comparação com referência simples e múltiplas métricas | Dummy que prevê a classe mais frequente, duas árvores iniciais e árvore refinada. F1 macro escolhe ajustes. |
| 77-79 | Acurácia, precisão, recall, F1, matriz de confusão e ROC/AUC | Métricas por classe e matriz para cada modelo. ROC um-contra-resto e AUC macro complementares para a árvore final. Métricas de regressão e clustering não se aplicam. |
| 82-86 e 96 | Identificar sobreajuste e ajustar hiperparâmetros | Comparar treino/validação e testar profundidade, folha mínima, poda e número de atributos por grade. Não forçar melhora no teste. |
| 97 | Implantação pode usar modelos serializados ou processamento em lote | Pipeline serializado e `src/prever.py`, com demonstração local. |
| 98 | Monitorar qualidade, desempenho, drift e retreinar quando necessário | Referência estatística do treino salva e plano com indicadores, revisão e nova validação. Sem inventar medições de produção. |

## Diferenças em relação ao plano inicial

O roteiro de 06/11 terminava na comunicação. A consulta acrescentou implantação local e planejamento de monitoramento. O slide apresenta EDA/engenharia antes da divisão em seu esquema geral. A execução antecipa a divisão para respeitar a instrução explícita de evitar vazamento. As comparações de 20/11 usam validação cruzada, e a leitura dos resultados de teste ocorre apenas depois do congelamento da configuração em 27/11.

O slide descreve conteúdos e boas práticas, sem estabelecer aqui uma obrigação de usar todos os algoritmos apresentados. Por isso mantemos a árvore definida no projeto, a comparação com referência e o subconjunto selecionado. Não há necessidade de AutoML, séries temporais, clustering ou redes neurais para esta pergunta.
