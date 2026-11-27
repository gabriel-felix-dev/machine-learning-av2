# Projeto AV2 — Versão 1.0 (atualizada em 13/11/2026)

## Identificação

**Tema:** Classificação de variedades de trigo por características geométricas dos grãos  
**Dataset:** Seeds  
**Integrantes:** Gabriel Felix - 03356520, David Ryan - 03354657

**Notebook Google Colab:** [machine-learning-av2](https://colab.research.google.com/drive/1mnFHxz7e_JAl_LBnGD1dD0bZfN9cPtuL?usp=sharing)

**Repositório Github:** [machine-learning-av2](https://github.com/gabriel-felix-dev/machine-learning-av2.git)

## T1 — Escolha e coleta do dataset

O dataset escolhido é o **Seeds**, disponibilizado pelo [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/236/seeds). Ele reúne medidas geométricas de **210 grãos de trigo**, pertencentes a três variedades: **Kama, Rosa e Canadian**, com **70 amostras de cada variedade**. As medidas já foram extraídas pelos responsáveis pela pesquisa; este projeto usará a tabela numérica, sem processamento de imagens.

O [arquivo original](https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt) foi coletado em 06/11/2026 e está salvo em [`dados/dataset-seeds.txt`](dados/dataset-seeds.txt). Para facilitar a leitura e a análise, os mesmos dados também estão disponíveis em [`dados/dataset-seeds.csv`](dados/dataset-seeds.csv), com cabeçalho, colunas separadas por ponto e vírgula (`;`) e ponto (`.`) como separador decimal. A conferência inicial confirmou **210 registros**, **oito valores por registro** (sete atributos e uma classe), todos numéricos, com **70 registros em cada uma das classes 1, 2 e 3**. O CSV possui ainda uma linha de cabeçalho. Na entrega de 13/11, os dois arquivos foram comparados e a auditoria de consistência foi concluída.

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

| Etapa | Aplicação no projeto | Data | Situação em 13/11 |
| --- | --- | --- | --- |
| Definição do problema e coleta | Escolher o Seeds, formular pergunta e hipótese, identificar entradas e alvo e obter o arquivo original. | 06/11 | Concluída |
| Limpeza e pré-processamento | Conferir leitura, tipos, valores ausentes, duplicatas e consistência dos registros; separar treino e teste. | 13/11 | Concluída |
| Análise exploratória (EDA) | Comparar distribuições das medidas entre as três classes e examinar relações entre atributos. | 13/11 | Concluída no treino |
| Seleção de atributos | Investigar quais medidas contribuem mais e comparar o uso de todos os atributos com um subconjunto. | 13/11 | Concluída no treino |
| Divisão, seleção e treinamento | Documentar a divisão dos dados já preparada em 13/11, selecionar o modelo com os dados de treino e treiná-lo. | 20/11 (feriado; envio indicado no cronograma) | Pendente |
| Refino do modelo e análise do erro | Ajustar o modelo, avaliá-lo e examinar a matriz de confusão e os exemplos classificados incorretamente. | 27/11 | Pendente |
| Apresentação final | Apresentar método, resultados, limitações e resposta à pergunta inicial. | 04/12 | Pendente |

## T4 — Limpeza e pré-processamento (13/11)

O [notebook da entrega](machine_learning_av2.ipynb) lê o TXT original ou o CSV do projeto. Os dois arquivos contêm os mesmos **210 registros** e **oito colunas**. A auditoria converte as colunas em números e verifica valores ausentes, texto inesperado, infinitos, duplicatas exatas, classes fora de 1–3, medidas não positivas e compacidade fora do intervalo de 0 a 1. **Nenhum registro foi removido** e não houve necessidade de imputação.

Os dados foram separados de forma estratificada, com semente 42: **168 registros de treino** (56 por classe) e **42 de teste** (14 por classe). O teste ficou reservado. A padronização usada na comparação de atributos é ajustada dentro de cada dobra da validação cruzada, somente com os dados de treino daquela dobra.

## T5 — Análise exploratória dos dados (13/11)

A EDA usa apenas os registros de treino. Foram produzidos gráficos de contagem por variedade, boxplots e histogramas das sete medidas, mapa de correlações, dispersão entre área e comprimento do sulco e mapa das médias por variedade em unidades de desvio padrão.

No treino, **Rosa** apresentou as maiores médias de área, perímetro, comprimento e largura do grão e comprimento do sulco. **Canadian** apresentou as menores médias dessas medidas e o maior coeficiente de assimetria. A correlação entre área e perímetro foi aproximadamente **0,99**, indicando forte redundância entre essas duas medidas. Os boxplots mostram valores extremos plausíveis, que não foram removidos automaticamente.

## T6 — Seleção de atributos (13/11)

O teste F da ANOVA foi aplicado somente ao treino para ordenar os atributos. A comparação de subconjuntos de **1 a 7 atributos** usou regressão logística como referência exploratória e validação cruzada estratificada de cinco dobras; em cada dobra, a seleção e a padronização foram refeitas no pipeline. O notebook inclui o gráfico do ranking ANOVA e o gráfico da acurácia média por quantidade de atributos, com o desvio entre dobras.

A maior acurácia média exploratória foi **0,946** com cinco ou seis atributos. Pela regra de 1 erro padrão, o subconjunto mais simples dentro do limite foi o de **quatro atributos: área, perímetro, largura do grão e comprimento do sulco**. Ele obteve média **0,929**, igual à média com os sete atributos. Esses resultados orientam a seleção e **não representam desempenho final**: a escolha de `k` pode tornar a estimativa otimista, e a avaliação no teste reservado está planejada para a entrega de 27/11.

## Fonte e referência

Charytanowicz, M., Niewczas, J., Kulczycki, P., Kowalski, P., & Lukasik, S. (2010). *Seeds* [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C5H30K>

Página oficial: <https://archive.ics.uci.edu/dataset/236/seeds>  
Arquivo de dados: <https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt>
