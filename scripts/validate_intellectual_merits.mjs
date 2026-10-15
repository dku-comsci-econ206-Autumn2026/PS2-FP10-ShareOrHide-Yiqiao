"use strict";

import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const svgPath = path.join(root, "figures", "final", "intellectual_merits.svg");
const outputPath = path.join(root, "outputs", "final", "intellectual_merits_geometry.json");
const svg = await fs.readFile(svgPath, "utf8");
const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});

function intersects(a, b, padding = 0) {
  return !(
    a.x + a.width + padding <= b.x ||
    b.x + b.width + padding <= a.x ||
    a.y + a.height + padding <= b.y ||
    b.y + b.height + padding <= a.y
  );
}

try {
  const page = await browser.newPage({ viewport: { width: 1800, height: 544 } });
  await page.setContent(`<style>html,body{margin:0}</style>${svg}`, { waitUntil: "networkidle" });
  const geometry = await page.evaluate(() => {
    const svgNode = document.querySelector("svg");
    const viewBox = svgNode.viewBox.baseVal;
    const cards = [...document.querySelectorAll("g[data-card]")].map((group) => {
      const rect = group.querySelector("rect").getBBox();
      const texts = [...group.querySelectorAll("text")].map((text) => {
        const bounds = text.getBBox();
        return {
          text: text.textContent.trim(),
          role: text.dataset.role || "body",
          fontSize: Number.parseFloat(getComputedStyle(text).fontSize),
          bounds: { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height },
        };
      });
      return {
        id: group.dataset.card,
        rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
        texts,
      };
    });
    const connectors = [...document.querySelectorAll("path.connector")].map((node, index) => {
      const bounds = node.getBBox();
      return { id: `connector-${index + 1}`, bounds: { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height } };
    });
    return {
      viewBox: { x: viewBox.x, y: viewBox.y, width: viewBox.width, height: viewBox.height },
      cards,
      connectors,
    };
  });

  const failures = [];
  for (const card of geometry.cards) {
    for (const text of card.texts) {
      const b = text.bounds;
      const r = card.rect;
      const inside = b.x >= r.x + 14 && b.y >= r.y + 3 && b.x + b.width <= r.x + r.width - 14 && b.y + b.height <= r.y + r.height - 3;
      if (!inside) failures.push(`Text overflow in ${card.id}: ${text.text}`);
    }
    for (let i = 0; i < card.texts.length; i += 1) {
      for (let j = i + 1; j < card.texts.length; j += 1) {
        if (intersects(card.texts[i].bounds, card.texts[j].bounds, 0)) {
          failures.push(`Text collision in ${card.id}: ${card.texts[i].text} / ${card.texts[j].text}`);
        }
      }
    }
  }
  for (let i = 0; i < geometry.cards.length; i += 1) {
    for (let j = i + 1; j < geometry.cards.length; j += 1) {
      if (intersects(geometry.cards[i].rect, geometry.cards[j].rect, 0)) {
        failures.push(`Card overlap: ${geometry.cards[i].id} and ${geometry.cards[j].id}`);
      }
    }
  }
  const allTexts = geometry.cards.flatMap((card) => card.texts.map((text) => ({ card: card.id, ...text })));
  for (const connector of geometry.connectors) {
    for (const text of allTexts) {
      if (intersects(connector.bounds, text.bounds, 2)) failures.push(`${connector.id} intersects text in ${text.card}: ${text.text}`);
    }
  }
  for (const card of geometry.cards) {
    const r = card.rect;
    const v = geometry.viewBox;
    if (r.x < v.x || r.y < v.y || r.x + r.width > v.x + v.width || r.y + r.height > v.y + v.height) {
      failures.push(`Card outside viewBox: ${card.id}`);
    }
  }

  const sourceToPosterScale = Math.min(1664 / geometry.viewBox.width, 490 / geometry.viewBox.height);
  const posterMillimetresPerUnit = 1189 / 4460;
  const fontMetrics = allTexts.map((text) => ({
    text: text.text,
    sourcePx: text.fontSize,
    posterPt: text.fontSize * sourceToPosterScale * posterMillimetresPerUnit * 72 / 25.4,
  }));
  const report = {
    schemaVersion: 1,
    source: path.relative(root, svgPath),
    viewBox: geometry.viewBox,
    posterEmbedding: { left: 1415, top: 1170, width: 1664, height: 490 },
    sourceToPosterScale,
    cardCount: geometry.cards.length,
    connectorCount: geometry.connectors.length,
    cards: geometry.cards,
    fontMetrics,
    failures,
    status: failures.length === 0 ? "PASS" : "FAIL",
  };
  await fs.writeFile(outputPath, `${JSON.stringify(report, null, 2)}\n`);
  console.log(JSON.stringify({ status: report.status, cards: report.cardCount, connectors: report.connectorCount, failures }, null, 2));
  if (failures.length) process.exitCode = 1;
} finally {
  await browser.close();
}
