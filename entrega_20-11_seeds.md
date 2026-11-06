# Entrega de 20/11/2026 - Divisão, escolha e treinamento

Material preparado antecipadamente em 06/11/2026. A data no título identifica o marco do cronograma, não uma execução futura já ocorrida. Não houve envio à plataforma da disciplina.

**Há envio previsto em 20/11, apesar do feriado.**

## Procedimento e resultados observados

A divisão estratificada 80/20, semente 42, precede EDA e seleção supervisionada. São 168 exemplos de treino (56 por classe) e 42 de teste (14 por classe). Validação cruzada estratificada de cinco folds, com embaralhamento e semente 42, usa apenas treino. O seletor SelectKBest com ANOVA f_classif fica no Pipeline e reaprende as colunas em cada fold. Não há normalização no classificador de árvore, imputação ou reamostragem. As classes já estão equilibradas. Os códigos 1, 2, 3 são categorias, sem ordem quantitativa.

O pandas prepara X e y. O scikit-learn realiza divisão, seleção, treinamento e avaliação. A árvore representa relações não lineares com regras explicáveis e atende ao plano inicial. Referência: `DummyClassifier(strategy='most_frequent')`. Árvores iniciais: Gini, profundidade irrestrita, folha mínima 1, semente 42, todos os atributos ou k=3 selecionados dentro do fold. Em folds com frequências ligeiramente diferentes, a referência pode prever outra classe majoritária.

| Modelo | Acurácia CV | F1 macro CV | DP F1 macro |
| --- | --- | --- | --- |
| Referência simples | 32,75% | 0,1644 | 0,0018 |
| Árvore inicial (7) | 89,86% | 0,8984 | 0,0406 |
| Árvore inicial (k=3) | 83,33% | 0,8340 | 0,0488 |
| Árvore refinada | 92,26% | 0,9231 | 0,0527 |

Nesta etapa, os três primeiros modelos constituem a comparação inicial. A linha refinada consolida o trabalho de 27/11. A árvore com sete atributos superou a versão k=3 em validação. As duas árvores iniciais alcançaram 100% no treino interno, mas ficaram abaixo disso na validação, evidenciando necessidade de controlar complexidade. As médias de acurácia são médias não ponderadas entre folds de 33 ou 34 exemplos.

Não consultamos o teste para escolher o modelo. Os resultados finais dos quatro modelos constam da entrega de 27/11, calculados após congelar a configuração refinada.

## Arquivos produzidos

`src/analise_seeds.py`, `requirements.txt`, `resultados/distribuicao_particoes.csv`, `resultados/folds_validacao.csv`, `resultados/comparacao_folds.csv`, `resultados/comparacao_validacao.csv` e `relatorios/protocolo_experimental.md`.

## Próximos passos do cronograma

Em 27/11, ajustar profundidade, tamanho mínimo de folha, poda e quantidade de atributos só com treino, congelar a configuração e abrir o teste para avaliação final e análise dos erros.
