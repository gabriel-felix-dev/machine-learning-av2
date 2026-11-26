# Roteiro da apresentação final — até 7 minutos

**Projeto:** classificação das variedades de trigo do dataset Seeds  
**Apresentadores:** Gabriel Felix e David Ryan  
**Duração planejada:** **6 minutos e 35 segundos**, com 25 segundos de margem.  
**Slides:** `apresentacao_final.pptx` (8 slides).

Fale com suas próprias palavras. As frases abaixo são uma referência para ensaiar; as marcações de tempo ajudam a manter o ritmo. Se a apresentação for em dupla, a troca de apresentador pode acontecer depois do slide 4.

## Slide 1 — Tema e pergunta (0:00–0:30, 30 s)

> Nosso projeto tenta identificar a variedade de um grão de trigo a partir de suas medidas. Usamos o dataset Seeds e comparamos três variedades: Kama, Rosa e Canadian. A pergunta é: essas medidas são suficientes para fazer uma previsão melhor do que uma regra muito simples?

**Ponto no slide:** mostre o título e diga o nome do projeto. Não explique ainda o algoritmo.

## Slide 2 — Dados e hipótese (0:30–1:15, 45 s)

> A base da UCI tem 210 grãos, 70 de cada variedade. Cada grão possui sete medidas geométricas, como área, perímetro e largura, além da classe correta. Como as classes têm o mesmo tamanho, uma regra que sempre responde uma única variedade acertaria aproximadamente 33,3%. Nossa hipótese é que um modelo treinado com as medidas supera essa referência.

**Ponto no slide:** mostre as três barras iguais e o número 33,3%.

## Slide 3 — Preparação e divisão (1:15–2:00, 45 s)

> Conferimos os dados e não encontramos registros que precisassem ser removidos. Antes de escolher o modelo, separamos 168 grãos para treino e validação e guardamos 42 para o teste final. Mantivemos a mesma proporção das três variedades em cada grupo. A análise do treino indicou quatro medidas úteis: área, perímetro, largura e comprimento do sulco.

**Ponto no slide:** aponte para 168 e 42. Diga que o teste ficou reservado durante as escolhas.

## Slide 4 — Escolha do modelo (2:00–3:00, 60 s)

> Com os 168 grãos de treino, comparamos uma regra simples, uma árvore de decisão e regressão logística. Fizemos validação cruzada em cinco partes: em cada rodada, o modelo aprende com uma parte do treino e é conferido em outra. Usamos o F1 macro para dar o mesmo peso às três variedades. A regressão logística com sete medidas teve F1 médio de 0,9286, e com quatro teve 0,9276. Como a diferença foi pequena dentro da variação observada, escolhemos quatro medidas para manter o modelo mais simples.

**Ponto no slide:** destaque as duas barras da regressão. Esses números são **do treino**, não do teste final.

## Slide 5 — Refino (3:00–3:50, 50 s)

> Depois ajustamos a regularização da regressão logística, controlada pelo valor C. Testamos cinco valores, sempre usando apenas o treino. C igual a 10 teve o maior F1 macro médio na validação, 0,9462. Treinamos a versão final com os 168 grãos e salvamos a configuração antes de abrir o conjunto de teste. Assim, o teste não influenciou essa escolha.

**Ponto no slide:** aponte para C=10 e para a linha destacada. Não entre em detalhes matemáticos dos coeficientes.

## Slide 6 — Resultado final (3:50–4:40, 50 s)

> Só depois de fixar o modelo usamos os 42 grãos reservados. Ele acertou 38, chegando a 90,48% de acurácia. O F1 macro no teste foi 0,9007. A regra simples acertaria 14 dos 42, ou 33,33%. O resultado sustenta nossa hipótese para esta divisão dos dados. Ainda precisamos olhar onde aconteceram os quatro erros.

**Ponto no slide:** pause brevemente em **38 de 42**. Não chame 0,9462 de resultado final; esse era o valor de validação.

## Slide 7 — Análise dos erros (4:40–5:50, 70 s)

> Esta é a matriz de confusão. As linhas mostram a classe real e as colunas mostram a previsão. O modelo reconheceu todos os grãos Rosa e Canadian do teste. Os quatro erros foram grãos Kama: três previstos como Canadian e um como Rosa. Por isso, o recall de Kama foi 71,43%, ou dez Kama encontrados entre 14. Ao olhar as medidas, os três confundidos com Canadian têm área e largura próximas dos valores centrais Canadian no treino. O outro tem medidas de tamanho próximas das Rosa. Isso descreve a confusão, mas não prova a causa dos erros.

**Ponto no slide:** leia primeiro a linha Kama, da esquerda para a direita. Não precisa ler todas as nove células.

## Slide 8 — Conclusão e limites (5:50–6:35, 45 s)

> A resposta à pergunta inicial é sim, nesta divisão: o modelo superou a regra simples por uma margem grande. Ao mesmo tempo, o teste tem só 42 grãos, e Kama foi a classe mais difícil. Os dados vêm de uma origem específica, então não podemos garantir o mesmo resultado para outras safras ou locais. Uma continuação justa seria coletar grãos independentes e avaliar o modelo neles. Obrigado.

**Ponto no slide:** conclua com a hipótese e com a limitação principal. Termine antes dos 7 minutos.

## Se houver perguntas depois da apresentação

- **O que é F1 macro?** É a média do F1 das três classes, com a mesma importância para cada uma. O F1 combina precisão e recall.
- **Por que guardar o teste?** Para avaliar, ao final, exemplos que não orientaram a escolha do modelo.
- **Por que quatro medidas, se sete tiveram média ligeiramente maior?** A diferença na validação foi pequena. Usamos a regra de 1 erro padrão para preferir a versão mais simples.
- **O ajuste de C melhorou o teste?** Não medimos o modelo anterior no teste. Podemos afirmar que C=10 teve melhor resultado na validação usada para o refino; não podemos atribuir a ele um ganho de teste comprovado.
- **Podemos ajustar o modelo para corrigir esses quatro erros?** Podemos investigar os casos, mas uma nova versão exigiria outro conjunto independente para uma avaliação justa.

## Fontes dos números

- Dataset: [UCI Seeds](https://archive.ics.uci.edu/dataset/236/seeds).
- Divisão e comparação inicial: [`entrega_20-11_seeds.md`](../entrega_20-11_seeds.md), [`resultados/validacao_20-11.csv`](../resultados/validacao_20-11.csv).
- Refino, teste e erros: [`entrega_27-11_seeds.md`](../entrega_27-11_seeds.md), [`resultados/resumo_teste_27-11.json`](../resultados/resumo_teste_27-11.json), [`resultados/matriz_confusao_27-11.csv`](../resultados/matriz_confusao_27-11.csv).
