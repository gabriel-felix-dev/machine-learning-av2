# Implantação local e plano de monitoramento

## Executado

O pipeline final, ajustado nos 168 registros de treino, fica em `modelos/seeds_arvore.joblib`. A seleção faz parte do objeto salvo. `src/prever.py` lê um CSV com as sete colunas, valida os valores, retorna classe, nome e proporções de classe na folha. As proporções não são probabilidades calibradas de acerto. `modelos/referencia_treino.csv` guarda mínimos, máximos, médias e desvios dos atributos no treino. A ferramenta sinaliza linhas com medidas fora do intervalo observado no treino.

O processamento em lote constitui uma demonstração local de implantação. Não há API publicada, usuários de produção, novos grãos independentes ou monitoramento contínuo executado. O exemplo de inferência usa linhas já conhecidas e apenas verifica a interface, sem fornecer nova evidência de generalização.

## Planejado para eventual uso real

Responsável proposto: Gabriel Felix. A cada novo lote, registrar versão do modelo, data, identificação do lote e instrumento de medição, validação do esquema, faltantes, medidas não positivas, compacidade inválida e proporção fora do intervalo de treino. Rejeitar entradas inválidas antes da previsão. Investigar qualquer mudança de instrumento ou unidade de medida.

Revisar mensalmente os resumos e distribuições por atributo e a distribuição das classes previstas, sempre comparando com a referência do treino. Sinalizar para investigação quando mais de 10% das linhas de um lote saírem do intervalo do treino. Esse limiar é uma proposta operacional a calibrar com dados reais, não um detector estatístico de drift validado. Uma mudança isolada na distribuição de previsões também não comprova mudança da relação entre medidas e classes.

Quando houver pelo menos 30 rótulos novos por classe, calcular acurácia, precisão, recall, F1 macro e matriz de confusão por lote. Comparar com os resultados de referência considerando a incerteza amostral. Propor revisão se F1 macro cair 10 pontos percentuais ou se recall de alguma classe ficar abaixo de 80%. Esses gatilhos são propostas, não resultados observados nem garantias de segurança.

Na revisão, verificar medição e rótulos antes de retreinar. Separar novos lotes por origem, reservar nova avaliação externa e repetir seleção e ajuste apenas no desenvolvimento. O teste original já consultado permanece um registro histórico e não será tratado como teste inédito de novas versões. Versionar dados, código, dependências e modelo, manter a versão anterior disponível para reversão.
