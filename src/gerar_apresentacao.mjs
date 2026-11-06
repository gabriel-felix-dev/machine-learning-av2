// Execute com Node.js e @oai/artifact-tool fornecidos pelo runtime do Codex.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const modules = process.env.CODEX_RUNTIME_NODE_MODULES || 'C:/Users/Gabriel/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const skillDir = process.env.CODEX_PRESENTATION_SKILL || 'C:/Users/Gabriel/.codex/plugins/cache/openai-primary-runtime/presentations/26.1104.12130/skills/presentations';
const python = process.env.CODEX_RUNTIME_PYTHON || 'C:/Users/Gabriel/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES = modules;
const require = createRequire(path.join(modules, 'package.json'));
const { FileBlob, Presentation, PresentationFile } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const { finalizePresentation, applyPresentationChartFont } = await import(pathToFileURL(path.join(skillDir, 'container_tools/artifact_tool_utils.mjs')).href);
const s = JSON.parse(await fs.readFile(path.join(root, 'resultados/resumo_execucao.json'), 'utf8'));
const build = path.join(root, '.build/slides');
await fs.mkdir(build, {recursive:true});
await fs.mkdir(path.join(root, 'apresentacao'), {recursive:true});
const pct = n => (100*n).toFixed(2).replace('.', ',')+'%';
const dec = (n, digits=4) => n.toFixed(digits).replace('.', ',');
async function readCSV(relative) {
  const lines=(await fs.readFile(path.join(root,relative),'utf8')).trim().split(/\r?\n/);
  const header=lines.shift().split(',');
  return lines.map(line => Object.fromEntries(line.split(',').map((v,i)=>[header[i],v!=='' && Number.isFinite(Number(v))?Number(v):v])));
}
const trainX = await readCSV('dados/X_treino.csv');
const trainY = await readCSV('dados/y_treino.csv');
const yById = new Map(trainY.map(row=>[row.linha_origem,row.classe]));
const ranking = await readCSV('resultados/ranking_atributos_treino.csv');
const errors = await readCSV('resultados/erros_teste.csv');
const colors=['#27675E','#C68B31','#596D9B'];
const ink='#17372F', muted='#52635C', paper='#F9FAF6';
const presentation=Presentation.create({slideSize:{width:1280,height:720}});
const tableOwners=[], chartOwners=[], outline=[];
let shapeId=0;

function text(slide, value, x,y,w,h,size=28,bold=false,color=ink,name='body') {
  const shape=slide.shapes.add({geometry:'textbox',name:`${name}-${++shapeId}`,
    position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  shape.text=value;
  shape.text.style={typeface:'Arial',fontSize:size,bold,color,verticalAlignment:'top',insets:0,autoFit:'none',wrap:'square'};
  return shape;
}
function slide(title, note='', source='Resultados locais: resultados/resumo_execucao.json') {
  const sl=presentation.slides.add();
  sl.background.fill=paper;
  const number=presentation.slides.items.length;
  if(title) text(sl,title,64,46,1150,90,44,true,ink,'title');
  text(sl,String(number).padStart(2,'0'),1160,668,60,24,18,false,muted,'page');
  sl.speakerNotes.text=note+'\n\nFontes: '+source;
  outline.push({number,title,note,source});
  return sl;
}
function caption(sl, value, y=625) {text(sl,value,64,y,1110,45,20,false,muted,'caption');}
function chart(sl, type, config) {
  const c=sl.charts.add(type,{chartFill:paper,plotAreaFill:paper,
    chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},...config});
  applyPresentationChartFont(c,{fontFamily:'Arial'});
  chartOwners.push(presentation.slides.items.indexOf(sl)+1);
  return c;
}
function table(sl, values, x,y,w,h, widths, size=25) {
  const t=sl.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,values:values.map(row=>row.map(String)),columnWidths:widths});
  t.borders.assign({fill:'#D8E1DB',width:.5,style:'solid'});
  for(let r=0;r<values.length;r++) for(let c=0;c<values[0].length;c++) {
    const cell=t.getCell(r,c);
    cell.text.style={typeface:'Arial',fontSize:size,color:ink,bold:r===0,insets:10,verticalAlignment:'middle'};
    cell.fill=r===0?'#E1ECE5':paper;
  }
  tableOwners.push(presentation.slides.items.indexOf(sl)+1);
  return t;
}
const axis=(title, other={})=>({title:{text:title,textStyle:{fontSize:22}},textStyle:{fontSize:21,fill:muted},line:{fill:'#BCCBC1',width:1},...other});
const sourceUCI='UCI Seeds: https://archive.ics.uci.edu/dataset/236/seeds. DOI: https://doi.org/10.24432/C5H30K. Mapa dos códigos: https://raw.githubusercontent.com/liuyu-star/ODRF/master/man/seeds.Rd. Consulta em 06/11/2026. A versão ODRF tem 209 linhas e só foi usada para confirmar o mapa. Dados analisados: 210 linhas da cópia UCI local.';

// 1. Capa
{
 const sl=slide('', 'Apresentar o tema, autor e escopo acadêmico. Execução antecipada em 06/11/2026, entrega final prevista em 04/12/2026.',sourceUCI);
 outline.at(-1).title='Seeds: classificação de variedades de trigo';
 text(sl,'Seeds',64,115,1100,115,96,true);
 text(sl,'Classificação de\nvariedades de trigo',68,250,1100,195,62,true);
 text(sl,'Gabriel Felix\nMachine Learning, AV2',70,500,950,90,28,false,muted);
 text(sl,'Entrega final: 04/12/2026',70,620,1000,40,23,false,muted);
}
// 2. Pergunta
{
 const sl=slide('Pergunta e hipótese', 'A pergunta e a hipótese preservam a entrega inicial. Explicar classificação supervisionada: conhecemos as variedades nos exemplos e queremos prever a classe de novos grãos. A hipótese é operacional, comparada com uma regra de classe única.');
 text(sl,'As sete características geométricas\npermitem prever a variedade\nde um grão de trigo?',64,163,1140,230,46,true);
 text(sl,'Hipótese',64,430,1090,42,30,true);
 text(sl,'Um modelo treinado com essas medidas supera\na regra que sempre prevê uma única classe.',64,490,1120,90,30);
 caption(sl,'Referência esperada com classes equilibradas: aproximadamente 33,3% de acurácia.');
}
// 3. Fonte e composição
{
 const sl=slide('210 grãos e três variedades', 'A UCI documenta sete medidas extraídas por análise de imagens de raios X. Não processamos imagens neste projeto. Os sete valores alimentam X e a classe nominal alimenta y. Os códigos foram confirmados na documentação dos autores do ODRF.',sourceUCI);
 chart(sl,'bar',{position:{left:64,top:165,width:590,height:410},categories:['1 Kama','2 Rosa','3 Canadian'],
  series:[{name:'Grãos',values:[70,70,70],fill:colors[0],points:colors.map((fill,idx)=>({idx,fill}))}],
  hasLegend:false,barOptions:{direction:'column',gapWidth:110},
  xAxis:axis('Variedade'),yAxis:axis('Grãos',{min:0,max:80,majorUnit:20}),
  dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:25,bold:true,fill:ink}}});
 text(sl,'Sete atributos geométricos',710,180,500,55,30,true);
 text(sl,'Área, perímetro e compacidade\nComprimento e largura\nAssimetria e sulco',710,260,500,170,29);
 text(sl,'Alvo: variedade do trigo',710,465,500,50,29,true);
 caption(sl,'Fonte: UCI Seeds, DOI 10.24432/C5H30K. Códigos confirmados na documentação ODRF.');
}
// 4. Qualidade
{
 const sl=slide('Auditoria e preparação dos dados', 'O pandas lê separadores por espaços ou tabulações, nomeia as colunas e valida tipos. O arquivo bruto mantém o mesmo SHA-256. Seis grãos do treino foram sinalizados pelo IQR, sem evidência de erro. Não excluímos valores ou linhas. A árvore não requer padronização de escala.');
 table(sl,[['Verificação','Resultado'],['Valores ausentes','0'],['Linhas duplicadas','0'],['Medidas não positivas','0'],['Registros removidos ou corrigidos','0']],64,160,1152,325,[780,372],28);
 text(sl,'Seis grãos sinalizados como extremos no treino',64,520,1140,45,30,true);
 text(sl,'Mantivemos os valores por falta de evidência de erro de medição.',64,575,1140,50,27);
}
// 5. EDA
{
 const sl=slide('Medidas separam grupos com sobreposição', 'Dispersão calculada somente nos 168 grãos de treino. Rosa tende a ter medidas maiores, mas as variedades se sobrepõem. Este gráfico usa duas das sete medidas e não representa a regra completa do classificador. As unidades físicas não foram presumidas porque não estão explicitadas na ficha consultada.');
 chart(sl,'scatter',{position:{left:64,top:155,width:810,height:440},series:[1,2,3].map((k,i)=>{
  const rows=trainX.filter(r=>yById.get(r.linha_origem)===k);
  return {name:['Kama','Rosa','Canadian'][i],xValues:rows.map(r=>r.largura),values:rows.map(r=>r.sulco),fill:colors[i],line:{fill:'none',width:0},marker:{symbol:'circle',size:7,fill:colors[i]}};
 }),scatterOptions:{style:'marker'},hasLegend:true,legend:{position:'bottom',textStyle:{fontSize:22}},
 xAxis:axis('Largura do grão',{min:2.5,max:4.1}),yAxis:axis('Comprimento do sulco',{min:4.4,max:6.7})});
 text(sl,'Apenas treino',920,200,300,45,28,true);
 text(sl,'Rosa apresenta\nmedidas maiores\nem média.',920,275,290,140,28);
 text(sl,'Kama e Canadian\nse sobrepõem\nnesta projeção.',920,455,300,130,28);
 caption(sl,'Gráficos completos: histogramas, boxplots, correlação e dispersão.');
}
// 6. Seleção
{
 const sl=slide('Seleção de atributos no treino', 'ANOVA univariada classifica medidas pelo contraste entre classes. Candidatos k=3: área, perímetro e largura. A correlação área/perímetro é 0,9945. Retirar atributos com base só no ranking pode descartar informação complementar. O Pipeline reaprende o ranking dentro de cada fold. Valores-p são exploratórios, sem inferência confirmatória.','resultados/ranking_atributos_treino.csv. SelectKBest: https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html');
 chart(sl,'bar',{position:{left:64,top:165,width:790,height:430},categories:ranking.map(r=>r.atributo).reverse(),
  series:[{name:'F ANOVA',values:ranking.map(r=>r.F_ANOVA).reverse(),fill:colors[0]}],hasLegend:false,
  barOptions:{direction:'bar',gapWidth:40},xAxis:axis('Atributo'),yAxis:axis('F ANOVA',{min:0,max:520}),
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0',textStyle:{fontSize:21,fill:ink}}});
 text(sl,'Candidatos iniciais',910,190,310,70,29,true);
 text(sl,'Área\nPerímetro\nLargura',910,280,300,150,30);
 text(sl,'Área e perímetro:\nr = 0,9945',910,480,305,90,27,true);
 caption(sl,'O ranking descreve o treino. A validação decide quantos atributos manter.');
}
// 7. Avaliação sem vazamento
{
 const sl=slide('Treino, validação e teste reservado', 'A divisão estratificada 80/20 com semente 42 acontece antes da seleção supervisionada e da EDA orientada a decisões, apesar de constar formalmente em 20/11. Os mesmos cinco folds de treino são usados nas comparações. O teste só é aberto depois de salvar a configuração final.','Protocolo local. Aula p. 68-70 e 81. https://scikit-learn.org/stable/common_pitfalls.html');
 table(sl,[['Conjunto','Total','Kama','Rosa','Canadian'],['Treino','168','56','56','56'],['Teste reservado','42','14','14','14']],64,170,1152,205,[410,185,185,185,187],28);
 text(sl,'Validação cruzada de cinco folds somente no treino',64,430,1140,55,31,true);
 text(sl,'Seleção de atributos dentro do Pipeline em cada fold.\nAjustes e comparação usam F1 macro médio.\nTeste entra uma vez, após congelar o modelo.',64,515,1140,120,29);
}
// 8. Validação
{
 const sl=slide('Validação favorece a árvore refinada', 'Médias dos cinco folds exclusivamente no treino. Referência 0,1644; árvore 7 0,8984; k=3 0,8340; refinada 0,9231. Desvio padrão de F1 macro da refinada: 0,0527. A busca seleciona entre 240 configurações, então seu melhor CV pode ser otimista. Nenhum resultado de teste orienta a escolha.');
 chart(sl,'bar',{position:{left:64,top:160,width:1152,height:425},categories:['Referência','Árvore 7','Árvore k=3','Refinada'],
  series:[{name:'F1 macro médio',values:s.validacao.map(r=>Number(r.f1_macro_cv_media.toPrecision(12))),fill:colors[0]}],hasLegend:false,
  barOptions:{direction:'column',gapWidth:95},xAxis:axis('Modelo'),yAxis:axis('F1 macro médio',{min:0,max:1.05,numberFormatCode:'0.0'}),
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.000',textStyle:{fontSize:25,bold:true,fill:ink}}});
 caption(sl,'A versão com três atributos teve desempenho inferior à entrada completa.');
}
// 9. Refinamento
{
 const sl=slide('240 configurações comparadas no treino', 'Grade declarada antes de avaliar o teste: 6 escolhas de k, 5 de profundidade, 4 de folha mínima e 2 de poda. Total 240 configurações e 1.200 ajustes de CV. Desempate predefinido por acurácia, menos atributos, menor profundidade, maior folha mínima e maior poda. Modelo final com sete entradas, profundidade 5 e oito folhas.','resultados/busca_hiperparametros.csv e modelo_congelado.json. Aula p. 96.');
 table(sl,[['Parâmetro','Valores testados'],['Atributos (k)','2, 3, 4, 5, 6, todos'],['Profundidade','2, 3, 4, 5, irrestrita'],['Folha mínima','1, 2, 4, 6'],['Poda (ccp_alpha)','0 e 0,01']],64,170,685,340,[300,385],26);
 text(sl,'Configuração escolhida',800,180,410,80,30,true);
 text(sl,'7 atributos\nProfundidade máxima 5\nFolha mínima 1\nPoda 0,01',800,285,410,210,29);
 caption(sl,'Árvore final: profundidade observada 5 e oito folhas. Semente 42.');
}
// 10. Resultado final
{
 const sl=slide('39 acertos em 42 grãos no teste', 'Os quatro modelos foram avaliados no teste somente após o congelamento final. Referência 14/42, árvore 7 37/42, árvore k3 35/42, refinada 39/42. Ganho final de 59,52 pontos percentuais sobre referência. F1 macro final 0,9263. Wilson 95%: 80,99% a 97,54%. ROC um-contra-resto AUC macro 0,9226. Não houve novo ajuste após consultar os resultados.');
 chart(sl,'bar',{position:{left:64,top:160,width:830,height:425},categories:['Referência','Árvore 7','Árvore k=3','Refinada'],
  series:[{name:'Acurácia no teste',values:s.teste.map(r=>Number(r.acuracia_teste.toPrecision(12))),fill:colors[0]}],hasLegend:false,
  barOptions:{direction:'column',gapWidth:90},xAxis:axis('Modelo'),yAxis:axis('Acurácia',{min:0,max:1.05,numberFormatCode:'0%'}),
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{fontSize:24,bold:true,fill:ink}}});
 text(sl,pct(s.teste.at(-1).acuracia_teste),920,185,300,100,62,true);
 text(sl,'Acurácia final',920,305,300,50,27);
 text(sl,'F1 macro\n'+dec(s.teste.at(-1).f1_macro_teste),920,420,300,110,30,true);
 caption(sl,'Teste de 42 grãos. Intervalo de Wilson de 95% para acurácia: 80,99% a 97,54%.');
}
// 11. Classes e matriz
{
 const sl=slide('Kama concentra os três erros finais', 'A matriz usa linhas reais e colunas previstas. Kama tem 11 acertos, um erro como Rosa e dois como Canadian. Rosa e Canadian têm recall de 100%, mas recebem falsos positivos de Kama. Por isso a precisão de Rosa é 93,33% e Canadian 87,50%. Cada classe tem 14 grãos de suporte. F1 de Kama 0,88, Rosa 0,9655 e Canadian 0,9333.');
 text(sl,'Matriz de confusão',64,160,540,45,30,true);
 table(sl,[['Real / prevista','Kama','Rosa','Canadian'],...['Kama','Rosa','Canadian'].map((n,i)=>[n,...s.matrizes_confusao.arvore_refinada[i]])],64,225,552,300,[195,100,100,157],25);
 text(sl,'Métricas por classe',665,160,550,45,30,true);
 const rep=s.metricas_por_classe.arvore_refinada;
 table(sl,[['Classe','Precisão','Recall','F1'],...['Kama','Rosa','Canadian'].map(n=>[n,pct(rep[n].precision),pct(rep[n].recall),dec(rep[n]['f1-score'],3)])],665,225,551,300,[155,145,140,111],24);
 caption(sl,'Suporte: 14 grãos reais por classe. O recall de Kama é 78,57%.',570);
}
// 12. Erros
{
 const sl=slide('Análise dos casos incorretos', 'Linhas rastreáveis do arquivo bruto, começando em 1. Linhas 24 e 62 são Kama em uma folha com 48 Canadian de treino, e caem na região de área pequena. Linha 38 alcança uma folha Rosa com apenas um exemplo de treino. Os vizinhos nos sete atributos incluem classes diferentes. Todas essas folhas erradas são puras no treino, então pureza não é certeza. Não há base para alegar erro de rótulo ou causa biológica. Caminhos e atributos completos estão nos arquivos de erros.');
 const ordered=[24,62,38].map(id=>errors.find(row=>row.linha_origem===id));
 table(sl,[['Linha','Real','Previsão','Área','Sulco','Treino na folha'],...ordered.map(r=>[r.linha_origem,'Kama',r.prev_arvore_refinada===3?'Canadian':'Rosa',dec(r.area,2),dec(r.sulco,3),r.linha_origem===38?1:48])],64,180,1152,260,[100,170,210,170,170,332],25);
 text(sl,'A linha 38 revela fragilidade local',64,485,1130,50,32,true);
 text(sl,'Uma folha com apenas um exemplo classificou esse grão como Rosa.\nFolhas puras também erram em dados novos.',64,555,1130,90,28);
}
// 13. Interpretação
{
 const sl=slide('Regras interpretáveis e limites da avaliação', 'A árvore recebe sete medidas, mas os cortes finais usam área, comprimento, largura, assimetria e sulco. A regra principal classifica sulco acima de 5,5755 como Rosa. No treino completo há 98,81% de acurácia e a validação média é 92,26%. O risco de sobreajuste persiste. O teste é pequeno, uma única divisão, e a origem experimental é limitada. Um novo local, safra ou instrumento exige nova validação externa.',sourceUCI+' Modelo: modelos/regras_arvore.txt.');
 text(sl,'Um exemplo de regra aprendida',64,175,1140,50,31,true);
 text(sl,'Sulco maior que 5,5755:\nprevisão Rosa',64,250,1140,125,43,true);
 text(sl,'Limites',64,435,1140,45,31,true);
 text(sl,'Teste pequeno: 42 exemplos de uma única divisão.\nSem avaliação em nova safra, local ou instrumento.\nFolhas pequenas ainda podem generalizar mal.',64,505,1140,140,29);
}
// 14. Implantação
{
 const sl=slide('Implantação local e monitoramento', 'As páginas 52, 97, 98 e 130 da aula ampliaram o roteiro com implantação e monitoramento. Executado: pipeline Joblib, inferência CSV em lote e referência do treino. A demonstração usa três linhas de treino e apenas verifica a interface. Planejado: qualidade por lote, revisão mensal de distribuição e métricas com novos rótulos. Não houve publicação de API nem observação de drift. Gatilhos no plano são propostas a calibrar.','slide-machine-learning.pdf, p. 52, 97, 98 e 130. relatorios/plano_monitoramento.md.');
 text(sl,'Executado',64,180,1130,45,33,true);
 text(sl,'Modelo serializado e previsão em lote com CSV.\nValidação de entradas e alerta fora do intervalo do treino.',64,250,1130,110,30);
 text(sl,'Planejado para novos dados',64,430,1130,55,33,true);
 text(sl,'Acompanhar qualidade e distribuição das medidas.\nMedir desempenho quando houver rótulos independentes.\nRetreinar com nova avaliação reservada, se necessário.',64,510,1130,140,29);
}
// 15. Conclusão
{
 const sl=slide('A hipótese foi sustentada nesta avaliação', 'Resposta à pergunta: as sete medidas permitem prever variedades melhor que a regra simples nesta avaliação. 92,86% contra 33,33%, ganho 59,52 pontos percentuais. Evitar generalizar para qualquer origem ou afirmar melhor algoritmo universal. O relatório contém reprodutibilidade, erros, limites e comparação completa. As entregas estão preparadas antecipadamente para os marcos de 13/11, 20/11, 27/11 e 04/12, com envio no feriado de 20/11 a cargo do aluno.',sourceUCI+' Métodos: https://scikit-learn.org/stable/common_pitfalls.html.');
 text(sl,'92,86%',64,180,1100,125,90,true);
 text(sl,'de acurácia, contra 33,33% da referência',68,325,1120,65,34);
 text(sl,'As medidas carregam informação útil para prever a variedade.\nO próximo passo é validar em grãos de outras origens.',68,450,1120,115,31);
 caption(sl,'Dados: Seeds, UCI, DOI 10.24432/C5H30K. Código, métricas e fontes acompanham o relatório.');
}

const draft=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(draft);
console.log('PPTX candidato exportado. Iniciando validação.');
let finalPath=path.join(root,'apresentacao/apresentacao_final.pptx');
try {await fs.access(finalPath); finalPath=path.join(root,`apresentacao/apresentacao_final_${Date.now()}.pptx`);} catch {}
const finalResult=await finalizePresentation({workspaceDir:root,candidatePath:draft,finalPath,pythonExecutable:python,
 integrityValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skillDir,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--cover-role','cover',
  ...[...new Set(tableOwners)].flatMap(n=>['--require-native-table-slide',String(n)])],
 requiredNativeTableOwnerSlides:[...new Set(tableOwners)],requiredNativeChartOwnerSlides:[...new Set(chartOwners)],
 materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(build,`${path.basename(finalPath)}.validation.json`)});
console.log('PPTX final:',finalPath);
const finalPresentation=await PresentationFile.importPptx(await FileBlob.load(finalPath));
for(const [i,sl] of finalPresentation.slides.items.entries()) {
 const png=await finalPresentation.export({slide:sl,format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 console.log(`Render ${i+1}/${presentation.slides.items.length}`);
}
await fs.writeFile(path.join(build,'outline.json'),JSON.stringify(outline,null,2));
const roteiro='# Roteiro da apresentação final\n\nGabriel Felix. Sugestão: 10 a 12 minutos, ajustável ao tempo da disciplina. Execução em 06/11/2026, entrega prevista 04/12/2026.\n\n'+outline.map(item=>`## ${item.number}. ${item.title}\n\n${item.note}\n\nFonte: ${item.source}\n`).join('\n');
await fs.writeFile(path.join(root,'apresentacao/roteiro_apresentacao.md'),roteiro,'utf8');
