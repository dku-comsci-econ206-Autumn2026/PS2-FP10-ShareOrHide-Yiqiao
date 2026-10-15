import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import { pathToFileURL } from "node:url";
import {
  FileBlob,
  Presentation,
  PresentationFile,
} from "/Users/mickeyxiaoliuliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs";

const root = "/Users/mickeyxiaoliuliu/Desktop/DKU curriculums/cs206/PS2-ShareOrHide-Yiqiao";
const template = "/Users/mickeyxiaoliuliu/Desktop/DKU curriculums/cs206/final project requirements/COMSCI_ECON206_Final_Project_A0_Poster_Template.pptx";
const outDir = `${root}/.codex-review/poster-build`;

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

async function inspectTemplate() {
  await fs.mkdir(outDir, { recursive: true });
  const deck = await PresentationFile.importPptx(await FileBlob.load(template));
  const slide = deck.slides.items[0];
  await writeBlob(`${outDir}/official-template.png`, await deck.export({ slide, format: "png", scale: 0.5 }));
  const info = await deck.inspect({ kind: "slide,textbox,shape,image,layout", maxChars: 20000 });
  await fs.writeFile(`${outDir}/official-template.inspect.ndjson`, info.ndjson);
  console.log(JSON.stringify({ slides: deck.slides.length, size: deck.size, elements: slide.elements.length }, null, 2));
}

async function bytes(path) {
  const b = await fs.readFile(path);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.byteLength);
}

function put(deck, id, value, fontSize) {
  const el = deck.resolve(id);
  el.text = value;
  if (fontSize) el.text.style = { ...el.text.style, fontSize };
  return el;
}

async function buildPoster() {
  await fs.mkdir(outDir, { recursive: true });
  await fs.mkdir(`${root}/poster`, { recursive: true });
  const deck = await PresentationFile.importPptx(await FileBlob.load(template));
  const slide = deck.resolve("sl/y90nupkv");

  put(deck, "sh/7qp4be9c", "Share or Hide? Strategic Disclosure\nin Congested Low-Altitude Drone Traffic", 104);
  put(deck, "sh/65g3298r", "Yiqiao Liu  |  Team FP10", 52);
  put(deck, "sh/k3yl0zql", "FINAL PROJECT v2026.10.15", 26);
  put(deck, "sh/wn6dc7eh", "The Medium-congestion welfare gap falls from 0.946 to 0.050 in the benchmark CCAR example, but the rule also has no-effect and adverse parameter regions.", 48);

  put(deck, "sh/4r6dg7et", "When do private confidentiality costs and public congestion make voluntary M/P/F disclosure inefficient, and when does CCAR improve welfare?\nClosest work: Los et al. (2020); Liu & Chow (2022); Maheshwari et al. (2025).\nContribution: a reproducible stylized comparison with failure regions, not a theorem or aviation field result.", 36);
  put(deck, "sh/ipovexwn", "", 36);
  put(deck, "sh/sfqdkrep", "Game theory predicts complete type-contingent pure BNE.\nSocial choice compares operator utility with total welfare and an infeasible type-observing reference.\nMechanism design tests a congestion-contingent rule for enhanced, non-safety access.", 36);
  put(deck, "sh/1cvuxc7e", "One residual commercial priority slot. FCFS: first eligible request, zero payment. Second-price auction: highest bid wins, pays second bid.\nSeed-206 simulation: mean efficiency 0.622 vs 1.000. Emergency and public-safety missions remain outside payment-based access.", 34);

  put(deck, "sh/90ve1w7q", "", 30);
  put(deck, "sh/ozmd8r65", "", 30);
  put(deck, "sh/nydczmpk", "Figure 1. Three closest foundations feed an endogenous-disclosure Bayesian model, welfare benchmark, CCAR test, and explicit limitations.", 31);
  put(deck, "sh/p4bu5s76", "", 30);
  put(deck, "sh/432dwn6l", "", 30);
  put(deck, "sh/uxgjq907", "Figure 2. Expected normalized welfare. Low: 0.000 / 0.639. Medium: 2.193 / 3.089 / 3.139. High: 6.882 / 6.882 / 7.385 (BNE / CCAR / first best).\n760 deterministic grid cells: 401 no-effect; 334 robust improvements; 18 excessive-disclosure flags; 3 larger-gap; 66 multiple CCAR BNE. Diagnostics overlap.\nVerification: outputs/final/; exhaustive 81-profile search. Evidence: stylized computation.", 32);

  put(deck, "sh/i1gje90j", "", 30);
  put(deck, "sh/43y1gji9", "", 30);
  put(deck, "sh/y5wjip0z", "Economics defines incentives and welfare; computation exposes failure regions; those failures narrow the practical claim and motivate comprehension/fairness tests.\nYiqiao Liu: model boundary, code, experiments, interface, paper and poster; 65 baseline tests and fresh artifact verification.\nLimits: two operators/types, exogenous congestion, pure strategies, no calibration, report-quality or implementation-cost model.", 34);
  put(deck, "sh/z650ba1k", "OCT 12 / OCT 14 historical activity records: author confirmation pending\nOCT 21  Final submission at 23:00 Shanghai", 28);

  put(deck, "sh/14fyhgbe", "Prof. Luyao Zhang: course design and official templates. Prof. Kenneth S. (Ken) Rogerson: documented course-workshop context; no direct FP10 review claimed. Han Zhang: proposed three-party oversight extension. Xinrong Sun: novelty, domain, congestion-benefit and CCAR-externality challenges (author-supplied summaries; source records pending). Tencent Shanghai office; Shanghai Science and Technology Museum; COMSCI/ECON 206 classroom community. UN SDG assets; Python/NumPy/Matplotlib/nbclient/Gradio/Playwright/ACM template; OpenAI Codex assistance. Yiqiao Liu remains responsible.", 24);
  put(deck, "sh/nqxgjqtk", "Los et al. (2020), Transp. Res. E 141, 102011. doi:10.1016/j.tre.2020.102011\nLiu & Chow (2022), Transp. Res. B 163, 64–87. doi:10.1016/j.trb.2022.06.013\nMaheshwari et al. (2025), ACM JATS 2(4), Art. 19. doi:10.1145/3732290\nUN SDG targets 9.1 and 11.2: sdgs.un.org/goals", 23);
  put(deck, "sh/9sfylgbq", "Hugging Face: hf.co/spaces/dku-comsci-econ206-2026/ps2-share-or-hide-drone-disclosure\nGitHub: github.com/dku-comsci-econ206-Autumn2026/PS2-FP10-ShareOrHide-Yiqiao\nFinal tested commit: pending final verification commit", 23);
  put(deck, "sh/buh0nqtg", "", 20);
  put(deck, "sh/8zqx4vq9", "", 20);

  const intellectual = await bytes(`${root}/figures/final/intellectual_merits.png`);
  slide.images.add({ blob: intellectual, contentType: "image/png", alt: "Intellectual Merits evidence chain", fit: "contain", position: { left: 1415, top: 1180, width: 1664, height: 470 } });

  slide.charts.add("column", {
    position: { left: 1450, top: 1885, width: 1590, height: 590 },
    categories: ["Low", "Medium", "High"],
    series: [
      { name: "BNE", values: [0, 2.192883, 6.881808], fill: "#214E78" },
      { name: "CCAR", values: [0, 3.089085, 6.881808], fill: "#14877D" },
      { name: "First best", values: [0.639095, 3.139085, 7.385238], fill: "#E57A00" },
    ],
    hasLegend: true,
    legend: { position: "bottom" },
    dataLabels: { showValue: true, position: "outEnd" },
    xAxis: { title: "Public congestion" },
    yAxis: { title: "Expected normalized welfare", minimumScale: 0, maximumScale: 8 },
  });
  const welfare = await bytes(`${root}/figures/final/welfare_comparison.png`);
  slide.images.add({ blob: welfare, contentType: "image/png", alt: "Code-recomputed welfare comparison for Low, Medium, and High congestion", fit: "contain", position: { left: 1450, top: 1885, width: 1590, height: 590 } });

  const practical = await bytes(`${root}/figures/final/practical_impacts.png`);
  slide.images.add({ blob: practical, contentType: "image/png", alt: "Practical impacts with UN SDG targets 9.1 and 11.2", fit: "contain", position: { left: 3198, top: 1245, width: 1150, height: 395 } });
  const roadmap = await bytes(`${root}/figures/final/research_roadmap.png`);
  slide.images.add({ blob: roadmap, contentType: "image/png", alt: "Economics, computer science, behavioral and institutional research roadmap", fit: "contain", position: { left: 3198, top: 1735, width: 1150, height: 565 } });
  const hfQr = await bytes(`${root}/poster/qr/huggingface.png`);
  slide.images.add({ blob: hfQr, contentType: "image/png", alt: "QR code for the Hugging Face Space", fit: "contain", position: { left: 4108, top: 2966, width: 115, height: 115 } });
  const ghQr = await bytes(`${root}/poster/qr/github.png`);
  slide.images.add({ blob: ghQr, contentType: "image/png", alt: "QR code for the GitHub repository", fit: "contain", position: { left: 4235, top: 2966, width: 115, height: 115 } });

  const gameX = 150;
  const gameY = 1665;
  const labels = [
    ["PRIVATE TYPE", "Low or High confidentiality cost"],
    ["ACTION", "Minimum / Partial / Full"],
    ["BNE", "Best response to rival's type strategy"],
    ["CCAR", "Minimum access factor αM at Medium/High"],
  ];
  labels.forEach(([head, body], i) => {
    const top = gameY + i * 86;
    const box = slide.shapes.add({ geometry: "roundRect", position: { left: gameX, top, width: 1135, height: 70 }, fill: i === 3 ? "#E8F4F1" : "#EEF3FB", line: { style: "solid", fill: i === 3 ? "#14877D" : "#315EFB", width: 2 } });
    box.text = `${head}   ${body}`;
    box.text.style = { fontSize: 28, fontFamily: "Calibri", color: "#18324A", bold: false, verticalAlignment: "middle" };
  });

  slide.speakerNotes.text = "Sources: Los et al. (2020), DOI 10.1016/j.tre.2020.102011; Liu and Chow (2022), DOI 10.1016/j.trb.2022.06.013; Maheshwari et al. (2025), DOI 10.1145/3732290; official UN SDG Goal 9 and Goal 11 pages and communications assets; FP10 outputs/final/release_manifest.json. Evidence is a stylized computational benchmark, not real-world drone traffic evidence. Official course A0 template supplied by COMSCI/ECON 206.";

  const draft = `${outDir}/final-poster-draft.pptx`;
  const pptx = await PresentationFile.exportPptx(deck);
  await pptx.save(draft);
  await writeBlob(`${outDir}/final-poster.png`, await deck.export({ slide, format: "png", scale: 0.5 }));
  const layout = await slide.export({ format: "layout" });
  await fs.writeFile(`${outDir}/final-poster.layout.json`, await layout.text());
  console.log(JSON.stringify({ draft, slides: deck.slides.length, template: true }, null, 2));
}

async function finalizePoster() {
  const skillDir = "/Users/mickeyxiaoliuliu/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations";
  const runtimePython = "/Users/mickeyxiaoliuliu/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3";
  const candidatePath = `${outDir}/final-poster-draft.pptx`;
  const finalPath = `${root}/poster/final-poster.pptx`;
  const referenceSha256 = crypto.createHash("sha256").update(await fs.readFile(template)).digest("hex");
  const { finalizePresentation } = await import(pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href);
  const result = await finalizePresentation({
    explicitTotalSlideCount: 1,
    requiredNativeTableOwnerSlides: [],
    requiredNativeChartOwnerSlides: [],
    sourceTemplatePath: template,
    requiredTemplateReferenceSlides: [1],
    minimumTemplateCoverageRatio: 0.9,
    requireExactTemplateDimensions: true,
    requireTemplatePlaceholderGeometry: true,
    requirePhotographicBackground: false,
    workspaceDir: root,
    candidatePath,
    finalPath,
    pythonExecutable: runtimePython,
    integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
    layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
    layoutArgs: ["--expected-slide-size-emu", "42804000,30276000", "--validate-bullet-geometry", "--validate-heading-fit"],
    fontPolicy: { basis: "reference", families: ["Calibri"], referencePath: template, referenceSha256 },
    verifyArtifactToolImport: true,
    receiptPath: `${outDir}/final-poster.validation.json`,
  });
  console.log(JSON.stringify(result, null, 2));
}

if (process.argv.includes("--inspect-template")) {
  await inspectTemplate();
}
if (process.argv.includes("--build")) {
  try {
    await buildPoster();
  } catch (error) {
    console.error("BUILD_ERROR", error?.message ?? error);
    if (error?.issues) console.error(JSON.stringify(error.issues, null, 2));
    process.exitCode = 1;
  }
}
if (process.argv.includes("--finalize")) {
  try {
    await finalizePoster();
  } catch (error) {
    console.error("FINALIZE_ERROR", error?.message ?? error);
    process.exitCode = 1;
  }
}
