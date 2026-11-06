# AV2 Seeds - Gabriel Felix

Projeto executado em **06/11/2026**, com as quatro próximas entregas preparadas antecipadamente. As datas nos arquivos representam os marcos acadêmicos, e não execuções futuras já realizadas. A entrega original de 06/11 e o arquivo bruto foram preservados. **20/11 tem envio previsto, apesar do feriado.** Nenhum envio à disciplina foi realizado por este projeto.

## Resultados observados

Divisão estratificada: **168 grãos de treino e 42 de teste**, com semente 42. Seleção de atributos e ajustes usam somente treino, com Pipeline e validação cruzada de cinco folds.

| Modelo | Acurácia no teste | F1 macro | Acertos |
| --- | --- | --- | --- |
| Referência de classe única | 33,33% | 0,1667 | 14/42 |
| Árvore inicial, sete atributos | 88,10% | 0,8766 | 37/42 |
| Árvore inicial, três atributos | 83,33% | 0,8226 | 35/42 |
| Árvore refinada | **92,86%** | **0,9263** | **39/42** |

O modelo final usa sete atributos na entrada, profundidade máxima 5, folha mínima 1 e poda `ccp_alpha=0.01`. Tem oito folhas. A validação, sem consultar teste, escolheu essa configuração entre 240 alternativas. Todos os modelos foram avaliados no mesmo teste após congelar a configuração final. O ganho sobre a referência é de 59,52 pontos percentuais. O intervalo de Wilson de 95% para a acurácia é de 80,99% a 97,54%.

Os três erros finais são grãos Kama: dois previstos como Canadian e um como Rosa. O relatório examina cada caso pela linha original. A hipótese foi sustentada nesta divisão, com limitações pela amostra pequena e pela falta de avaliação em novas origens.

## Onde encontrar os materiais

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| [entrega_13-11_seeds.md](entrega_13-11_seeds.md) | Auditoria, preparação, EDA e candidatos a atributos |
| [entrega_20-11_seeds.md](entrega_20-11_seeds.md) | Divisão e comparação inicial por validação |
| [entrega_27-11_seeds.md](entrega_27-11_seeds.md) | Refinamento, teste final e análise individual dos erros |
| [entrega_04-12_seeds.md](entrega_04-12_seeds.md) | Consolidação final, arquivos e próximos passos |
| [relatorios/relatorio_final.pdf](relatorios/relatorio_final.pdf) | Relatório paginado, nove páginas |
| [relatorios/relatorio_final.md](relatorios/relatorio_final.md) | Relatório completo editável |
| [apresentacao/apresentacao_final.pptx](apresentacao/apresentacao_final.pptx) | Apresentação editável de 15 slides, com tabelas e gráficos nativos |
| [apresentacao/roteiro_apresentacao.md](apresentacao/roteiro_apresentacao.md) | Roteiro e fontes por slide |
| [relatorios/protocolo_experimental.md](relatorios/protocolo_experimental.md) | Critérios fixados antes de executar os modelos |
| [relatorios/aderencia_slide.md](relatorios/aderencia_slide.md) | Correspondência com as páginas do material da aula |
| [relatorios/plano_monitoramento.md](relatorios/plano_monitoramento.md) | Implantação local executada e monitoramento proposto |
| [fontes/referencias.md](fontes/referencias.md) | Fontes verificadas, inclusive o mapa das classes |
| `src/` | Código de análise, inferência, relatórios, apresentação e verificação |
| `dados/` | Bruto preservado, dados organizados, X/y por partição e exemplo de inferência |
| `resultados/` | Auditoria, folds, grade, métricas por classe, matrizes, previsões e erros em CSV/JSON |
| `graficos/` | Dez figuras em PNG e SVG: classes, boxplots, histogramas, correlação, dispersão, ranking, matriz, comparação, árvore e ROC |
| `modelos/` | Pipeline Joblib, regras da árvore e referência estatística do treino |
| [resultados/manifesto_arquivos.csv](resultados/manifesto_arquivos.csv) | Lista dos arquivos entregues, tamanhos e hashes |

`dados/seeds_dataset.txt` é a fonte bruta. `dados/seeds_tratado.csv` é derivado. `linha_origem` conta as linhas do bruto a partir de 1 e nunca entra em X. Os nomes de variedades, a partição e a classe também não entram nos atributos preditores.

## Reprodução em Python

Ambiente validado: **Python 3.12.14**, pandas 3.1.1, scikit-learn 1.9.1. Todas as versões diretas e transitivas estão fixadas em `requirements.txt`. O pipeline resolve os caminhos pela localização do código e pode ser chamado de outra pasta.

Com o ambiente `.venv` já criado nesta máquina:

```powershell
Set-Location 'D:\Dev - Falculdade\machine-learning-av2'
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src/analise_seeds.py
.\.venv\Scripts\python.exe src/gerar_relatorios.py
.\.venv\Scripts\python.exe src/prever.py dados/exemplo_inferencia.csv --saida resultados/previsoes_exemplo.csv
.\.venv\Scripts\python.exe src/verificar_resultados.py
.\.venv\Scripts\python.exe src/gerar_manifesto.py
```

Para recriar o ambiente com o Python 3.12 do runtime disponível nesta máquina, execute antes:

```powershell
Set-Location 'D:\Dev - Falculdade\machine-learning-av2'
& 'C:\Users\Gabriel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m venv .venv
```

Em outra máquina com Python 3.12 instalado, pode usar `py -3.12 -m venv .venv` no Windows ou `python3.12 -m venv .venv` no Linux/macOS, adaptando o caminho do executável do ambiente. O relatório PDF usa Arial no Windows e Helvetica como alternativa quando não disponível. A reprodução da análise não requer a internet após instalar as dependências e ter o bruto local.

O script de análise não baixa nem sobrescreve o bruto e confere seu SHA-256:

```text
1f3f83c0d8485ae9148061389d19628607e3f5660e3d6f40ec9102fb398bb12f
```

O script interrompe se detectar alteração do bruto, esquema inesperado, faltantes ou duplicatas. A demonstração de inferência usa as linhas de treino 179, 63 e 55. Ela verifica o programa salvo e **não representa nova avaliação de generalização**. Para prever outro lote, forneça um CSV com as colunas `area,perimetro,compacidade,comprimento,largura,assimetria,sulco` e use `src/prever.py`. Os escores representam proporções nas folhas e não foram calibrados.

Reexecutar o experimento com a mesma divisão reproduz os resultados registrados. Não use o teste já conhecido para escolher novas configurações ou alegar uma avaliação inédita de uma nova versão.

## Reprodução da apresentação

A apresentação final já pode ser aberta em um editor de PPTX. O gerador `src/gerar_apresentacao.mjs` usa Node.js v24.22.1 e `@oai/artifact-tool` 2.8.132 do runtime Codex, com os validadores fornecidos pela skill de apresentações. Esse componente não é uma dependência Python e não é necessário para refazer a análise.

Nesta máquina:

```powershell
Set-Location 'D:\Dev - Falculdade\machine-learning-av2'
& 'C:\Users\Gabriel\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' src/gerar_apresentacao.mjs
```

O código contém os caminhos locais padrão e aceita `CODEX_RUNTIME_NODE_MODULES`, `CODEX_RUNTIME_PYTHON` e `CODEX_PRESENTATION_SKILL` para outro runtime compatível. O gerador não sobrescreve um PPTX final existente: cria uma nova versão com sufixo. Arquivos intermediários de exportação, validação e prévias ficam em `.build/`, fora das pastas de entrega. O validador também pode gerar pastas temporárias `.chart-data-*` na raiz, excluídas do Git e do manifesto. Os valores dos gráficos de CV/teste são arredondados a 12 algarismos significativos para compatibilidade com as planilhas embutidas, preservando toda a precisão exibida. As métricas completas permanecem no JSON/CSV.

## Conferência do slide e das fontes

O PDF da aula foi consultado da página física **10 até 130**. As p. 52 e 130 incluem implantação e monitoramento, e as p. 97-98 detalham essas etapas. Por isso o trabalho inclui inferência local e um plano operacional. O monitoramento de produção está explicitamente planejado, sem medições inventadas. A divisão antecipada e o uso do teste apenas ao fim seguem a instrução do projeto e as p. 68-70/81.

A [ficha da UCI](https://archive.ics.uci.edu/dataset/236/seeds) documenta 210 grãos e as variedades. A [documentação dos autores do ODRF](https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd) confirma **1=Kama, 2=Rosa, 3=Canadian**. Essa documentação descreve uma versão de 209 linhas, consultada somente para os nomes dos códigos. Não importamos essa versão. A análise usa exclusivamente as 210 linhas do bruto local da UCI.

Charytanowicz, M., Niewczas, J., Kulczycki, P., Kowalski, P., & Lukasik, S. (2010). *Seeds* [Dataset]. UCI Machine Learning Repository. [DOI 10.24432/C5H30K](https://doi.org/10.24432/C5H30K). Licença CC BY 4.0.
