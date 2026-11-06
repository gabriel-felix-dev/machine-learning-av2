# Roteiro da apresentação final

Gabriel Felix. Sugestão: 10 a 12 minutos, ajustável ao tempo da disciplina. Execução em 06/11/2026, entrega prevista 04/12/2026.

## 1. Seeds: classificação de variedades de trigo

Apresentar o tema, autor e escopo acadêmico. Execução antecipada em 06/11/2026, entrega final prevista em 04/12/2026.

Fonte: UCI Seeds: https://archive.ics.uci.edu/dataset/236/seeds. DOI: https://doi.org/10.24432/C5H30K. Mapa dos códigos: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd. Consulta em 06/11/2026. A versão ODRF tem 209 linhas e só foi usada para confirmar o mapa. Dados analisados: 210 linhas da cópia UCI local.

## 2. Pergunta e hipótese

A pergunta e a hipótese preservam a entrega inicial. Explicar classificação supervisionada: conhecemos as variedades nos exemplos e queremos prever a classe de novos grãos. A hipótese é operacional, comparada com uma regra de classe única.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 3. 210 grãos e três variedades

A UCI documenta sete medidas extraídas por análise de imagens de raios X. Não processamos imagens neste projeto. Os sete valores alimentam X e a classe nominal alimenta y. Os códigos foram confirmados na documentação dos autores do ODRF.

Fonte: UCI Seeds: https://archive.ics.uci.edu/dataset/236/seeds. DOI: https://doi.org/10.24432/C5H30K. Mapa dos códigos: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd. Consulta em 06/11/2026. A versão ODRF tem 209 linhas e só foi usada para confirmar o mapa. Dados analisados: 210 linhas da cópia UCI local.

## 4. Auditoria e preparação dos dados

O pandas lê separadores por espaços ou tabulações, nomeia as colunas e valida tipos. O arquivo bruto mantém o mesmo SHA-256. Seis grãos do treino foram sinalizados pelo IQR, sem evidência de erro. Não excluímos valores ou linhas. A árvore não requer padronização de escala.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 5. Medidas separam grupos com sobreposição

Dispersão calculada somente nos 168 grãos de treino. Rosa tende a ter medidas maiores, mas as variedades se sobrepõem. Este gráfico usa duas das sete medidas e não representa a regra completa do classificador. As unidades físicas não foram presumidas porque não estão explicitadas na ficha consultada.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 6. Seleção de atributos no treino

ANOVA univariada classifica medidas pelo contraste entre classes. Candidatos k=3: área, perímetro e largura. A correlação área/perímetro é 0,9945. Retirar atributos com base só no ranking pode descartar informação complementar. O Pipeline reaprende o ranking dentro de cada fold. Valores-p são exploratórios, sem inferência confirmatória.

Fonte: resultados/ranking_atributos_treino.csv. SelectKBest: https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html

## 7. Treino, validação e teste reservado

A divisão estratificada 80/20 com semente 42 acontece antes da seleção supervisionada e da EDA orientada a decisões, apesar de constar formalmente em 20/11. Os mesmos cinco folds de treino são usados nas comparações. O teste só é aberto depois de salvar a configuração final.

Fonte: Protocolo local. Aula p. 68-70 e 81. https://scikit-learn.org/stable/common_pitfalls.html

## 8. Validação favorece a árvore refinada

Médias dos cinco folds exclusivamente no treino. Referência 0,1644; árvore 7 0,8984; k=3 0,8340; refinada 0,9231. Desvio padrão de F1 macro da refinada: 0,0527. A busca seleciona entre 240 configurações, então seu melhor CV pode ser otimista. Nenhum resultado de teste orienta a escolha.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 9. 240 configurações comparadas no treino

Grade declarada antes de avaliar o teste: 6 escolhas de k, 5 de profundidade, 4 de folha mínima e 2 de poda. Total 240 configurações e 1.200 ajustes de CV. Desempate predefinido por acurácia, menos atributos, menor profundidade, maior folha mínima e maior poda. Modelo final com sete entradas, profundidade 5 e oito folhas.

Fonte: resultados/busca_hiperparametros.csv e modelo_congelado.json. Aula p. 96.

## 10. 39 acertos em 42 grãos no teste

Os quatro modelos foram avaliados no teste somente após o congelamento final. Referência 14/42, árvore 7 37/42, árvore k3 35/42, refinada 39/42. Ganho final de 59,52 pontos percentuais sobre referência. F1 macro final 0,9263. Wilson 95%: 80,99% a 97,54%. ROC um-contra-resto AUC macro 0,9226. Não houve novo ajuste após consultar os resultados.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 11. Kama concentra os três erros finais

A matriz usa linhas reais e colunas previstas. Kama tem 11 acertos, um erro como Rosa e dois como Canadian. Rosa e Canadian têm recall de 100%, mas recebem falsos positivos de Kama. Por isso a precisão de Rosa é 93,33% e Canadian 87,50%. Cada classe tem 14 grãos de suporte. F1 de Kama 0,88, Rosa 0,9655 e Canadian 0,9333.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 12. Análise dos casos incorretos

Linhas rastreáveis do arquivo bruto, começando em 1. Linhas 24 e 62 são Kama em uma folha com 48 Canadian de treino, e caem na região de área pequena. Linha 38 alcança uma folha Rosa com apenas um exemplo de treino. Os vizinhos nos sete atributos incluem classes diferentes. Todas essas folhas erradas são puras no treino, então pureza não é certeza. Não há base para alegar erro de rótulo ou causa biológica. Caminhos e atributos completos estão nos arquivos de erros.

Fonte: Resultados locais: resultados/resumo_execucao.json

## 13. Regras interpretáveis e limites da avaliação

A árvore recebe sete medidas, mas os cortes finais usam área, comprimento, largura, assimetria e sulco. A regra principal classifica sulco acima de 5,5755 como Rosa. No treino completo há 98,81% de acurácia e a validação média é 92,26%. O risco de sobreajuste persiste. O teste é pequeno, uma única divisão, e a origem experimental é limitada. Um novo local, safra ou instrumento exige nova validação externa.

Fonte: UCI Seeds: https://archive.ics.uci.edu/dataset/236/seeds. DOI: https://doi.org/10.24432/C5H30K. Mapa dos códigos: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd. Consulta em 06/11/2026. A versão ODRF tem 209 linhas e só foi usada para confirmar o mapa. Dados analisados: 210 linhas da cópia UCI local. Modelo: modelos/regras_arvore.txt.

## 14. Implantação local e monitoramento

As páginas 52, 97, 98 e 130 da aula ampliaram o roteiro com implantação e monitoramento. Executado: pipeline Joblib, inferência CSV em lote e referência do treino. A demonstração usa três linhas de treino e apenas verifica a interface. Planejado: qualidade por lote, revisão mensal de distribuição e métricas com novos rótulos. Não houve publicação de API nem observação de drift. Gatilhos no plano são propostas a calibrar.

Fonte: slide-machine-learning.pdf, p. 52, 97, 98 e 130. relatorios/plano_monitoramento.md.

## 15. A hipótese foi sustentada nesta avaliação

Resposta à pergunta: as sete medidas permitem prever variedades melhor que a regra simples nesta avaliação. 92,86% contra 33,33%, ganho 59,52 pontos percentuais. Evitar generalizar para qualquer origem ou afirmar melhor algoritmo universal. O relatório contém reprodutibilidade, erros, limites e comparação completa. As entregas estão preparadas antecipadamente para os marcos de 13/11, 20/11, 27/11 e 04/12, com envio no feriado de 20/11 a cargo do aluno.

Fonte: UCI Seeds: https://archive.ics.uci.edu/dataset/236/seeds. DOI: https://doi.org/10.24432/C5H30K. Mapa dos códigos: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd. Consulta em 06/11/2026. A versão ODRF tem 209 linhas e só foi usada para confirmar o mapa. Dados analisados: 210 linhas da cópia UCI local. Métodos: https://scikit-learn.org/stable/common_pitfalls.html.
