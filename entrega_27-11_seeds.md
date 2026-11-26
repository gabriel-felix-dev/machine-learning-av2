# Entrega de 27/11/2026 — refino do modelo e análise dos erros

**Projeto:** classificação de variedades de trigo com o dataset Seeds  
**Integrantes:** Gabriel Felix — 03356520; David Ryan — 03354657  
**Branch:** `feat/entrega-27-11`

Material preparado antecipadamente em 26/11/2026 para o marco de 27/11/2026.

## Objetivo e continuidade

Na entrega de 20/11, separamos 168 grãos para treino e 42 para teste e escolhemos uma regressão logística com quatro atributos. Nesta entrega, ajustamos a intensidade de regularização desse mesmo modelo **usando apenas o treino**. Depois de fixar e salvar a configuração, avaliamos o modelo nos 42 grãos reservados e examinamos os erros. Não usamos o resultado do teste para fazer novos ajustes.

## 1. Refino antes de abrir o teste

Mantivemos a divisão estratificada de 80/20, a semente 42 e os mesmos quatro atributos selecionados por ANOVA: **área, perímetro, largura do grão e comprimento do sulco**. O pipeline continua com seleção de atributos, padronização e regressão logística. Dentro de cada dobra de validação, seleção e padronização são ajustadas apenas com o treino daquela dobra.

Testamos `C` em **0,01; 0,1; 1; 10; 100** por validação cruzada estratificada de cinco dobras nos 168 grãos de treino. `C` controla a regularização: valores menores impõem uma penalidade mais forte aos coeficientes; valores maiores deixam o modelo se ajustar mais aos dados. A métrica principal foi F1 macro, que dá peso igual às três classes.

| C | F1 macro médio na validação | Acurácia média na validação |
| ---: | ---: | ---: |
| 0,01 | 0,8822 | 0,8868 |
| 0,1 | 0,9097 | 0,9111 |
| 1 (entrega de 20/11) | 0,9276 | 0,9287 |
| **10 (escolhido)** | **0,9462** | **0,9465** |
| 100 | 0,9402 | 0,9405 |

Aplicamos a regra de 1 erro padrão: o limite calculado a partir da maior média foi **0,9284**. `C=10` e `C=100` ficaram acima desse limite; escolhemos **C=10**, que mantém regularização mais forte entre os dois. `C=1` ficou ligeiramente abaixo do limite. O ganho de F1 médio de `C=1` para `C=10` foi **0,0185** na validação do treino. Isso orientou o ajuste, mas não prova um ganho em novos grãos.

A configuração foi registrada em `resultados/configuracao_27-11.json` e o pipeline treinado com os 168 grãos de treino foi salvo em `modelos/modelo_27-11.joblib` **antes** da avaliação final. O arquivo de configuração guarda o SHA-256 do modelo para conferir que ele não mudou. A tabela completa está em `resultados/refino_27-11.csv`.

## 2. Avaliação final no teste reservado

Com a configuração fixada, abrimos os **42 grãos de teste**. O modelo acertou **38 de 42**: **acurácia de 90,48%** e **F1 macro de 0,9007**. A referência simples que sempre prevê uma classe acertaria 14 de 42 (33,33%), pois há 14 grãos de cada classe no teste. A hipótese operacional de superar essa regra simples foi sustentada **nesta divisão dos dados**. Não avaliamos o modelo antigo de `C=1` no teste, portanto não afirmamos que o refino melhorou o desempenho de teste em relação a ele.

Matriz de confusão — **linhas = classe real; colunas = classe prevista**:

| Real / prevista | Kama | Rosa | Canadian |
| --- | ---: | ---: | ---: |
| **Kama** | 10 | 1 | 3 |
| **Rosa** | 0 | 14 | 0 |
| **Canadian** | 0 | 0 | 14 |

| Classe | Precisão | Recall | F1 | Grãos no teste |
| --- | ---: | ---: | ---: | ---: |
| Kama | 100,00% | 71,43% | 0,8333 | 14 |
| Rosa | 93,33% | 100,00% | 0,9655 | 14 |
| Canadian | 82,35% | 100,00% | 0,9032 | 14 |

**Como ler:** o modelo encontrou todos os Rosa e Canadian reais, mas reconheceu apenas 10 dos 14 Kama. A precisão de Kama é 100% porque todos os grãos que ele chamou de Kama eram Kama; isso não significa que ele encontrou todos os Kama. As previsões completas, a matriz e as métricas por classe estão em `resultados/`.

## 3. Análise dos quatro erros

Todos os erros são **Kama previstos como outra variedade**. A coluna “escore previsto” é a probabilidade fornecida pela regressão logística para a classe escolhida; esses valores **não foram calibrados**, então não devem ser tratados como certeza.

| Linha do arquivo bruto | Classe prevista | Área | Largura | Comprimento do sulco | Escore previsto |
| ---: | --- | ---: | ---: | ---: | ---: |
| 24 | Canadian | 12,08 | 2,936 | 4,961 | 0,9682 |
| 38 | Rosa | 17,08 | 3,683 | 5,484 | 0,8076 |
| 61 | Canadian | 11,42 | 2,850 | 4,607 | 0,9366 |
| 62 | Canadian | 11,23 | 2,879 | 4,703 | 0,9970 |

Para contextualizar, no **treino**, a mediana de área e largura foi **14,405 e 3,258** em Kama, **18,785 e 3,694** em Rosa e **11,825 e 2,828** em Canadian. Os Kama das linhas 24, 61 e 62 têm área e largura mais próximas dos valores centrais Canadian; o da linha 38 tem medidas de tamanho mais próximas das Rosa. Isso ajuda a descrever a confusão observada, mas não demonstra a causa de cada erro. Não há evidência aqui de rótulos errados, defeitos nos grãos ou causas biológicas. Os detalhes dos quatro casos estão em `resultados/erros_27-11.csv`.

## Limitações e próximo passo

O teste tem apenas **42 grãos**, sendo 14 por variedade. Cada erro muda a acurácia total em cerca de **2,38 pontos percentuais**. A validação cruzada foi usada para escolher `C`, por isso sua melhor média pode ser otimista. O resultado final vem de uma única divisão do dataset Seeds; não garante o mesmo desempenho em outra safra, origem ou forma de medição. O teste já foi consultado: qualquer novo ajuste precisaria de uma avaliação independente para sustentar uma nova afirmação de desempenho.

Para a apresentação de 04/12, usar a matriz de confusão, explicar que a principal dificuldade foi reconhecer Kama e concluir que o modelo superou a referência simples nesta amostra, com essas limitações.

## Arquivos e reprodução

| Arquivo | Conteúdo |
| --- | --- |
| `src/entrega_27_11.py` | Refino, avaliação e verificação dos resultados |
| `resultados/refino_27-11.csv` | Comparação dos cinco valores de `C` no treino |
| `resultados/configuracao_27-11.json` | Configuração fixada antes do teste |
| `modelos/modelo_27-11.joblib` | Pipeline treinado |
| `resultados/previsoes_teste_27-11.csv` | Previsões dos 42 grãos |
| `resultados/erros_27-11.csv` | Quatro casos classificados incorretamente |
| `resultados/matriz_confusao_27-11.csv` | Contagens por classe real e prevista |
| `resultados/metricas_por_classe_27-11.csv` | Precisão, recall e F1 por variedade |
| `resultados/resumo_teste_27-11.json` | Resumo da avaliação final |

Com Python 3.12 e as dependências de `requirements.txt`, os comandos usados na primeira execução foram:

```powershell
.\.venv\Scripts\python.exe src\entrega_27_11.py refinar
.\.venv\Scripts\python.exe src\entrega_27_11.py avaliar
```

Depois que os resultados foram gravados, o script bloqueia novo refino e nova avaliação para evitar ajustes motivados pelo teste. Para **conferir** os artefatos já salvos, use:

```powershell
.\.venv\Scripts\python.exe src\entrega_27_11.py verificar
```

Essa verificação confere fonte, modelo, previsões e métricas sem modificar os resultados.

## Como explicar o projeto

> Na entrega anterior, escolhemos a regressão logística com quatro medidas do grão e separamos 42 exemplos para o teste final. Agora testamos cinco intensidades de regularização usando apenas os outros 168 exemplos, em validação cruzada. `C=10` teve o melhor F1 macro médio, então fixamos e salvamos esse modelo antes de olhar o teste. No teste, ele acertou 38 de 42 grãos, ou 90,48%. A matriz mostra que os quatro erros foram grãos Kama: três confundidos com Canadian e um com Rosa. As medidas desses grãos se parecem, em parte, com as medidas típicas das classes previstas. O modelo superou a regra simples de prever sempre uma classe, mas o teste é pequeno e não permite garantir o mesmo resultado em grãos de outras origens.

**Se perguntarem o que é o refino:** ajustamos `C`, que controla a força da regularização da regressão logística. A escolha foi feita no treino, sem usar os 42 exemplos reservados.

**Se perguntarem por que a acurácia do teste é menor que a da validação:** são amostras diferentes. Além disso, escolhemos `C` pelos resultados da validação, o que pode tornar a melhor média de validação otimista.

**Se perguntarem qual classe foi mais difícil:** Kama teve recall de 71,43%, pois quatro dos seus 14 grãos foram previstos como outra variedade.

**Se perguntarem se podemos corrigir esses quatro erros e medir de novo no mesmo teste:** podemos estudar os casos, mas um modelo ajustado após vê-los precisaria de **outro conjunto independente** para uma nova avaliação justa.
