"use strict";

import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const sharp = require("sharp");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const beforePath = path.join(root, ".codex-review", "section02-arrow-clarity", "full-before.png");
const afterPath = path.join(root, "poster", "final-poster.png");
const geometryPath = path.join(root, "outputs", "final", "intellectual_merits_geometry.json");
const assetDir = path.join(root, "docs", "final", "assets", "section02_arrow_clarity");
const reportPath = path.join(root, "outputs", "final", "section02_arrow_clarity.json");

// The only permitted changes are inside the central Section 02 body column.
const section02Region = { left: 960, top: 850, width: 1460, height: 1290 };
const protectedRegions = {
  headerAndMessage: { left: 0, top: 0, width: 3371, height: 735 },
  section01: { left: 100, top: 735, width: 830, height: 1400 },
  section03: { left: 2440, top: 735, width: 830, height: 1400 },
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
await sharp(beforePath).extract(section02Region).toFile(path.join(assetDir, "section02-before.png"));
await sharp(afterPath).extract(section02Region).toFile(path.join(assetDir, "section02-after.png"));

const before = await sharp(beforePath).removeAlpha().raw().toBuffer({ resolveWithObject: true });
const after = await sharp(afterPath).removeAlpha().raw().toBuffer({ resolveWithObject: true });
if (before.info.width !== after.info.width || before.info.height !== after.info.height || before.info.channels !== after.info.channels) {
  throw new Error(`Poster dimensions differ: before=${JSON.stringify(before.info)} after=${JSON.stringify(after.info)}`);
}

const { width, height, channels } = before.info;
const diff = Buffer.alloc(before.data.length);
const threshold = 8;
let changedInsidePixels = 0;
let changedOutsidePixels = 0;
let comparedInsidePixels = 0;
let comparedOutsidePixels = 0;
let maximumOutsideChannelDelta = 0;

for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    const inside = insideRegion(x, y, section02Region);
    const offset = (y * width + x) * channels;
    let pixelMaximum = 0;
    for (let channel = 0; channel < channels; channel += 1) {
      const delta = Math.abs(before.data[offset + channel] - after.data[offset + channel]);
      pixelMaximum = Math.max(pixelMaximum, delta);
      diff[offset + channel] = Math.min(255, delta * 5);
      if (!inside) maximumOutsideChannelDelta = Math.max(maximumOutsideChannelDelta, delta);
    }
    if (inside) {
      comparedInsidePixels += 1;
      if (pixelMaximum > threshold) changedInsidePixels += 1;
    } else {
      comparedOutsidePixels += 1;
      if (pixelMaximum > threshold) changedOutsidePixels += 1;
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

const geometry = JSON.parse(await fs.readFile(geometryPath, "utf8"));
const spacingPassed = geometry.status === "PASS" && geometry.spacingMetrics.every((metric) => metric.actual >= metric.minimum);
const protectedPassed = Object.values(protectedEvidence).every((entry) => entry.identical);
const report = {
  schemaVersion: 1,
  before: path.relative(root, beforePath),
  after: path.relative(root, afterPath),
  dimensions: { width, height, channels },
  section02Region,
  threshold,
  changedInsidePixels,
  changedInsideRatio: changedInsidePixels / comparedInsidePixels,
  changedOutsidePixels,
  changedOutsideRatio: changedOutsidePixels / comparedOutsidePixels,
  maximumOutsideChannelDelta,
  protectedEvidence,
  spacingMetrics: geometry.spacingMetrics,
  geometryStatus: geometry.status,
  status: changedInsidePixels > 0 && changedOutsidePixels === 0 && maximumOutsideChannelDelta === 0 && protectedPassed && spacingPassed ? "PASS" : "REVIEW",
};

await fs.writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
