"""Gera as entregas Markdown e o relatório PDF a partir das métricas executadas."""
import json
from html import escape
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"referencia": "Referência simples", "arvore_7": "Árvore inicial (7)", "arvore_k3": "Árvore inicial (k=3)", "arvore_refinada": "Árvore refinada"}
LABELS = ["Kama", "Rosa", "Canadian"]


def pct(value):
    return f"{100*value:.2f}%".replace(".", ",")


def dec(value, places=4):
    return f"{value:.{places}f}".replace(".", ",")


def markdown_table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"]*len(headers)) + " |"] + ["| " + " | ".join(map(str, row)) + " |" for row in rows])


def write(path, text):
    (ROOT / path).write_text(text.rstrip() + "\n", encoding="utf-8")


def main():
    s = json.loads((ROOT / "resultados/resumo_execucao.json").read_text(encoding="utf-8"))
    final = s["teste"][-1]; m = s["modelo_final"]; report = s["metricas_por_classe"]["arvore_refinada"]
    cv_rows = [[NAMES[r["modelo"]], pct(r["acuracia_cv_media"]), dec(r["f1_macro_cv_media"]), dec(r["f1_macro_cv_dp"])] for r in s["validacao"]]
    test_rows = [[NAMES[r["modelo"]], pct(r["acuracia_treino"]), pct(r["acuracia_teste"]), dec(r["f1_macro_teste"]), f'{r["acertos"]}/42'] for r in s["teste"]]
    class_rows = [[name, pct(report[name]["precision"]), pct(report[name]["recall"]), dec(report[name]["f1-score"]), "14"] for name in LABELS]
    cv_md = markdown_table(["Modelo", "Acurácia CV", "F1 macro CV", "DP F1 macro"], cv_rows)
    test_md = markdown_table(["Modelo", "Acurácia treino", "Acurácia teste", "F1 macro teste", "Acertos"], test_rows)
    class_md = markdown_table(["Classe", "Precisão", "Recall", "F1", "Suporte"], class_rows)
    cm_md = markdown_table(["Real / previsto", *LABELS], [[name, *row] for name, row in zip(LABELS, s["matrizes_confusao"]["arvore_refinada"])])
    rank = pd.read_csv(ROOT / "resultados/ranking_atributos_treino.csv")
    rank_rows = [[row.atributo, dec(row.F_ANOVA, 2), "Sim" if row.candidato_k3 else "Não"] for row in rank.itertuples()]
    rank_md = markdown_table(["Atributo", "F ANOVA no treino", "Candidato k=3"], rank_rows)
    error_rows = [[e["linha_origem"], e["variedade_real"], e["variedade_prevista"], e["folha"], e["amostras_treino_folha"]] for e in s["erros_finais"]]
    err_md = markdown_table(["Linha do bruto", "Real", "Previsto", "Folha", "Grãos de treino na folha"], error_rows)
    error_sections = []
    for e in s["erros_finais"]:
        neighbors = "; ".join(f'linha {v["linha"]}, classe {v["classe"]}, distância {dec(v["distancia_padronizada_7_atributos"],3)}' for v in e["vizinhos_treino"])
        error_sections.append(f'### Linha {e["linha_origem"]}: {e["variedade_real"]} classificada como {e["variedade_prevista"]}\n\nCaminho observado: ' + "; ".join(e["caminho"]) + f'. Folha {e["folha"]}, com {e["amostras_treino_folha"]} exemplos de treino. Proporções de classes 1, 2, 3 nessa folha: {e["proporcoes_classes_folha"]}.\n\nTrês vizinhos no treino, por distância euclidiana nos sete atributos padronizados com estatísticas somente do treino: {neighbors}. Esse diagnóstico não altera o classificador.\n')
    errors_md = "\n".join(error_sections)
    date_note = "Material preparado antecipadamente em 06/11/2026. A data no título identifica o marco do cronograma, não uma execução futura já ocorrida. Não houve envio à plataforma da disciplina."
    quality_text = (f'Auditoria executada: 210 linhas, sete medidas contínuas e uma classe nominal codificada por inteiro. '
                    f'Zero ausentes, zero duplicatas de linhas ou de X, zero valores não finitos e zero medidas não positivas. '
                    f'O arquivo foi lido com `pandas.read_csv(sep=r"\\s+", header=None)`, nomes explícitos e conversão numérica validada. '
                    f'Nenhum registro foi removido ou valor corrigido. O bruto mantém o mesmo SHA-256 antes e depois.')
    eda_text = (f'A EDA usa somente os 168 grãos de treino. A correlação de Pearson entre área e perímetro foi '
                f'{dec(s["eda_treino"]["correlacao_area_perimetro"])}. Essa redundância ajuda a explicar por que escolher '
                f'apenas os três maiores escores univariados pode descartar informação complementar. '
                f'O critério de 1,5 IQR sinalizou quatro valores de compacidade e dois de assimetria, em seis grãos. '
                f'Mantivemos esses registros por não existir evidência de erro de medição. '
                f'No treino, a média da área foi 14,43 em Kama, 18,36 em Rosa e 11,87 em Canadian, '
                f'enquanto a média da assimetria foi 2,58, 3,66 e 4,82, respectivamente. Há sobreposição entre distribuições.')
    method_text = ("A divisão estratificada 80/20, semente 42, precede EDA e seleção supervisionada. São 168 exemplos de treino "
                   "(56 por classe) e 42 de teste (14 por classe). Validação cruzada estratificada de cinco folds, com "
                   "embaralhamento e semente 42, usa apenas treino. O seletor SelectKBest com ANOVA f_classif fica no Pipeline "
                   "e reaprende as colunas em cada fold. Não há normalização no classificador de árvore, imputação ou "
                   "reamostragem. As classes já estão equilibradas. Os códigos 1, 2, 3 são categorias, sem ordem quantitativa.")
    tuning_text = ("A busca testa 240 configurações e 1.200 ajustes de validação: k em [2,3,4,5,6,all], profundidade "
                   "em [2,3,4,5,None], folha mínima em [1,2,4,6] e ccp_alpha em [0,0.01]. F1 macro médio escolhe "
                   "a configuração. Empates numéricos usam acurácia, menos atributos, menor profundidade, maior folha "
                   "mínima e maior poda, nessa ordem. A comparação usa os mesmos folds. O melhor resultado de CV "
                   "é um critério de seleção e pode ser otimista após a busca. O desvio padrão entre folds não é um intervalo de confiança.")
    chosen_text = (f'A configuração escolhida aceita os sete atributos, usa Gini, max_depth=5, min_samples_leaf=1, '
                   f'ccp_alpha=0.01 e random_state=42. A árvore resultante tem {m["profundidade_observada"]} níveis de profundidade '
                   f'e {m["folhas"]} folhas. Seus cortes efetivos usam área, comprimento, largura, assimetria e sulco. '
                   f'Perímetro e compacidade continuam na entrada, mas não aparecem nos cortes da árvore final.')
    outcome_text = (f'A árvore refinada acertou {final["acertos"]} de 42 grãos: acurácia {pct(final["acuracia_teste"])} '
                    f'e F1 macro {dec(final["f1_macro_teste"])}. A referência sempre prevê Kama no treino completo '
                    f'e acerta 14/42 ({pct(s["teste"][0]["acuracia_teste"])}). O ganho foi de '
                    f'{dec(s["ganho_acuracia_pontos_percentuais"],2)} pontos percentuais. '
                    f'O intervalo de Wilson de 95% da acurácia é {pct(s["ic95_wilson_acuracia"][0])} a '
                    f'{pct(s["ic95_wilson_acuracia"][1])}, sob aproximação binomial para este teste. '
                    f'AUC macro um-contra-resto: {dec(s["auc_macro_ovr"])}. AUC mede ordenação dos escores, não a taxa de acertos.')
    errors_text = ("Todos os erros finais são Kama: dois classificados como Canadian e um como Rosa. As linhas 24 e 62 "
                   "caem na mesma região de área pequena e sulco acima de 4,675, com folha formada por 48 Canadian no treino. "
                   "Os vizinhos nos sete atributos incluem ambas as classes. A linha 38 tem área 17,08 e largura 3,683 e "
                   "alcança uma folha Rosa formada por apenas um grão de treino. Isso evidencia fragilidade local da árvore. "
                   "As proporções de classe nas três folhas erradas são 100% para a classe prevista, mostrando que pureza "
                   "de folha não equivale a certeza de acerto. Não há evidência para atribuir os erros a defeitos, rótulos "
                   "incorretos ou causas biológicas. O diagnóstico é descritivo e não gerou novo ajuste após consultar o teste.")
    limitations = ("O teste contém apenas 42 exemplos e uma única divisão. Um erro representa 2,38 pontos percentuais "
                   "de acurácia e 7,14 pontos no recall de uma classe. Não há avaliação em nova safra, local, instrumento "
                   "ou protocolo de medição. A UCI descreve coleta em campos experimentais em Lublin. A hipótese fica "
                   "sustentada nesta divisão, sem demonstrar desempenho universal, causalidade ou superioridade sobre todos "
                   "os classificadores. A busca escolheu uma folha mínima de 1, mantendo risco local mesmo com poda. "
                   "O teste já consultado não serve como avaliação inédita de versões futuras. Não fizemos teste formal "
                   "de significância nem apresentamos um valor-p como prova da hipótese.")
    source_text = ("Dados: Charytanowicz et al. (2010), Seeds, UCI, DOI 10.24432/C5H30K, CC BY 4.0. "
                   "A ficha UCI informa os nomes, mas não explicita o mapa dos códigos. A documentação mantida pelos "
                   "autores do ODRF confirma 1=Kama, 2=Rosa, 3=Canadian. Ela descreve uma versão de 209 linhas, usada "
                   "aqui apenas para o mapa semântico. Toda a análise usa as 210 linhas do bruto local da UCI.")

    write("entrega_13-11_seeds.md", f"""# Entrega de 13/11/2026 - Preparação, EDA e seleção

{date_note}

## Procedimento e resultados observados

{quality_text}

Colunas: `area`, `perimetro`, `compacidade`, `comprimento`, `largura`, `assimetria`, `sulco`, `classe`. Identificador rastreável: `linha_origem`, contado a partir de 1. A fonte UCI não explicita unidades físicas na tabela consultada. Não atribuímos unidades por suposição. A discrepância máxima entre compacidade informada e 4πA/P² foi {dec(s['auditoria']['compacidade_residuo_maximo'],6)}. Esse diagnóstico isolado não justifica recalcular medidas do original.

{method_text}

{eda_text}

![Boxplots no treino](graficos/02_boxplots_treino.png)

{rank_md}

Os candidatos iniciais são área, perímetro e largura. O ranking ANOVA é um filtro univariado exploratório, não uma conclusão causal nem garantia de melhor subconjunto. Seus valores-p não foram usados como inferência confirmatória após seleção. O número final de atributos depende da validação posterior.

## Arquivos produzidos

`dados/seeds_tratado.csv`, `dados/X_treino.csv`, `dados/y_treino.csv`, `dados/X_teste.csv`, `dados/y_teste.csv`; `resultados/validacao_dados.json`, `particoes.csv`, `limites_iqr_treino.csv`, `extremos_iqr_treino.csv`, `resumo_treino.csv`, `resumo_por_classe_treino.csv`, `correlacao_treino.csv`, `ranking_atributos_treino.csv`; gráficos 01 a 06 em PNG e SVG. Os nomes sem diretório nesta lista pertencem a `resultados/`.

## Próximos passos do cronograma

Em 20/11, comparar referência e árvores por validação no treino. O teste fica reservado. As etapas posteriores já foram executadas antecipadamente e estão registradas nas respectivas entregas.
""")
    write("entrega_20-11_seeds.md", f"""# Entrega de 20/11/2026 - Divisão, escolha e treinamento

{date_note}

**Há envio previsto em 20/11, apesar do feriado.**

## Procedimento e resultados observados

{method_text}

O pandas prepara X e y. O scikit-learn realiza divisão, seleção, treinamento e avaliação. A árvore representa relações não lineares com regras explicáveis e atende ao plano inicial. Referência: `DummyClassifier(strategy='most_frequent')`. Árvores iniciais: Gini, profundidade irrestrita, folha mínima 1, semente 42, todos os atributos ou k=3 selecionados dentro do fold. Em folds com frequências ligeiramente diferentes, a referência pode prever outra classe majoritária.

{cv_md}

Nesta etapa, os três primeiros modelos constituem a comparação inicial. A linha refinada consolida o trabalho de 27/11. A árvore com sete atributos superou a versão k=3 em validação. As duas árvores iniciais alcançaram 100% no treino interno, mas ficaram abaixo disso na validação, evidenciando necessidade de controlar complexidade. As médias de acurácia são médias não ponderadas entre folds de 33 ou 34 exemplos.

Não consultamos o teste para escolher o modelo. Os resultados finais dos quatro modelos constam da entrega de 27/11, calculados após congelar a configuração refinada.

## Arquivos produzidos

`src/analise_seeds.py`, `requirements.txt`, `resultados/distribuicao_particoes.csv`, `resultados/folds_validacao.csv`, `resultados/comparacao_folds.csv`, `resultados/comparacao_validacao.csv` e `relatorios/protocolo_experimental.md`.

## Próximos passos do cronograma

Em 27/11, ajustar profundidade, tamanho mínimo de folha, poda e quantidade de atributos só com treino, congelar a configuração e abrir o teste para avaliação final e análise dos erros.
""")
    write("entrega_27-11_seeds.md", f"""# Entrega de 27/11/2026 - Refinamento e análise dos erros

{date_note}

## Ajustes com treino e validação

{tuning_text}

{chosen_text}

{cv_md}

## Avaliação final no teste reservado

{outcome_text}

{test_md}

{class_md}

Precisão = acertos entre as previsões da classe. Recall = acertos entre os exemplos reais da classe. F1 combina precisão e recall. F1 macro dá o mesmo peso às três classes. Suporte é a quantidade real no teste. A referência tem precisão/recall/F1 zero nas classes nunca previstas, com `zero_division=0` declarado.

Matriz com linhas reais e colunas previstas:

{cm_md}

![Matriz de confusão final](graficos/07_matriz_confusao_final.png)

## Erros observados

{err_md}

{errors_text}

{errors_md}

## Limitações

{limitations}

## Arquivos produzidos e próximos passos

`resultados/busca_hiperparametros.csv`, `modelo_congelado.json`, `comparacao_teste.csv`, `previsoes_teste.csv`, `erros_teste.csv`, `erros_detalhados.json`, `resumo_execucao.json`, `importancias_arvore_final.csv`; métricas por classe e matrizes de confusão de cada modelo em CSV; gráficos 07 a 10; `modelos/seeds_arvore.joblib` e `modelos/regras_arvore.txt`. Os nomes sem diretório nesta lista pertencem a `resultados/`.

Para 04/12, consolidar relatório, apresentação, demonstração local de inferência e plano de monitoramento. O modelo permanece congelado após esta avaliação.
""")
    write("entrega_04-12_seeds.md", f"""# Entrega de 04/12/2026 - Relatório e apresentação final

{date_note}

## Resultados e conclusão

Pergunta preservada: **As sete características geométricas do dataset Seeds permitem prever a variedade de um grão de trigo?**

{outcome_text}

Sim, os resultados sustentam a hipótese operacional nesta divisão: o modelo supera a regra que sempre prevê uma classe. O subconjunto de três atributos não foi superior à entrada completa. {limitations}

## Materiais produzidos

- `relatorios/relatorio_final.md` e `relatorios/relatorio_final.pdf`.
- `apresentacao/apresentacao_final.pptx` e `apresentacao/roteiro_apresentacao.md`.
- `src/analise_seeds.py`, `src/prever.py`, `src/gerar_relatorios.py`, `src/verificar_resultados.py` e `src/gerar_apresentacao.mjs`.
- `README.md`, `requirements.txt`, `fontes/referencias.md` e `resultados/manifesto_arquivos.csv`.
- Dados derivados, tabelas de resultados, dez figuras em PNG/SVG e pipeline treinado.

## Adequações exigidas pelo ciclo de vida do slide

As p. 52, 97, 98 e 130 incluem implantação e monitoramento. Acrescentamos pipeline Joblib, previsão em lote, referência estatística do treino e plano de monitoramento em `relatorios/plano_monitoramento.md`. O monitoramento de produção continua planejado, pois não há dados novos ou sistema publicado. As p. 68-70 e 81 reforçam a preservação do teste, e as p. 77-79 motivaram métricas por classe e ROC/AUC complementar. A conferência completa está em `relatorios/aderencia_slide.md`.

## Reprodução e próximos passos

Seguir `README.md`. A análise e o relatório são reproduzíveis em Python com o arquivo bruto local e versões fixadas. A apresentação editável já está entregue, e seu código usa o runtime Artifact Tool do Codex. Não houve envio à disciplina. Próximos passos externos: revisar identificação/tempo de apresentação, enviar os materiais nas datas previstas e, em eventual expansão, obter dados independentes por safra e local.
""")
    full = f"""# AV2 Seeds - Relatório final

Gabriel Felix. Execução antecipada em 06/11/2026. Entrega final prevista: 04/12/2026.

## 1. Problema, pergunta e hipótese

As sete características geométricas do dataset Seeds permitem prever a variedade de um grão de trigo?

Classificação supervisionada multiclasse: sete medidas como X, variedade como y. Hipótese preservada: superar uma regra que sempre prevê uma única classe. Acurácia da referência equilibrada esperada: cerca de 33,3%. A métrica de seleção é F1 macro, com acurácia e métricas por classe para comunicar o resultado.

{outcome_text}

## 2. Origem e auditoria

{source_text}

{quality_text}

SHA-256: `{s['auditoria']['sha256_antes']}`.

Entradas: área, perímetro, compacidade, comprimento, largura, assimetria e comprimento do sulco, nesta ordem. Não há unidades físicas explicitadas na ficha consultada. A compacidade é relacionada a 4πA/P², e a maior diferença observada foi {dec(s['auditoria']['compacidade_residuo_maximo'],6)}. Nenhum valor foi recalculado. `linha_origem` identifica a linha física do bruto a partir de 1 e não entra no modelo. `variedade` e `particao` também ficam fora de X.

## 3. Preparação e divisão

{method_text}

`dados/seeds_tratado.csv` organiza dados e metadados. Os CSV de X/y preservam `linha_origem` como índice, que deve ser retirado das entradas. O código realiza essa exclusão explicitamente. As quantidades globais e a qualidade são conferidas para todo o bruto, enquanto gráficos e decisões exploratórias usam só treino.

## 4. Análise exploratória e seleção

{eda_text}

![Boxplots no treino](../graficos/02_boxplots_treino.png)

![Correlações no treino](../graficos/04_correlacoes_treino.png)

{rank_md}

O ranking é descritivo, ajustado somente no treino. Os valores-p exploratórios ficam no CSV e não foram usados para uma afirmação confirmatória. Filtro ANOVA considera cada atributo isoladamente, pode reter medidas redundantes e ignorar contribuições conjuntas. A escolha k=3 é um comparador predefinido, não uma seleção feita no teste. Não criamos novas medidas porque a pergunta está definida sobre as sete originais. PCA/LDA não são necessários para manter regras interpretáveis.

## 5. Modelagem e validação

Árvore de decisão Gini, escolhida pela adequação à classificação numérica, não linearidade e interpretabilidade. Pandas prepara as tabelas; scikit-learn ajusta os estimadores. A referência Dummy usa a classe mais frequente. Duas árvores iniciais com folha mínima 1 e profundidade irrestrita comparam todos os atributos a k=3.

{tuning_text}

{cv_md}

{chosen_text}

Parâmetros e pipeline são salvos antes das previsões no teste. Os quatro modelos são avaliados no mesmo teste apenas nesse estágio final, para uma comparação previamente definida. As métricas de teste não orientam mudanças posteriores.

## 6. Resultados finais

{test_md}

{class_md}

Precisão, recall e F1 são calculados por classe. F1 macro é a média dos três F1. Suporte é o número de exemplos reais. Acurácia e F1 macro são frações entre 0 e 1, exceto onde mostramos porcentagem. Os arquivos `metricas_por_classe_*.csv` e `matriz_confusao_*.csv` trazem os quatro modelos, incluindo a referência com classes nunca previstas tratadas como zero.

{cm_md}

![Comparação final](../graficos/08_comparacao_modelos.png)

![Matriz final](../graficos/07_matriz_confusao_final.png)

{outcome_text}

## 7. Análise dos erros

{err_md}

{errors_text}

{errors_md}

Todos os sete valores de cada caso e os escores ficam em `resultados/erros_teste.csv`. Os caminhos usam precisão maior que o gráfico para facilitar rastreio. Escores de folha não foram calibrados. Vizinhos ilustram proximidade, sem provar o motivo biológico do erro.

## 8. Interpretação, conclusão e limites

![Árvore final](../graficos/09_arvore_final.png)

As árvores iniciais tiveram acurácia de treino de 100%. A refinada apresentou {pct(final['acuracia_treino'])} no treino completo e {pct(s['validacao'][-1]['acuracia_cv_media'])} na validação média. O intervalo entre treino e validação ainda indica sensibilidade. Poda e limitação de profundidade foram escolhidas por validação, sem garantir eliminar o sobreajuste. As importâncias Gini descrevem os cortes desta árvore e não medem causalidade ou relevância independente de correlação.

Resposta: **sim, os resultados desta avaliação sustentam que as medidas permitem prever as variedades melhor que a regra simples**. A hipótese operacional foi sustentada, com {pct(final['acuracia_teste'])} contra 33,33%. Não concluímos que três atributos bastam ou que este classificador é o melhor possível.

{limitations}

## 9. Ciclo de vida, implantação e monitoramento

O ciclo de vida consultado na aula vai até implantação e monitoramento. Acrescentamos inferência local em lote com o modelo serializado e referência estatística do treino. A demonstração lê medidas válidas e produz classes e escores. O pipeline continua ajustado somente nos 168 exemplos de treino.

O plano em `relatorios/plano_monitoramento.md` propõe validar cada lote, revisar distribuições mensalmente, medir desempenho quando houver rótulos independentes e retreinar com nova reserva de teste quando necessário. Os gatilhos propostos são sugestões operacionais a validar, não resultados de produção. Nenhum monitoramento contínuo foi executado. A conferência de páginas e diferenças está em `relatorios/aderencia_slide.md`.

## 10. Cronograma e arquivos

{markdown_table(['Marco', 'Registro'], [['13/11/2026', 'Auditoria, EDA e candidatos'], ['20/11/2026', 'Divisão e modelos iniciais, com envio no feriado'], ['27/11/2026', 'Busca no treino, teste final e erros'], ['04/12/2026', 'Relatório, apresentação e implantação local']])}

As quatro entregas estão preparadas antecipadamente. O registro original de 06/11 foi preservado. Não houve submissão externa. `resultados/manifesto_arquivos.csv` lista os arquivos finais com tamanho e hash, e `README.md` organiza a navegação.

## 11. Reprodução

Python {s['python']}. Versões usadas: {', '.join(f'{k} {v}' for k,v in s['versoes'].items())}. Dependências completas em `requirements.txt`.

```powershell
Set-Location 'D:\\Dev - Falculdade\\machine-learning-av2'
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe src/analise_seeds.py
.\\.venv\\Scripts\\python.exe src/gerar_relatorios.py
.\\.venv\\Scripts\\python.exe src/prever.py dados/exemplo_inferencia.csv --saida resultados/previsoes_exemplo.csv
.\\.venv\\Scripts\\python.exe src/verificar_resultados.py
```

O exemplo de inferência é um teste de interface com três linhas de treino, sem nova avaliação de generalização. Reexecutar recompõe o mesmo experimento congelado, não cria um novo teste independente. O gerador de apresentação usa Node.js com o runtime `@oai/artifact-tool` do Codex, como documentado no README.

## 12. Referências

- UCI e citação: https://archive.ics.uci.edu/dataset/236/seeds e https://doi.org/10.24432/C5H30K
- Mapa dos códigos ODRF: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd
- Métodos: https://scikit-learn.org/stable/common_pitfalls.html e documentação oficial das classes usadas.
- Material local: `slide-machine-learning.pdf`, páginas físicas 10-130, especialmente 52, 68-70, 74, 77-79, 81, 96-98 e 130.
- Evidência e observações de origem: `fontes/referencias.md` e `fontes/ODRF_seeds.Rd`.
"""
    write("relatorios/relatorio_final.md", full)

    # PDF paginado, com texto pesquisável e tabelas reais.
    font_dir = Path("C:/Windows/Fonts")
    if (font_dir / "arial.ttf").exists():
        pdfmetrics.registerFont(TTFont("Project", str(font_dir / "arial.ttf")))
        pdfmetrics.registerFont(TTFont("ProjectBold", str(font_dir / "arialbd.ttf")))
        pdfmetrics.registerFontFamily("Project", normal="Project", bold="ProjectBold", italic="Project", boldItalic="ProjectBold")
        body_font, bold_font = "Project", "ProjectBold"
    else:
        body_font, bold_font = "Helvetica", "Helvetica-Bold"
    styles = getSampleStyleSheet()
    for name in ["Normal", "BodyText", "Heading1", "Heading2", "Title"]:
        styles[name].fontName = bold_font if name in ["Title", "Heading1", "Heading2"] else body_font
    styles["BodyText"].fontSize = 10; styles["BodyText"].leading = 14; styles["BodyText"].spaceAfter = 9
    styles["Heading1"].fontSize = 20; styles["Heading1"].leading = 25; styles["Heading1"].textColor = colors.HexColor("#24594f")
    styles["Heading2"].fontSize = 12; styles["Heading2"].leading = 17
    styles.add(ParagraphStyle(name="SmallProject", fontName=body_font, fontSize=8, leading=11, spaceAfter=7))
    story=[]
    def para(text, style="BodyText"):
        story.append(Paragraph(escape(text).replace("\n", "<br/>"), styles[style]))
    def heading(title):
        para(title, "Heading1"); story.append(Spacer(1, 8))
    def table(headers, rows, widths=None, size=8.5):
        small = ParagraphStyle(name="CellProject", fontName=body_font, fontSize=size, leading=size+3)
        vals = [[Paragraph(escape(str(x)), small) for x in row] for row in [headers, *rows]]
        t=Table(vals, colWidths=widths, repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e1ece7")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("BOTTOMPADDING",(0,0),(-1,-1),7),
            ("TOPPADDING",(0,0),(-1,-1),7),("LINEBELOW",(0,0),(-1,0),.6,colors.HexColor("#24594f")),
            ("LINEBELOW",(0,1),(-1,-1),.3,colors.HexColor("#dddddd"))]))
        story.append(t); story.append(Spacer(1,10))
    def pic(name, width, caption=None):
        from PIL import Image as PILImage
        path=ROOT / "graficos" / name
        with PILImage.open(path) as im:
            w,h=im.size
        story.append(Image(str(path), width=width, height=width*h/w))
        if caption:
            para(caption, "SmallProject")
    def page(): story.append(PageBreak())
    heading("AV2 Seeds\nClassificação de variedades de trigo")
    para("Gabriel Felix\nExecução antecipada: 06/11/2026\nEntrega final prevista: 04/12/2026")
    para("Pergunta e hipótese", "Heading2")
    para("As sete características geométricas do dataset Seeds permitem prever a variedade de um grão de trigo?")
    para("Hipótese: um modelo treinado com essas características supera uma regra que sempre prevê uma única classe.")
    para("Resultado observado", "Heading2"); para(outcome_text)
    para("Escopo dos dados", "Heading2"); para(source_text)
    para("As entradas são sete medidas numéricas. A saída é uma das três classes. Este trabalho usa a tabela já extraída pelos pesquisadores, sem processamento de imagens. Não há submissão externa realizada.")
    page(); heading("1. Qualidade e preparação")
    para(quality_text)
    table(["Verificação", "Resultado"], [["Dimensões", "210 grãos, sete atributos e classe"],["Faltantes / duplicatas / medidas não positivas", "0 / 0 / 0"],["Bruto", "Conteúdo preservado por SHA-256"],["Transformação", "Nomes e tipos explícitos, nenhuma exclusão"]], [310,180])
    para("A diferença máxima da compacidade para 4πA/P² é 0,001020. Não houve recálculo. As unidades físicas não foram presumidas. Identificador da linha, nome da variedade e partição ficam fora das entradas do modelo.")
    para(method_text)
    para("No treino, seis grãos têm extremos pelo critério de 1,5 IQR: quatro em compacidade e dois em assimetria. Mantivemos os valores, pois não há evidência de medição incorreta.")
    pic("02_boxplots_treino.png", 490, "Figura 1. Distribuições por classe nos 168 grãos de treino.")
    page(); heading("2. EDA e seleção de atributos")
    para(eda_text)
    pic("04_correlacoes_treino.png", 285, "Figura 2. Correlações de Pearson no treino.")
    table(["Atributo", "F ANOVA", "k=3"], rank_rows, [280,110,100])
    para("O filtro ANOVA considera cada variável isoladamente. Os três candidatos incluem área e perímetro, fortemente correlacionados. Seletores reaprendem o ranking dentro de cada fold. Valores-p são exploratórios, sem uso confirmatório.")
    page(); heading("3. Treinamento e refinamento")
    para("A referência Dummy prevê a classe mais frequente. Árvores iniciais comparam os sete atributos a k=3. Usamos Gini, semente 42, folha mínima 1 e profundidade irrestrita nessa comparação inicial.")
    para(tuning_text)
    table(["Modelo", "Acurácia CV", "F1 macro CV", "DP do F1"], cv_rows, [190,100,100,100])
    para(chosen_text)
    para("As árvores iniciais alcançaram 100% no treino interno, com desempenho inferior na validação. A refinada alcançou 98,66% no treino médio dos folds e 92,26% na validação. Há sensibilidade residual, mesmo com a poda escolhida.")
    para("A configuração final e o pipeline são salvos antes de gerar previsões no teste. A comparação dos quatro modelos no teste é descritiva e predefinida. Não há ajuste posterior orientado por essa avaliação.")
    page(); heading("4. Avaliação final")
    table(["Modelo", "Treino", "Teste", "F1 macro", "Acertos"], test_rows, [170,80,80,80,80])
    table(["Classe", "Precisão", "Recall", "F1", "Suporte"], class_rows, [130,95,95,85,85])
    pic("07_matriz_confusao_final.png", 310, "Figura 3. Linhas são classes reais, colunas são classes previstas.")
    para(outcome_text)
    para("Precisão: acertos entre previsões da classe. Recall: acertos entre exemplos reais da classe. F1 combina ambos. As três classes têm o mesmo peso no F1 macro.", "SmallProject")
    page(); heading("5. Casos classificados incorretamente")
    table(["Linha", "Real", "Previsto", "Folha", "Treino na folha"], error_rows, [55,100,110,65,160])
    para(errors_text)
    for e in s["erros_finais"]:
        para(f'Linha {e["linha_origem"]}: {e["variedade_real"]} como {e["variedade_prevista"]}', "Heading2")
        para("Caminho: " + "; ".join(e["caminho"]) + ".")
        neighbor = e["vizinhos_treino"][0]
        para(f'Vizinho mais próximo no treino: linha {neighbor["linha"]}, classe {neighbor["classe"]}, distância padronizada {dec(neighbor["distancia_padronizada_7_atributos"],3)}. A padronização usa somente estatísticas do treino para diagnóstico.', "SmallProject")
    para("Todos os valores, caminhos e três vizinhos de cada erro estão nos arquivos erros_teste.csv e erros_detalhados.json. Não modificamos o modelo após esta leitura.")
    page(); heading("6. Interpretação e conclusão")
    pic("09_arvore_final.png", 490, "Figura 4. Árvore final treinada nos 168 exemplos. Regras em texto também disponíveis.")
    para("A hipótese foi sustentada nesta avaliação: a árvore refinada supera a regra de classe única. O subconjunto inicial de três atributos teve desempenho inferior. A entrada final mantém sete medidas, e cinco aparecem nos cortes.")
    para(limitations)
    page(); heading("7. Ciclo de vida e entregas")
    table(["Marco", "Trabalho preparado"], [["13/11", "Limpeza, pré-processamento, EDA e candidatos"],["20/11", "Divisão e treinamento. Envio previsto no feriado"],["27/11", "Refinamento no treino, avaliação final e erros"],["04/12", "Relatório, apresentação e inferência local"]], [75,415])
    para("O slide foi consultado da página física 10 à 130. As p. 52 e 130 incluem implantação e monitoramento, ausentes no encerramento do plano inicial. As p. 68-70 e 81 reservam teste ao fim. A p. 74 pede referência simples, e as p. 77-79 descrevem múltiplas métricas.")
    para("Implantação local executada", "Heading2")
    para("Exportamos o pipeline Joblib e um programa de previsão em lote. Ele valida entradas e sinaliza valores fora dos intervalos do treino. O exemplo usa três grãos já conhecidos e verifica a interface. As proporções nas folhas não são probabilidades calibradas.")
    para("Monitoramento proposto", "Heading2")
    para("Validar cada novo lote, revisar distribuições mensalmente e avaliar métricas quando existirem rótulos independentes. Investigar mudanças de instrumento, origem e unidade. O plano detalhado propõe gatilhos a validar e nova reserva de teste para versões futuras. Não há sistema de produção ou medições de drift observadas.")
    para("Arquivos e próximos passos", "Heading2")
    para("O README e o manifesto organizam entregas, fontes, dados derivados, gráficos, tabelas, código e modelo. As quatro entregas estão preparadas antecipadamente. Gabriel deve revisar os materiais e realizar os envios nas datas previstas.")
    page(); heading("8. Reprodução e referências")
    para(f'Python {s["python"]}. Versões: ' + ", ".join(f"{k} {v}" for k,v in s["versoes"].items()) + ".")
    para("Na raiz do projeto, criar um ambiente Python 3.12, instalar requirements.txt e executar os comandos abaixo. O README contém os comandos PowerShell completos e a geração da apresentação.")
    for cmd in ["python -m pip install -r requirements.txt", "python src/analise_seeds.py", "python src/gerar_relatorios.py", "python src/prever.py dados/exemplo_inferencia.csv --saida resultados/previsoes_exemplo.csv", "python src/verificar_resultados.py"]:
        para(cmd, "SmallProject")
    para("O código resolve caminhos a partir da própria pasta do projeto. Reexecutar reproduz o mesmo experimento, sem transformar o teste conhecido em uma nova avaliação independente.")
    para("Referências e rastreabilidade", "Heading2")
    para("Charytanowicz, M., Niewczas, J., Kulczycki, P., Kowalski, P., & Lukasik, S. (2010). Seeds [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5H30K. Licença CC BY 4.0.")
    for url in ["https://archive.ics.uci.edu/dataset/236/seeds", "https://doi.org/10.24432/C5H30K", "https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd", "https://scikit-learn.org/stable/common_pitfalls.html"]:
        para(url, "SmallProject")
    para("Material da disciplina: slide-machine-learning.pdf, páginas físicas 10-130. Mapa detalhado em relatorios/aderencia_slide.md. Cópia da documentação de classes em fontes/ODRF_seeds.Rd.")
    para("SHA-256 do bruto", "Heading2")
    digest=s["auditoria"]["sha256_antes"]
    para(digest[:32]+"\n"+digest[32:], "SmallProject")
    para("Nenhum conteúdo do bruto ou da entrega inicial foi alterado. Os resultados numéricos provêm da execução local, registrados em resultados/resumo_execucao.json.")

    def footer(canvas, doc):
        canvas.setFont(body_font, 8); canvas.setFillColor(colors.HexColor("#666666"))
        canvas.drawString(1.8*cm, 1.1*cm, "AV2 Seeds - Gabriel Felix - execução em 06/11/2026")
        canvas.drawRightString(A4[0]-1.8*cm, 1.1*cm, str(doc.page))
    doc=SimpleDocTemplate(str(ROOT / "relatorios/relatorio_final.pdf"), pagesize=A4,
                         rightMargin=1.8*cm, leftMargin=1.8*cm, topMargin=1.6*cm, bottomMargin=1.8*cm,
                         title="AV2 Seeds - Relatório final", author="Gabriel Felix")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Entregas Markdown e relatório PDF gerados a partir do resumo executado.")


if __name__ == "__main__":
    main()
