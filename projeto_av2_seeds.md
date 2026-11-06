# Projeto AV2 — Machine Learning com o dataset Seeds

**Pasta raiz oficial para todos os próximos materiais:** `D:\Dev - Falculdade\machine-learning-av2`. Criar entregas, códigos, gráficos, relatórios e apresentações nesta pasta ou em subpastas dela, mesmo quando o diretório de trabalho de uma conversa estiver em outro local.

## Orientações gerais da AV2

| Tarefa | Descrição |
| --- | --- |
| **T1** | Buscar um dataset interessante. |
| **T2** | Definir uma hipótese ou pergunta a ser respondida com os dados. |
| **T3** | Aplicar o ciclo de vida de um projeto de machine learning. A orientação do quadro remete ao PDF da Aula 03 **a partir da página 10**. |
| **T4** | Fazer previsões sobre uma variável alvo determinada. |

As fontes de dados mencionadas no quadro incluem portais de dados abertos do Brasil, dos EUA, de outros países ou da União Europeia, Our World in Data e Kaggle. Para este trabalho, o dataset escolhido é o **[Seeds, do UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/236/seeds)**, um repositório público de dados.

**Regras informadas:** entregas semanais; nota de 0 a 10 para cada entrega; nota final pela média das notas das entregas; trabalho individual ou em dupla. Este projeto está identificado em [`entrega_06-11_seeds.md`](entrega_06-11_seeds.md) como trabalho de Gabriel Felix.

## Arquivos e estado atual

| Caminho na pasta do projeto | Função |
| --- | --- |
| [`entrega_06-11_seeds.md`](entrega_06-11_seeds.md) | Registro da entrega inicial: tema, dataset, coleta, pergunta, hipótese e plano do ciclo de vida. Ler antes de continuar. |
| [`dados/seeds_dataset.txt`](dados/seeds_dataset.txt) | Cópia sem alterações do arquivo original da UCI. Preservar como dado bruto. |
| `slide-machine-learning.pdf` | Slide de orientação indicado pelo usuário como localizado na **pasta raiz do projeto**. Consultar **da página 10 até o fim do arquivo** antes de definir a versão final das etapas. |

**Situação do slide em 06/11/2026:** `slide-machine-learning.pdf` foi localizado na pasta raiz oficial. Seu conteúdo da página 10 em diante ainda precisa ser conferido antes de aplicar suas orientações. Não atribuir ao slide orientações que não tenham sido lidas.

**Dados já conferidos:** o arquivo bruto contém 210 linhas, cada uma com sete medidas numéricas e um código de classe; há 70 registros em cada classe (1, 2 e 3). A UCI informa ausência de valores faltantes. A verificação detalhada de duplicatas, consistência e distribuições pertence à etapa de 13/11.

**Tecnologia escolhida:** Python com `pandas` para leitura, limpeza, organização e análise dos dados, inclusive a preparação das tabelas usadas no treinamento. O ajuste e a avaliação do classificador serão feitos com `scikit-learn`, pois `pandas` não treina uma árvore de decisão por conta própria. O código deverá declarar as dependências e permitir reprodução dos resultados.

## Cronograma oficial e aplicação ao Seeds

| Data | Orientação da AV2 | Trabalho previsto com o Seeds |
| --- | --- | --- |
| **06/11** | T1, T2 e T3: definição do problema e coleta de dados. | Apresentar fonte, pergunta, hipótese, sete atributos, variável alvo e etapas planejadas. A entrega está registrada em `entrega_06-11_seeds.md`. |
| **13/11** | Limpeza e pré-processamento, análise exploratória dos dados (EDA) e seleção de atributos (*feature selection*). | Conferir leitura do arquivo, tipos, ausentes e duplicatas. Fazer gráficos comparando as medidas entre as três variedades e avaliar quais atributos são mais úteis. |
| **20/11** | Feriado; **envio** da divisão dos dados, seleção do modelo e treinamento do modelo. | Separar os dados preservando as três classes em treino e teste. Treinar uma árvore de decisão e comparar os sete atributos com um conjunto selecionado. |
| **27/11** | Refinamento do modelo e análise dos erros. | Ajustar a profundidade da árvore e analisar a matriz de confusão: quais variedades são confundidas e em quantos grãos. |
| **04/12** | Apresentação final. | Apresentar gráficos, modelo, resultados, erros, limitações e conclusão sobre a hipótese. |

## Instruções para o agente de IA que concluirá o projeto

### 1. Manter a definição do projeto

- Tratar o problema como **classificação supervisionada de três classes**. A variável alvo é o oitavo valor de cada linha; os sete valores anteriores são área, perímetro, compacidade, comprimento, largura, coeficiente de assimetria e comprimento do sulco do grão, nesta ordem.
- Usar como pergunta central: **“As sete características geométricas do dataset Seeds permitem prever a variedade de um grão de trigo?”**
- Testar a hipótese registrada em `entrega_06-11_seeds.md`: o modelo deve superar uma regra que sempre prevê uma única classe. Como as classes estão equilibradas, essa regra acerta cerca de **33,3%** dos registros.
- Manter a origem e a citação do dataset na documentação. Não alterar `dados/seeds_dataset.txt`; criar arquivos derivados separados quando necessário.
- Não associar os códigos 1, 2 e 3 aos nomes Kama, Rosa e Canadian sem confirmar essa correspondência em uma fonte confiável. Os nomes das três variedades são documentados pela UCI, mas a página consultada não explicita a associação de cada nome a cada código.

### 2. Executar e registrar as etapas por entrega

1. **Para 13/11:** usar `pandas` para carregar o arquivo de texto considerando espaços ou tabulações como separadores e atribuir nomes às oito colunas. Conferir dimensões, tipos, códigos de classe, ausentes, duplicatas e valores suspeitos; justificar qualquer correção. Fazer EDA com contagem das classes, resumos das sete medidas e gráficos que comparem atributos entre classes. Registrar o procedimento de seleção de atributos e os atributos candidatos.
2. **Antes de qualquer seleção supervisionada:** separar treino e teste de forma estratificada e com semente aleatória fixa, mesmo que a divisão só seja apresentada formalmente em 20/11. Ajustar seletores e outros transformadores apenas no treino; reservar o teste para a avaliação final. Se usar validação cruzada, executá-la somente no treino.
3. **Para 20/11:** documentar a proporção e a distribuição por classe nos conjuntos de treino e teste. Preparar as entradas e o alvo com `pandas`. Usar `scikit-learn` para comparar o desempenho de uma regra básica com uma árvore de decisão, treinar uma versão com os sete atributos e outra com o subconjunto selecionado e avaliar os modelos. Justificar a escolha do modelo e registrar parâmetros, métricas e resultados reproduzíveis. Lembrar que **20/11 é feriado, mas há envio previsto**.
4. **Para 27/11:** refinar parâmetros da árvore, como profundidade máxima e tamanho mínimo das folhas, usando apenas dados de treino para escolher ajustes. Relatar acurácia, desempenho por classe e matriz de confusão no teste reservado. Examinar os casos classificados incorretamente e explicar as principais confusões observadas, sem inventar causas que os dados não sustentem.
5. **Para 04/12:** preparar apresentação que mostre problema, fonte, hipótese, preparação, EDA, seleção de atributos, divisão dos dados, modelo, métricas, análise dos erros, limitações e conclusão. Responder explicitamente à pergunta inicial e indicar se a hipótese foi sustentada pelos resultados observados.

### 3. Critérios de execução

- Guardar código, gráficos e relatórios em arquivos identificáveis e reproduzíveis dentro da pasta do projeto. Indicar como executar a análise e de qual arquivo bruto ela parte.
- Diferenciar claramente **resultado observado** de **etapa planejada**. Não preencher métricas ou conclusões antes de executar os experimentos.
- Dar prioridade às orientações efetivamente verificadas no slide quando `slide-machine-learning.pdf` estiver disponível. Se houver divergência relevante com este resumo, documentar a diferença antes de alterar o trabalho já entregue.
- Ao concluir cada etapa, atualizar este documento ou criar uma entrega datada com o que foi feito, os resultados e os próximos passos, preservando o registro de 06/11.

## Referência do dataset

Charytanowicz, M., Niewczas, J., Kulczycki, P., Kowalski, P., & Lukasik, S. (2010). *Seeds* [Dataset]. UCI Machine Learning Repository. <https://doi.org/10.24432/C5H30K>

Página oficial: <https://archive.ics.uci.edu/dataset/236/seeds>  
Arquivo original: <https://archive.ics.uci.edu/ml/machine-learning-databases/00236/seeds_dataset.txt>

## Atualização de execução em 06/11/2026

As etapas restantes foram executadas antecipadamente e registradas em `entrega_13-11_seeds.md`, `entrega_20-11_seeds.md`, `entrega_27-11_seeds.md` e `entrega_04-12_seeds.md`. As datas identificam os marcos acadêmicos. A entrega inicial de 06/11 permanece preservada. Os materiais não foram enviados à plataforma da disciplina.

O slide foi consultado da página física 10 à 130. A indicação anterior de consulta pendente representa o estado inicial. A conferência está em `relatorios/aderencia_slide.md`. O ciclo de vida inclui implantação e monitoramento, então foram acrescentados modelo serializado, previsão local em lote e plano de monitoramento.

Resultados executados: 210 registros íntegros, sem ausentes ou duplicatas; treino/teste estratificados 168/42, semente 42. EDA e seleção orientadas somente por treino. Pipeline e validação de cinco folds comparam referência, árvore completa e k=3. A busca de 240 configurações escolheu sete atributos, profundidade máxima 5, folha mínima 1 e poda 0,01, antes de consultar teste. A árvore final tem oito folhas e acerta 39/42 (92,86%), com F1 macro 0,9263, contra 14/42 (33,33%) da referência. Os três erros são Kama, dois como Canadian e um como Rosa. A hipótese foi sustentada nesta divisão, com limites pela amostra e origem dos dados.

Mapa de classes confirmado na documentação mantida pelos autores do pacote ODRF: 1=Kama, 2=Rosa, 3=Canadian. Fonte e diferença da versão de 209 linhas documentadas em `fontes/referencias.md`. Os resultados usam as 210 linhas da cópia bruta UCI local, cujo conteúdo e SHA-256 foram preservados.

Navegação e reprodução: `README.md`. Relatório: `relatorios/relatorio_final.md` e PDF. Apresentação: `apresentacao/apresentacao_final.pptx`. Código: `src/`. Resultados completos: `resultados/`. Próximos passos externos: revisar os materiais e cumprir os envios do cronograma, incluindo 20/11 no feriado. Para expandir o projeto, coletar novos grãos independentes e reservar nova avaliação externa.
