# Entrega de 04/12/2026 - Relatório e apresentação final

Material preparado antecipadamente em 06/11/2026. A data no título identifica o marco do cronograma, não uma execução futura já ocorrida. Não houve envio à plataforma da disciplina.

## Resultados e conclusão

Pergunta preservada: **As sete características geométricas do dataset Seeds permitem prever a variedade de um grão de trigo?**

A árvore refinada acertou 39 de 42 grãos: acurácia 92,86% e F1 macro 0,9263. A referência sempre prevê Kama no treino completo e acerta 14/42 (33,33%). O ganho foi de 59,52 pontos percentuais. O intervalo de Wilson de 95% da acurácia é 80,99% a 97,54%, sob aproximação binomial para este teste. AUC macro um-contra-resto: 0,9226. AUC mede ordenação dos escores, não a taxa de acertos.

Sim, os resultados sustentam a hipótese operacional nesta divisão: o modelo supera a regra que sempre prevê uma classe. O subconjunto de três atributos não foi superior à entrada completa. O teste contém apenas 42 exemplos e uma única divisão. Um erro representa 2,38 pontos percentuais de acurácia e 7,14 pontos no recall de uma classe. Não há avaliação em nova safra, local, instrumento ou protocolo de medição. A UCI descreve coleta em campos experimentais em Lublin. A hipótese fica sustentada nesta divisão, sem demonstrar desempenho universal, causalidade ou superioridade sobre todos os classificadores. A busca escolheu uma folha mínima de 1, mantendo risco local mesmo com poda. O teste já consultado não serve como avaliação inédita de versões futuras. Não fizemos teste formal de significância nem apresentamos um valor-p como prova da hipótese.

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
