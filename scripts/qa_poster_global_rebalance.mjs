"use strict";

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const sharp = require("sharp");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const beforePath = path.join(root, ".codex-review", "poster-global-rebalance", "full-before.png");
const afterPath = path.join(root, "poster", "final-poster.png");
const assetDir = path.join(root, "docs", "final", "assets", "poster_layout_rebalance");
const reportPath = path.join(root, "outputs", "final", "poster_layout_rebalance.json");

const section02Crop = { left: 960, top: 720, width: 1460, height: 1430 };
const intendedRebalanceRegion = { left: 100, top: 735, width: 3170, height: 1400 };
const protectedRegions = {
  headerAndMessage: { left: 0, top: 0, width: 3371, height: 735 },
  footer: { left: 0, top: 2165, width: 3371, height: 219 },
};

function insideRegion(x, y, region) {
  return x >= region.left && x < region.left + region.width && y >= region.top && y < region.top + region.height;
}

function hash(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

await fs.mkdir(assetDir, { recursive: true });
await fs.copyFile(afterPath, path.join(assetDir, "full-after.png"));
await sharp(beforePath).extract(section02Crop).toFile(path.join(assetDir, "section02-before.png"));
await sharp(afterPath).extract(section02Crop).toFile(path.join(assetDir, "section02-after.png"));

const before = await sharp(beforePath).removeAlpha().raw().toBuffer({ resolveWithObject: true });
const after = await sharp(afterPath).removeAlpha().raw().toBuffer({ resolveWithObject: true });
if (before.info.width !== after.info.width || before.info.height !== after.info.height || before.info.channels !== after.info.channels) {
  throw new Error(`Poster dimensions differ: before=${JSON.stringify(before.info)} after=${JSON.stringify(after.info)}`);
}

const { width, height, channels } = before.info;
const diff = Buffer.alloc(before.data.length);
const threshold = 8;
let changedInside = 0;
let changedOutside = 0;
let comparedInside = 0;
let comparedOutside = 0;
let maximumOutsideChannelDelta = 0;

for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    const inside = insideRegion(x, y, intendedRebalanceRegion);
    const offset = (y * width + x) * channels;
    let pixelMax = 0;
    for (let channel = 0; channel < channels; channel += 1) {
      const delta = Math.abs(before.data[offset + channel] - after.data[offset + channel]);
      pixelMax = Math.max(pixelMax, delta);
      diff[offset + channel] = Math.min(255, delta * 5);
      if (!inside) maximumOutsideChannelDelta = Math.max(maximumOutsideChannelDelta, delta);
    }
    if (inside) {
      comparedInside += 1;
      if (pixelMax > threshold) changedInside += 1;
    } else {
      comparedOutside += 1;
      if (pixelMax > threshold) changedOutside += 1;
    }
  }
}

await sharp(diff, { raw: { width, height, channels } }).png().toFile(path.join(assetDir, "poster-diff.png"));

const protectedEvidence = {};
for (const [name, region] of Object.entries(protectedRegions)) {
  const beforeRegion = await sharp(beforePath).extract(region).removeAlpha().raw().toBuffer();
  const afterRegion = await sharp(afterPath).extract(region).removeAlpha().raw().toBuffer();
  protectedEvidence[name] = {
    beforeSha256: hash(beforeRegion),
    afterSha256: hash(afterRegion),
    identical: beforeRegion.equals(afterRegion),
  };
}

const report = {
  schemaVersion: 1,
  before: path.relative(root, beforePath),
  after: path.relative(root, afterPath),
  dimensions: { width, height, channels },
  section02Crop,
  intendedRebalanceRegion,
  threshold,
  changedInsidePixels: changedInside,
  changedInsideRatio: changedInside / comparedInside,
  changedOutsidePixels: changedOutside,
  changedOutsideRatio: changedOutside / comparedOutside,
  maximumOutsideChannelDelta,
  protectedEvidence,
  layoutMetrics: {
    beforeColumnWidths: [1160, 1693.86, 1160],
    afterColumnWidths: [1080, 1900, 1074],
    beforeColumnShares: [0.289, 0.422, 0.289],
    afterColumnShares: [0.266, 0.469, 0.265],
    section02FigureBefore: { width: 1664, height: 490 },
    section02FigureAfter: { width: 1870, height: 675 },
    section02FigureAreaIncreaseRatio: (1870 * 675) / (1664 * 490) - 1,
  },
  status: changedOutside === 0 && maximumOutsideChannelDelta === 0 && Object.values(protectedEvidence).every((entry) => entry.identical) ? "PASS" : "REVIEW",
};

await fs.writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
