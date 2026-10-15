"use strict";

import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const sharp = require("sharp");
const { chromium } = require("playwright");

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const figureDir = path.join(root, "figures", "final");
const stems = ["intellectual_merits", "practical_impacts", "research_roadmap"];

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
try {
  for (const stem of stems) {
    const svgPath = path.join(figureDir, `${stem}.svg`);
    const pngPath = path.join(figureDir, `${stem}.png`);
    const pdfPath = path.join(figureDir, `${stem}.pdf`);
    let svg = await fs.readFile(svgPath, "utf8");
    for (const asset of ["E_WEB_09.png", "E_WEB_11.png"]) {
      const assetPath = path.join(figureDir, "sdg_official", asset);
      const dataUri = `data:image/png;base64,${(await fs.readFile(assetPath)).toString("base64")}`;
      svg = svg.replaceAll(`sdg_official/${asset}`, dataUri);
    }
    const svgBytes = Buffer.from(svg, "utf8");
    await sharp(svgBytes, { density: 180 }).resize(2400, 1350).png().toFile(pngPath);

    const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
    await page.setContent(`<style>html,body{margin:0;width:1600px;height:900px}</style>${svg}`, { waitUntil: "networkidle" });
    await page.pdf({
      path: pdfPath,
      width: "1600px",
      height: "900px",
      printBackground: true,
      margin: { top: "0", right: "0", bottom: "0", left: "0" },
      preferCSSPageSize: false,
    });
    await page.close();
  }
} finally {
  await browser.close();
}
