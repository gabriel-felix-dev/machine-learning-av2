# AV2 — Classificação de variedades de trigo

Entrega de **13/11/2026**: limpeza e pré-processamento, análise exploratória (EDA) e seleção de atributos do dataset Seeds. O planejamento e a descrição do conjunto estão em [dataset-seed-versao-1.0.md](dataset-seed-versao-1.0.md).

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

Essas acurácias orientam a seleção de atributos. A avaliação final no teste reservado pertence à próxima entrega.
