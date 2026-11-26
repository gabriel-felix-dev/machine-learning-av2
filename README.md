# AV2 — Classificação de variedades de trigo

Entrega de **13/11/2026**: limpeza e pré-processamento, análise exploratória (EDA) e seleção de atributos do dataset Seeds. O planejamento e a descrição do conjunto estão em [dataset-seed-versao-2.0.md](dataset-seed-versao-2.0.md).

## Executar no Google Colab

1. Abra `machine_learning_av2.ipynb` no Colab.
2. Envie `dados/dataset-seeds.txt` junto ao notebook, preservando a pasta `dados/`. Também é possível enviar `dataset-seeds.txt` ou `dataset-seeds.csv` diretamente para `/content/`.
3. Execute as células de cima para baixo. As bibliotecas usadas são `pandas`, `numpy`, `matplotlib`, `seaborn` e `scikit-learn`, disponíveis no Colab.

O notebook contém tabelas e gráficos de distribuição das classes, medidas por variedade, correlações, relação entre área e comprimento do sulco, ranking ANOVA e acurácia exploratória por número de atributos.

## Resultado da entrega

- **210 registros e 7 atributos numéricos**, com 70 amostras por classe. O TXT original e o CSV do projeto contêm os mesmos valores.
- **Nenhum registro removido**: não há valores ausentes, infinitos, duplicatas exatas ou valores fora das regras de consistência adotadas.
- **Treino estratificado:** 168 registros; **teste reservado:** 42 registros. A EDA e a seleção de atributos usam apenas o treino.
- A seleção com ANOVA e validação cruzada de 5 dobras recomendou **área, perímetro, largura do grão e comprimento do sulco** pela regra de 1 erro padrão. A acurácia exploratória média foi **0,929** com quatro ou sete atributos; a maior média, **0,946**, ocorreu com cinco ou seis atributos.

Essas acurácias orientaram a seleção de atributos. A avaliação final no teste reservado está registrada na entrega de 27/11, abaixo.

## Entrega de 20/11

A divisão 168/42 foi reproduzida. Usando apenas o treino, comparamos referência simples, regressão logística e árvore de decisão por validação cruzada e treinamos uma regressão logística com quatro atributos. O procedimento, os resultados e um roteiro de explicação estão em [entrega_20-11_seeds.md](entrega_20-11_seeds.md).

Para reproduzir com Python 3.12, crie um ambiente virtual, instale `requirements.txt` e execute `src/entrega_20_11.py`. O script grava a comparação em `resultados/`, a divisão por índice e o pipeline treinado em `modelos/`. Nessa etapa, o teste de 42 grãos foi mantido reservado para 27/11.

## Entrega de 27/11

Refinamos a regressão logística usando somente o treino e fixamos `C=10` antes de avaliar o teste reservado. O modelo acertou **38 de 42 grãos (90,48%)**; os quatro erros foram Kama. A matriz de confusão, as métricas por classe, a explicação dos erros e um roteiro para apresentar o projeto estão em [entrega_27-11_seeds.md](entrega_27-11_seeds.md).

O script `src/entrega_27_11.py` separa o refino (`refinar`) da avaliação (`avaliar`). Como os resultados finais já estão salvos, use `verificar` para conferir fonte, modelo, previsões e métricas sem alterar os artefatos:

```powershell
.\.venv\Scripts\python.exe src\entrega_27_11.py verificar
```

## Apresentação final de 04/12

A apresentação editável de oito slides está em [apresentacao/apresentacao_final.pptx](apresentacao/apresentacao_final.pptx). O [roteiro de fala](apresentacao/roteiro_04-12.md) distribui o conteúdo em **6 minutos e 35 segundos**, com margem até o limite de 7 minutos. Os slides resumem o dataset, a divisão, a escolha e o refino do modelo, o resultado no teste, os erros e as limitações. O código de geração está em `src/gerar_apresentacao.mjs`.
