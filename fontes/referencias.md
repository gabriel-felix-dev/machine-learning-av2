# Fontes verificadas

Consulta em 06/11/2026. As fontes externas documentam o dataset e os métodos. Todas as métricas do projeto vêm da execução local.

## Dados e classes

- Charytanowicz, M., Niewczas, J., Kulczycki, P., Kowalski, P., & Lukasik, S. (2010). *Seeds* [Dataset]. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C5H30K
- Ficha oficial: https://archive.ics.uci.edu/dataset/236/seeds. Informa 210 grãos, 70 por variedade, sete medidas, ausência de faltantes, origem experimental em Lublin e licença CC BY 4.0. Não explicita a associação dos códigos aos nomes.
- Arquivo bruto: https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt. O projeto usa a cópia local já coletada, sem substituí-la.
- Correspondência confirmada na documentação do dataset mantida pelos autores do pacote ODRF: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd. A documentação associa explicitamente 1 a Kama, 2 a Rosa e 3 a Canadian. Cópia consultada: `fontes/ODRF_seeds.Rd`.
- Fonte editável da mesma documentação: https://raw.githubusercontent.com/liuyu-star/ODRF/master/R/seeds.R

**Diferença relevante:** a versão dos dados distribuída pelo pacote ODRF é descrita como tendo 209 linhas. Consultamos essa documentação apenas para a semântica dos códigos. Não importamos a versão do ODRF. A quantidade e os resultados deste projeto correspondem às 210 linhas do arquivo original local da UCI.

## Métodos

- Vazamento de dados e Pipeline: https://scikit-learn.org/stable/common_pitfalls.html
- SelectKBest: https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html
- Árvore de decisão: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
- GridSearchCV: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html
- DummyClassifier: https://scikit-learn.org/stable/modules/generated/sklearn.dummy.DummyClassifier.html

## Material da disciplina

`slide-machine-learning.pdf`, páginas físicas 10 a 130, consultadas até o fim. Ciclo de vida nas p. 52 e 130, preparação nas p. 55-67, treino/validação/teste nas p. 68-70 e 81, referência simples na p. 74, avaliação nas p. 77-79, refinamento nas p. 82-86 e 96, implantação na p. 97 e monitoramento na p. 98. As p. 90 e 95 contêm ilustrações de PCA/LDA sem texto extraível relevante. A paginação indicada conta a primeira página do PDF como 1.
