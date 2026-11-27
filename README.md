# AV2 — Classificação de variedades de trigo

O notebook reúne as entregas de **13/11/2026** (limpeza, EDA e seleção de atributos) e **20/11/2026** (divisão documentada, escolha e treinamento do modelo). O planejamento e a descrição do conjunto estão em [dataset-seed-versao-2.0.md](dataset-seed-versao-2.0.md).

## Executar no Google Colab

1. Abra `machine_learning_av2.ipynb` no Colab.
2. Envie `dados/dataset-seeds.txt` junto ao notebook, preservando a pasta `dados/`. Também é possível enviar `dataset-seeds.txt` ou `dataset-seeds.csv` diretamente para `/content/`.
3. Execute as células de cima para baixo. As bibliotecas usadas são `pandas`, `numpy`, `matplotlib`, `seaborn` e `scikit-learn`, disponíveis no Colab.

O notebook contém tabelas e gráficos de distribuição das classes, medidas por variedade, correlações, ranking ANOVA e seleção de atributos. Na seção 8, compara cinco candidatos por validação cruzada, explica a escolha e treina o pipeline final. O arquivo do modelo é salvo em `modelos/` no ambiente em que o notebook for executado. No Colab, baixe esse arquivo se quiser conservá-lo após a sessão.

## Resultado da entrega

- **210 registros e 7 atributos numéricos**, com 70 amostras por classe. O TXT original e o CSV do projeto contêm os mesmos valores.
- **Nenhum registro removido**: não há valores ausentes, infinitos, duplicatas exatas ou valores fora das regras de consistência adotadas.
- **Treino estratificado:** 168 registros; **teste reservado:** 42 registros. A EDA e a seleção de atributos usam apenas o treino.
- A seleção com ANOVA e validação cruzada de 5 dobras recomendou **área, perímetro, largura do grão e comprimento do sulco** pela regra de 1 erro padrão. A acurácia exploratória média foi **0,929** com quatro ou sete atributos; a maior média, **0,946**, ocorreu com cinco ou seis atributos.

Essas acurácias orientam a seleção de atributos. A avaliação final no teste reservado está planejada para a entrega de 27/11.

## Entrega de 20/11

A divisão 168/42 foi reproduzida. Usando apenas o treino, comparamos referência simples, regressão logística e árvore de decisão por validação cruzada e treinamos uma regressão logística com quatro atributos. O procedimento, os resultados e um roteiro de explicação estão em [entrega_20-11_seeds.md](entrega_20-11_seeds.md).

Para reproduzir com Python 3.12, crie um ambiente virtual, instale `requirements.txt` e execute `src/entrega_20_11.py`. O script grava a comparação em `resultados/`, a divisão por índice e o pipeline treinado em `modelos/`. O teste de 42 grãos continua reservado para 27/11.
