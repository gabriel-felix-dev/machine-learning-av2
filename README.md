# AV2 — Classificação de variedades de trigo

O [notebook](machine_learning_av2.ipynb) contém a **entrega de 20/11/2026**: divisão dos dados, escolha e treinamento do modelo. O procedimento e um roteiro de explicação estão em [entrega_20-11_seeds.md](entrega_20-11_seeds.md).

## Executar no Google Colab

1. Abra `machine_learning_av2.ipynb` no Colab.
2. Envie `dados/dataset-seeds.txt` junto ao notebook, preservando a pasta `dados/`. Também é possível enviar `dataset-seeds.txt` ou `dataset-seeds.csv` diretamente para `/content/`.
3. Execute as células de cima para baixo. O notebook usa `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn` e `joblib`, disponíveis no Colab.

O notebook lê e confere os dados, reproduz a divisão estratificada, compara cinco candidatos por validação cruzada no treino e ajusta o modelo escolhido. O arquivo do modelo é salvo em `modelos/` no ambiente em que o notebook for executado. No Colab, baixe esse arquivo se quiser conservá-lo após a sessão.

## Resultado da entrega

- **210 registros e 7 atributos numéricos**, com 70 amostras por classe. O TXT original e o CSV do projeto contêm os mesmos valores.
- **Nenhum registro removido**: não há valores ausentes, infinitos, duplicatas exatas ou valores fora das regras de consistência adotadas.
- **Treino estratificado:** 168 registros; **teste reservado:** 42 registros. A comparação e o treinamento usam apenas o treino.
- A validação cruzada recomendou **regressão logística com quatro atributos**: área, perímetro, largura do grão e comprimento do sulco. O F1 macro médio foi **0,9276**.

O modelo treinado acertou **158 dos 168 grãos usados no próprio ajuste**. Esse resultado não mede o desempenho em dados novos. O teste reservado será avaliado em outra etapa.

Para reproduzir com Python 3.12, crie um ambiente virtual, instale `requirements.txt` e execute `src/entrega_20_11.py`. O script grava a comparação em `resultados/`, a divisão por índice e o pipeline treinado em `modelos/`. O teste de 42 grãos continua reservado para 27/11.
