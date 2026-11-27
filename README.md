# AV2 — Classificação de variedades de trigo

Entrega de **27/11/2026**: refino da regressão logística e análise dos erros de classificação do dataset Seeds. O planejamento e a descrição do conjunto estão em [dataset-seed-versao-2.0.md](dataset-seed-versao-2.0.md).

## Executar no Google Colab

1. Abra `machine_learning_av2.ipynb` no Colab.
2. Envie `dados/dataset-seeds.txt` junto ao notebook, preservando a pasta `dados/`. Também é possível enviar `dataset-seeds.txt` ou `dataset-seeds.csv` diretamente para `/content/`.
3. Execute as células de cima para baixo. As bibliotecas usadas são `pandas`, `numpy`, `matplotlib`, `seaborn`, `scikit-learn` e `joblib`, disponíveis no Colab.

O notebook contém a leitura e auditoria dos dados, a divisão estratificada, a comparação de valores de `C` por validação cruzada, o treinamento do pipeline, a avaliação no teste reservado, a matriz de confusão e a tabela dos erros. Ele salva uma cópia do modelo em `modelos/modelo_27-11.joblib` no ambiente em que for executado.

## Resultado no notebook

- **210 registros e 7 atributos numéricos**, com 70 amostras por classe. O TXT original e o CSV do projeto contêm os mesmos valores.
- **Nenhum registro removido**: não há valores ausentes, infinitos, duplicatas exatas ou valores fora das regras de consistência adotadas.
- **Treino estratificado:** 168 registros; **teste reservado:** 42 registros. A escolha de `C` e a seleção de atributos usam apenas o treino.
- **Modelo refinado:** regressão logística com `C=10` e quatro atributos selecionados: área, perímetro, largura do grão e comprimento do sulco.
- **Teste reservado:** 38 acertos em 42 grãos (acurácia de **90,48%** e F1 macro de **0,9007**). Os quatro erros foram grãos Kama: três previstos como Canadian e um como Rosa.

## Material de apoio

A explicação das métricas, dos erros e um roteiro para apresentar o projeto estão em [entrega_27-11_seeds.md](entrega_27-11_seeds.md).

O script `src/entrega_27_11.py` separa o refino (`refinar`) da avaliação (`avaliar`). Como os resultados finais já estão salvos, use `verificar` para conferir fonte, modelo, previsões e métricas sem alterar os artefatos:

```powershell
.\.venv\Scripts\python.exe src\entrega_27_11.py verificar
```
