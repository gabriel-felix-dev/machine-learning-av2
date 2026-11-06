# Prompt para concluir o Projeto AV2 Seeds

Trabalhe no projeto de Machine Learning localizado em `D:\Dev - Falculdade\machine-learning-av2`.

Sua missão é preparar e executar as etapas restantes da AV2 com o dataset Seeds, produzindo materiais locais, reproduzíveis e organizados por entrega. Trabalhe de forma autônoma até concluir o projeto; peça esclarecimento apenas se faltar uma informação indispensável.

## Antes de começar

1. Inspecione os arquivos da pasta e leia `AGENTS.md`, `projeto_av2_seeds.md` e `entrega_06-11_seeds.md`.
2. Leia `slide-machine-learning.pdf` **a partir da página 10 até o fim do arquivo** e confira se há exigências adicionais.
3. Use `dados/seeds_dataset.txt` como arquivo bruto da UCI e preserve seu conteúdo.
4. Trate `D:\Dev - Falculdade\machine-learning-av2` como a raiz para novos códigos, gráficos, relatórios e apresentações, mesmo que seu diretório de trabalho inicial seja outro.

## Tecnologia definida

Implemente o projeto em **Python**. Use **pandas** para carregar o dataset, organizar as colunas, validar, limpar e explorar os dados e preparar `X` e `y` para o treinamento. Use **scikit-learn** para dividir os dados, selecionar atributos, ajustar o classificador e avaliar as previsões. `pandas` integra o fluxo de treinamento pela preparação dos dados; o ajuste do modelo é responsabilidade do estimador do `scikit-learn`. Registre as dependências e os comandos necessários para reproduzir a análise.

## Etapas do cronograma

- **13/11:** carregue e valide os dados com `pandas`; documente tipos, ausentes, duplicatas e decisões de limpeza. Faça EDA com tabelas e gráficos relevantes. Realize seleção de atributos e explique o método.
- **20/11:** divida os dados em treino e teste de forma estratificada e reproduzível; compare uma referência simples com modelos de classificação adequados; treine o modelo escolhido com `scikit-learn` e registre parâmetros e resultados. Há envio previsto nessa data, apesar do feriado.
- **27/11:** refine o modelo usando apenas os dados de treino para escolher ajustes. Avalie o teste reservado com acurácia, métricas por classe e matriz de confusão. Analise exemplos classificados incorretamente.
- **04/12:** prepare o relatório e a apresentação final, respondendo à pergunta e à hipótese registradas na entrega de 06/11.

A divisão dos dados deve ocorrer antes de qualquer seleção de atributos que use os rótulos. Use validação cruzada somente no conjunto de treino e preserve o teste para a avaliação final. Execute a análise para obter métricas e conclusões reais. Confirme em fonte confiável a correspondência entre os códigos 1, 2 e 3 e os nomes das variedades antes de associá-los.

Crie o código necessário, execute-o, verifique os artefatos gerados e registre como reproduzir a análise. Mantenha a entrega de 06/11 como registro do trabalho já feito. Ao terminar, informe quais arquivos foram criados, os resultados principais, os comandos para reproduzi-los e qualquer exigência do slide que tenha alterado o plano.
