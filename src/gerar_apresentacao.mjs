/** Gera e valida a apresentação final a partir dos resultados desta branch. */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const build = path.join(raiz, ".build_apresentacao");
const saida = path.join(raiz, "apresentacao");
let finalPath = path.join(saida, "apresentacao_final.pptx");
for (let versao = 2; ; versao += 1) {
  try {
    await fs.access(finalPath);
    finalPath = path.join(saida, `apresentacao_final_v${versao}.pptx`);
  } catch {
    break;
  }
}
const runtimeModules = process.env.CODEX_RUNTIME_NODE_MODULES ?? path.join(
  os.homedir(), ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules",
);
const runtimePython = process.env.CODEX_RUNTIME_PYTHON ?? path.join(
  os.homedir(), ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "python", "python.exe",
);
process.env.RUNTIME_NODE_MODULES = runtimeModules;
const skillDir = process.env.CODEX_PRESENTATION_SKILL ?? path.join(
  os.homedir(), ".codex", "plugins", "cache", "openai-primary-runtime", "presentations",
  "26.1123.11515", "skills", "presentations",
);
const { Presentation, PresentationFile } = await import(pathToFileURL(
  path.join(runtimeModules, "@oai", "artifact-tool", "dist", "artifact_tool.mjs"),
).href);
const { finalizePresentation } = await import(pathToFileURL(
  path.join(skillDir, "container_tools", "artifact_tool_utils.mjs"),
).href);

const C = {
  ink: "#1D302B",
  cream: "#F6F3EB",
  white: "#FFFEFA",
  gold: "#C48B2F",
  goldLight: "#F1E2C3",
  green: "#2F765A",
  greenLight: "#DDEBE1",
  red: "#B95043",
  redLight: "#F4DBD5",
  muted: "#566761",
  line: "#D9D8CC",
};
const p = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function rect(slide, x, y, w, h, fill, stroke = "none", sw = 0) {
  return slide.shapes.add({
    geometry: "rect", position: { left: x, top: y, width: w, height: h }, fill,
    line: { style: "solid", fill: stroke, width: sw },
  });
}
function ellipse(slide, x, y, w, h, fill, stroke = "none", sw = 0) {
  return slide.shapes.add({
    geometry: "ellipse", position: { left: x, top: y, width: w, height: h }, fill,
    line: { style: "solid", fill: stroke, width: sw },
  });
}
function txt(slide, text, x, y, w, h, size = 22, color = C.ink, bold = false, align = "left") {
  const shape = slide.shapes.add({
    geometry: "textbox", position: { left: x, top: y, width: w, height: h }, fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: `${size}pt`, typeface: "Arial", color, bold, alignment: align,
    verticalAlignment: "middle", autoFit: "none", wrap: "square", insets: 0,
  };
  return shape;
}
function base(n, title, source = "Fonte: UCI Seeds e resultados do projeto") {
  const slide = p.slides.add();
  slide.background.fill = C.cream;
  rect(slide, 0, 0, 1280, 9, C.gold);
  txt(slide, title, 72, 54, 1136, 86, 35, C.ink, true);
  rect(slide, 72, 650, 1136, 2, C.line);
  txt(slide, source, 72, 660, 990, 28, 10, C.muted);
  txt(slide, String(n).padStart(2, "0"), 1120, 657, 88, 30, 12, C.muted, true, "right");
  return slide;
}
function note(slide, content, sources) {
  slide.speakerNotes.text = `${content}\n\nFontes: ${sources}`;
}

// 1 — capa.
{
  const s = p.slides.add();
  s.background.fill = C.ink;
  rect(s, 0, 0, 1280, 11, C.gold);
  rect(s, 78, 155, 7, 348, C.gold);
  txt(s, "De sete medidas à\nvariedade do trigo", 115, 150, 850, 230, 49, C.white, true);
  txt(s, "Classificação do dataset Seeds", 117, 390, 790, 62, 26, C.goldLight);
  txt(s, "Gabriel Felix  •  David Ryan", 117, 553, 850, 42, 19, C.white);
  txt(s, "Apresentação final  |  04/12/2026", 117, 597, 850, 37, 15, C.goldLight);
  ellipse(s, 1035, 175, 104, 104, C.goldLight);
  ellipse(s, 1059, 307, 104, 104, C.gold);
  ellipse(s, 1035, 439, 104, 104, C.green);
  note(s, "Apresente o tema e a pergunta: conseguimos identificar a variedade a partir das medidas do grão?", "dataset-seed-versao-2.0.md; UCI https://archive.ics.uci.edu/dataset/236/seeds");
}

// 2 — dados e hipótese.
{
  const s = base(2, "210 grãos, três variedades equilibradas", "Fonte: UCI Seeds; auditoria do projeto em 13/11");
  txt(s, "210", 78, 192, 310, 120, 70, C.green, true);
  txt(s, "grãos de trigo", 83, 313, 320, 52, 24, C.ink);
  txt(s, "7 medidas geométricas por grão", 82, 378, 390, 47, 20, C.muted);
  const nomes = ["Kama", "Rosa", "Canadian"];
  const cores = [C.gold, C.green, C.ink];
  nomes.forEach((nome, i) => {
    const y = 205 + i * 111;
    txt(s, nome, 560, y, 205, 44, 23, C.ink, true);
    rect(s, 765, y + 4, 320, 36, cores[i]);
    txt(s, "70", 1100, y, 70, 44, 24, C.ink, true, "right");
  });
  rect(s, 80, 547, 1120, 2, C.line);
  txt(s, "Hipótese: superar uma regra que prevê sempre uma única classe (33,3%).", 82, 565, 1100, 58, 21, C.ink);
  note(s, "Explique que cada grão traz sete números e um rótulo de variedade. Como há 70 exemplos por classe, uma regra que sempre diz a mesma variedade acerta um terço dos casos.", "UCI https://archive.ics.uci.edu/dataset/236/seeds; dataset-seed-versao-2.0.md");
}

// 3 — preparação e partições.
{
  const s = base(3, "Separamos os dados antes de escolher o modelo", "Fonte: notebook de 13/11; resultados/particoes_20-11.csv");
  const blocks = [
    { x: 75, n: "210", lab: "grãos válidos", color: C.ink },
    { x: 465, n: "168", lab: "para treino e validação", color: C.green },
    { x: 855, n: "42", lab: "reservados para teste", color: C.gold },
  ];
  blocks.forEach(b => {
    rect(s, b.x, 192, 330, 190, C.white, C.line, 2);
    txt(s, b.n, b.x + 28, 206, 274, 96, 57, b.color, true, "center");
    txt(s, b.lab, b.x + 20, 304, 290, 52, 18, C.ink, false, "center");
  });
  txt(s, "Treino: 56 de cada classe", 460, 413, 350, 42, 19, C.muted, true);
  txt(s, "Teste: 14 de cada classe", 853, 413, 350, 42, 19, C.muted, true);
  txt(s, "Quatro medidas escolhidas no treino", 76, 512, 700, 43, 22, C.ink, true);
  txt(s, "Área  /  Perímetro  /  Largura  /  Comprimento do sulco", 76, 560, 1100, 42, 21, C.green);
  note(s, "A auditoria não removeu registros. A separação foi estratificada e reproduzível com semente 42. A análise e a escolha dos atributos usaram os 168 grãos de treino; os 42 ficaram guardados.", "machine_learning_av2.ipynb; entrega_20-11_seeds.md");
}

// 4 — seleção do modelo.
{
  const s = base(4, "A regressão logística foi a escolha inicial", "Fonte: resultados/validacao_20-11.csv (F1 macro em 5 dobras)");
  const rows = [
    ["Referência simples", 0.1644, C.muted],
    ["Árvore, 7 medidas", 0.8984, C.gold],
    ["Regressão, 4 medidas", 0.9276, C.green],
    ["Regressão, 7 medidas", 0.9286, C.ink],
  ];
  rows.forEach(([label, value, color], i) => {
    const y = 183 + i * 91;
    txt(s, label, 78, y, 350, 50, 20, C.ink, i === 2);
    rect(s, 442, y + 8, 610, 35, C.line);
    rect(s, 442, y + 8, Math.round(610 * value), 35, color);
    txt(s, Number(value).toFixed(4).replace(".", ","), 1070, y, 122, 50, 22, C.ink, true, "right");
  });
  txt(s, "Quatro medidas tiveram resultado quase igual a sete.", 78, 560, 1100, 40, 22, C.green, true);
  note(s, "Explique que a comparação foi feita por validação cruzada somente no treino. A regressão com sete medidas teve F1 0,9286 e a de quatro 0,9276. Pela regra de um erro padrão, escolhemos a versão de quatro medidas, mais simples.", "entrega_20-11_seeds.md; resultados/validacao_20-11.csv");
}

// 5 — refino.
{
  const s = base(5, "Refinamos a regularização usando só o treino", "Fonte: resultados/refino_27-11.csv");
  txt(s, "C = 10", 80, 213, 500, 115, 65, C.green, true);
  txt(s, "melhor F1 macro médio\nna validação: 0,9462", 80, 348, 430, 100, 25, C.ink);
  txt(s, "C", 636, 180, 155, 45, 18, C.muted, true);
  txt(s, "F1 macro", 930, 180, 225, 45, 18, C.muted, true, "right");
  const vals = [["0,01", "0,8822"], ["0,1", "0,9097"], ["1", "0,9276"], ["10", "0,9462"], ["100", "0,9402"]];
  vals.forEach(([c, f1], i) => {
    const y = 227 + i * 67;
    if (i === 3) rect(s, 610, y - 7, 550, 56, C.greenLight);
    txt(s, c, 637, y, 160, 38, 23, i === 3 ? C.green : C.ink, i === 3);
    txt(s, f1, 922, y, 225, 38, 23, i === 3 ? C.green : C.ink, i === 3, "right");
  });
  txt(s, "Configuração fixada antes de abrir o teste.", 80, 551, 490, 48, 18, C.muted);
  note(s, "C controla a força da regularização. Comparamos cinco valores em cinco dobras do treino. C igual a 10 teve a maior média de F1. Fixamos esse valor e salvamos o modelo antes de olhar o teste reservado.", "entrega_27-11_seeds.md; resultados/configuracao_27-11.json; resultados/refino_27-11.csv");
}

// 6 — resultado final.
{
  const s = p.slides.add();
  s.background.fill = C.ink;
  rect(s, 0, 0, 1280, 9, C.gold);
  txt(s, "No teste reservado", 75, 62, 1000, 65, 35, C.white, true);
  txt(s, "90,48%", 75, 183, 820, 165, 84, C.goldLight, true);
  txt(s, "38 acertos em 42 grãos", 80, 361, 770, 60, 30, C.white);
  rect(s, 80, 466, 1110, 2, C.green);
  txt(s, "Regra simples", 80, 495, 280, 44, 20, C.white);
  txt(s, "33,33%", 345, 485, 230, 58, 30, C.goldLight, true);
  txt(s, "F1 macro", 715, 495, 220, 44, 20, C.white);
  txt(s, "0,9007", 915, 485, 260, 58, 30, C.goldLight, true);
  txt(s, "Fonte: resultados/resumo_teste_27-11.json", 80, 664, 980, 28, 11, C.goldLight);
  txt(s, "06", 1120, 662, 70, 28, 12, C.goldLight, true, "right");
  note(s, "Depois de fixar o modelo, abrimos os 42 grãos de teste. Ele acertou 38, ou 90,48%. O F1 macro foi 0,9007. A regra de sempre prever uma classe acertaria 14 dos 42, ou 33,33%, porque o teste está equilibrado.", "resultados/resumo_teste_27-11.json; entrega_27-11_seeds.md");
}

// 7 — matriz de confusão.
{
  const s = base(7, "Os quatro erros foram grãos Kama", "Fonte: resultados/matriz_confusao_27-11.csv; erros_27-11.csv");
  const labs = ["Kama", "Rosa", "Canadian"];
  const m = [[10, 1, 3], [0, 14, 0], [0, 0, 14]];
  txt(s, "Previsto", 548, 165, 480, 35, 17, C.muted, true, "center");
  labs.forEach((lab, i) => txt(s, lab, 431 + i * 170, 208, 155, 42, 18, C.ink, true, "center"));
  txt(s, "Real", 76, 391, 105, 40, 18, C.muted, true);
  labs.forEach((lab, r) => {
    const y = 262 + r * 100;
    txt(s, lab, 165, y + 22, 230, 45, 21, C.ink, true);
    m[r].forEach((v, c) => {
      const x = 431 + c * 170;
      rect(s, x, y, 155, 86, r === c ? C.greenLight : v ? C.redLight : C.white, C.line, 1);
      txt(s, String(v), x, y + 8, 155, 70, 32, v && r !== c ? C.red : C.ink, true, "center");
    });
  });
  txt(s, "3 Kama → Canadian", 1000, 303, 230, 54, 20, C.red, true);
  txt(s, "1 Kama → Rosa", 1000, 380, 230, 54, 20, C.red, true);
  txt(s, "Kama: recall 71,43%", 78, 588, 600, 43, 21, C.ink, true);
  note(s, "Leia a matriz por linhas reais e colunas previstas. Dos 14 Kama, dez foram reconhecidos, três viraram Canadian e um virou Rosa. Todos os Rosa e Canadian reais foram reconhecidos. Os Kama errados tinham medidas de tamanho próximas das classes previstas, mas isso é uma descrição, não uma causa comprovada.", "resultados/matriz_confusao_27-11.csv; resultados/erros_27-11.csv; entrega_27-11_seeds.md");
}

// 8 — conclusão.
{
  const s = p.slides.add();
  s.background.fill = C.cream;
  rect(s, 0, 0, 1280, 9, C.gold);
  txt(s, "A hipótese se sustentou nesta divisão", 75, 64, 1120, 86, 35, C.ink, true);
  txt(s, "90,48%", 79, 214, 550, 118, 63, C.green, true);
  txt(s, "contra 33,33% da regra simples", 80, 340, 585, 58, 23, C.ink);
  rect(s, 737, 191, 4, 336, C.gold);
  txt(s, "O que ainda não sabemos", 780, 190, 426, 55, 25, C.ink, true);
  txt(s, "• Teste com apenas 42 grãos\n• Uma única origem dos dados\n• Kama foi a classe mais difícil", 780, 270, 425, 225, 21, C.ink);
  txt(s, "Próximo passo: avaliar grãos de outras origens.", 80, 565, 1120, 55, 23, C.green, true);
  rect(s, 75, 649, 1130, 2, C.line);
  txt(s, "Fonte: UCI Seeds e resultados do projeto", 76, 660, 1000, 28, 10, C.muted);
  txt(s, "08", 1120, 657, 84, 30, 12, C.muted, true, "right");
  note(s, "Conclua que a hipótese foi sustentada nesta divisão: o modelo superou a regra simples. Diga que o teste tem 42 exemplos de uma origem, então o número não garante o mesmo desempenho em outras safras ou locais. Uma nova avaliação deve usar grãos independentes.", "UCI https://archive.ics.uci.edu/dataset/236/seeds; entrega_27-11_seeds.md");
}

await fs.mkdir(build, { recursive: true });
await fs.mkdir(saida, { recursive: true });
for (const [i, slide] of p.slides.items.entries()) {
  const preview = await p.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(build, `slide-${String(i + 1).padStart(2, "0")}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const candidatePath = path.join(build, "candidate.pptx");
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const result = await finalizePresentation({
  workspaceDir: raiz,
  candidatePath,
  finalPath,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit"],
  explicitTotalSlideCount: 8,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  fontPolicy: { basis: "design", families: ["Arial"] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(build, "validacao.json"),
});
console.log(JSON.stringify({ finalPath, result }, null, 2));
