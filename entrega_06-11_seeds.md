# Projeto AV2 — Entrega de 06/11/2026

## Identificação

**Tema:** classificação de variedades de trigo por características geométricas dos grãos  
**Dataset:** Seeds  
**Integrante(s):** Gabriel Felix

## T1 — Escolha e coleta do dataset

O dataset escolhido é o **Seeds**, disponibilizado pelo [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/236/seeds). Ele reúne medidas geométricas de **210 grãos de trigo**, pertencentes a três variedades: **Kama, Rosa e Canadian**, com **70 amostras de cada variedade**. As medidas já foram extraídas pelos responsáveis pela pesquisa; este projeto usará a tabela numérica, sem processamento de imagens.

O [arquivo original](https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt) foi coletado em 06/11/2026 e está salvo em [`dados/seeds_dataset.txt`](dados/seeds_dataset.txt). A conferência inicial confirmou **210 linhas**, **oito valores por linha** (sete atributos e uma classe), todos numéricos, com **70 registros em cada uma das classes 1, 2 e 3**. A ficha da UCI informa que o conjunto não possui valores ausentes. A verificação detalhada de consistência e possíveis duplicatas fará parte da próxima entrega.

| Posição | Variável | Papel |
| --- | --- | --- |
| 1 | Área do grão | Atributo de entrada |
| 2 | Perímetro do grão | Atributo de entrada |
| 3 | Compacidade | Atributo de entrada |
| 4 | Comprimento do grão | Atributo de entrada |
| 5 | Largura do grão | Atributo de entrada |
| 6 | Coeficiente de assimetria | Atributo de entrada |
| 7 | Comprimento do sulco do grão | Atributo de entrada |
| 8 | Classe (1, 2 ou 3) | Variável alvo |

Cada linha representa um grão de trigo. A variável alvo identifica sua variedade; os outros sete valores descrevem sua geometria. A tarefa escolhida é **classificação supervisionada com três classes**.

## T2 — Problema, pergunta e hipótese

**Problema:** identificar a variedade de um grão de trigo a partir de suas medidas geométricas.

**Pergunta de pesquisa:** *As sete características geométricas do dataset Seeds permitem prever a variedade de um grão de trigo?*

**Hipótese:** *Um modelo treinado com essas características conseguirá classificar os grãos com desempenho superior ao de uma regra simples que sempre prevê uma única classe.* Como as três classes têm a mesma quantidade de registros, essa regra simples acertaria aproximadamente **33,3%** das amostras.

**Objetivo:** construir e avaliar um modelo que receba as sete medidas de um grão e produza uma previsão para sua classe. O resultado será avaliado com acurácia e matriz de confusão, para mostrar também quais classes são confundidas.

## T3 — Plano do ciclo de vida do projeto de machine learning

| Etapa | Aplicação no projeto | Entrega prevista |
| --- | --- | --- |
| Definição do problema e coleta | Escolher o Seeds, formular pergunta e hipótese, identificar entradas e alvo e obter o arquivo original. | 06/11 |
| Limpeza e pré-processamento | Conferir leitura, tipos, valores ausentes, duplicatas e consistência dos registros. | 13/11 |
| Análise exploratória (EDA) | Comparar distribuições das medidas entre as três classes e examinar relações entre atributos. | 13/11 |
| Seleção de atributos | Investigar quais medidas contribuem mais e comparar o uso de todos os atributos com um subconjunto. | 13/11 |
| Divisão dos dados e modelagem | Separar treino e teste preservando as três classes; escolher e treinar um classificador inicial, como uma árvore de decisão. | 20/11 (envio no feriado) |
| Refinamento e análise de erros | Ajustar o modelo e analisar a matriz de confusão e os exemplos classificados incorretamente. | 27/11 |
| Comunicação dos resultados | Apresentar método, resultados, limitações e resposta à pergunta inicial. | 04/12 |

**Cuidado metodológico:** embora a divisão dos dados seja apresentada na entrega de 20/11, ela será feita antes de qualquer seleção de atributos que utilize os rótulos das classes. O conjunto de teste ficará reservado para a avaliação final.

**Tecnologia prevista para executar o plano:** Python com a biblioteca `pandas` para leitura, preparação e análise dos dados; `scikit-learn` para a divisão dos dados, o treinamento da árvore de decisão e a avaliação das previsões. Assim, `pandas` participa da preparação dos dados de treino, enquanto o treinamento do modelo é feito pelo classificador do `scikit-learn`.

## Fonte e referência

Charytanowicz, M., Niewczas, J., Kulczycki, P., Kowalski, P., & Lukasik, S. (2010). *Seeds* [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C5H30K>

Página oficial: <https://archive.ics.uci.edu/dataset/236/seeds>  
Arquivo de dados: <https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt>
