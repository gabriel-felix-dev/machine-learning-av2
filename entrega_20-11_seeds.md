# Entrega de 20/11/2026 — divisão, seleção e treinamento do modelo

**Projeto:** classificação de variedades de trigo com o dataset Seeds  
**Integrantes:** Gabriel Felix — 03356520; David Ryan — 03354657  
**Branch:** `feat/entrega-20-11`

## Objetivo desta entrega

Documentar a divisão dos dados, escolher um classificador e treiná-lo. A pergunta do projeto continua sendo: **as características geométricas permitem prever a variedade de um grão de trigo?** A avaliação final no conjunto de teste e a análise dos erros ficam para 27/11. O dia 20/11 é feriado, mas o cronograma indica envio.

## 1. Divisão dos dados

O arquivo bruto `dados/dataset-seeds.txt` contém **210 grãos**, sete medidas numéricas e uma classe entre 1, 2 e 3. A auditoria feita na entrega anterior não encontrou registros que precisassem ser removidos. Reproduzimos a divisão já preparada no notebook, com `train_test_split`, **80% para treino e 20% para teste**, `random_state=42` e estratificação pela classe.

| Partição | Total | Classe 1 (Kama) | Classe 2 (Rosa) | Classe 3 (Canadian) |
| --- | ---: | ---: | ---: | ---: |
| Treino | 168 | 56 | 56 | 56 |
| Teste reservado | 42 | 14 | 14 | 14 |

Estratificar mantém as três classes igualmente representadas nas duas partições. A semente fixa torna a divisão reproduzível. Os índices de origem de cada partição estão em `resultados/particoes_20-11.csv`. **Nenhum dos 42 grãos de teste foi usado para escolher, ajustar ou medir o modelo nesta entrega.**

## 2. Seleção do modelo

Comparamos cinco candidatos usando **somente os 168 grãos de treino**: uma referência que sempre prevê a classe mais frequente, regressão logística com quatro ou sete atributos e árvore de decisão com quatro ou sete atributos. A seleção dos quatro atributos usa ANOVA (`SelectKBest`) dentro de cada dobra. Para regressão logística, a padronização também ocorre dentro do `Pipeline`, ajustada apenas com o treino da dobra. A árvore não precisa dessa padronização. A validação cruzada foi estratificada em cinco dobras, embaralhada com semente 42.

A métrica principal foi **F1 macro**, que calcula o F1 de cada classe e tira uma média com pesos iguais. Também observamos a acurácia. Os valores abaixo são **médias de validação cruzada no treino**, não resultados no teste reservado.

| Candidato | Atributos | F1 macro médio | Acurácia média |
| --- | ---: | ---: | ---: |
| Referência: classe mais frequente | 0 | 0,1644 | 0,3275 |
| Regressão logística | 4 | 0,9276 | 0,9287 |
| Regressão logística | 7 | **0,9286** | 0,9287 |
| Árvore de decisão | 4 | 0,8926 | 0,8929 |
| Árvore de decisão | 7 | 0,8984 | 0,8986 |

A maior média de F1 foi 0,9286, com regressão logística e sete atributos. Reaplicamos a **regra de 1 erro padrão** usada na entrega anterior: entre os candidatos com F1 médio de pelo menos **0,9011**, escolhemos o de menor número de atributos. As duas regressões ficaram acima desse limite; a versão com quatro atributos ficou apenas **0,0009** abaixo da média da versão com sete. Assim, escolhemos a **regressão logística com quatro atributos**, preservando a seleção de 13/11. Essa regra é uma preferência por simplicidade diante da variação entre dobras, não uma prova de equivalência estatística. Os valores por candidato estão em `resultados/validacao_20-11.csv`.

## 3. Treinamento realizado

Após a escolha, ajustamos um novo `Pipeline` com **todos os 168 grãos de treino**. Ele executa, nesta ordem:

1. ANOVA para selecionar quatro atributos;
2. `StandardScaler` para padronizar as medidas selecionadas;
3. `LogisticRegression(max_iter=2000, random_state=42)` para aprender a associação entre medidas e classes.

Os quatro atributos selecionados no treino completo foram **área, perímetro, largura do grão e comprimento do sulco**. O pipeline treinado está em `modelos/modelo_20-11.joblib`. A acurácia nos próprios dados usados para ajustá-lo foi **0,9405 (158/168)**; esse valor apenas confirma o ajuste e **não mede o desempenho em grãos reservados ou novos**. Os parâmetros, versões e resumo da execução estão em `resultados/treinamento_20-11.json`.

A escolha de quatro atributos começou na análise exploratória de 13/11, com os mesmos dados de treino. Por isso, as médias de validação desta entrega servem para **selecionar** o modelo e podem ser otimistas como estimativa independente de desempenho. Em 27/11, o refinamento deve usar apenas o treino; depois de fixada a configuração final, o teste reservado pode ser aberto uma vez para a avaliação e a análise dos erros.

## Como reproduzir

Com Python 3.12, na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\entrega_20_11.py
```

O script lê o TXT bruto, valida dimensões e classes, reproduz a divisão, compara os candidatos e grava os arquivos em `resultados/` e `modelos/`. A versão usada nesta execução foi Python 3.12.14, pandas 3.1.1 e scikit-learn 1.9.1. A divisão, a escolha e o treinamento podem ser repetidos sem consultar o conjunto de teste.

## Como explicar o projeto na apresentação

> Temos 210 medidas de grãos de três variedades. Separei 168 grãos para aprender e escolher o modelo e reservei 42 para uma avaliação posterior. Mantive 56 exemplos de cada variedade no treino e 14 no teste, para que nenhuma classe ficasse desfavorecida. Comparei uma regra simples, regressão logística e árvore de decisão usando cinco divisões internas do treino. A regressão logística teve os melhores resultados de validação. Como quatro atributos tiveram resultado muito próximo de sete, escolhi a versão mais simples, com área, perímetro, largura e comprimento do sulco. Treinei essa versão com os 168 grãos de treino. Ainda não medi o resultado nos 42 grãos reservados; isso será feito após o refinamento da próxima entrega.

**Se perguntarem por que separar treino e teste:** o treino serve para aprender e tomar decisões; o teste reservado serve para conferir, ao final, como o modelo se comporta em exemplos que não participaram dessas decisões.

**Se perguntarem por que F1 macro:** ele dá a mesma importância às três variedades e combina precisão e recuperação de cada classe. A acurácia mostra a proporção total de acertos.

**Se perguntarem por que quatro atributos:** a diferença de F1 médio para sete foi pequena na validação, e a regra de 1 erro padrão favoreceu o modelo com menos medidas. Isso também mantém a recomendação obtida em 13/11.

**Se perguntarem se o modelo já está aprovado:** ainda não. Os números desta entrega vêm da validação dentro do treino. A avaliação final com matriz de confusão e análise dos erros pertence à entrega de 27/11.
