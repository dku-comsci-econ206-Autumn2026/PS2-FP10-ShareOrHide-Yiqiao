"use strict";

import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const sharp = require("sharp");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const beforePath = path.join(root, ".codex-review", "intellectual-merits-fix", "poster-before.png");
const afterPath = path.join(root, "poster", "final-poster.png");
const assetDir = path.join(root, "docs", "final", "assets", "intellectual_merits_fix");
const reportPath = path.join(root, "outputs", "final", "intellectual_merits_poster_diff.json");
const sectionCrop = { left: 1035, top: 735, width: 1325, height: 690 };
const intendedChangeRegion = { left: 1055, top: 870, width: 1290, height: 410 };

await fs.mkdir(assetDir, { recursive: true });
await sharp(afterPath).extract(sectionCrop).toFile(path.join(assetDir, "section02_after.png"));

const before = await sharp(beforePath).removeAlpha().raw().toBuffer({ resolveWithObject: true });
const after = await sharp(afterPath).removeAlpha().raw().toBuffer({ resolveWithObject: true });
if (before.info.width !== after.info.width || before.info.height !== after.info.height || before.info.channels !== after.info.channels) {
  throw new Error(`Poster dimensions differ: before=${JSON.stringify(before.info)} after=${JSON.stringify(after.info)}`);
}

const { width, height, channels } = before.info;
const diff = Buffer.alloc(before.data.length);
let changedInside = 0;
let changedOutside = 0;
let comparedInside = 0;
let comparedOutside = 0;
let maximumOutsideChannelDelta = 0;
let outsideAbsoluteDelta = 0;
const threshold = 8;

for (let y = 0; y < height; y += 1) {
  for (let x = 0; x < width; x += 1) {
    const inside = x >= intendedChangeRegion.left && x < intendedChangeRegion.left + intendedChangeRegion.width && y >= intendedChangeRegion.top && y < intendedChangeRegion.top + intendedChangeRegion.height;
    let pixelMax = 0;
    const offset = (y * width + x) * channels;
    for (let channel = 0; channel < channels; channel += 1) {
      const delta = Math.abs(before.data[offset + channel] - after.data[offset + channel]);
      pixelMax = Math.max(pixelMax, delta);
      diff[offset + channel] = Math.min(255, delta * 5);
      if (!inside) {
        maximumOutsideChannelDelta = Math.max(maximumOutsideChannelDelta, delta);
        outsideAbsoluteDelta += delta;
      }
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

await sharp(diff, { raw: { width, height, channels } }).png().toFile(path.join(assetDir, "poster_diff.png"));
const report = {
  schemaVersion: 1,
  before: path.relative(root, beforePath),
  after: path.relative(root, afterPath),
  dimensions: { width, height, channels },
  sectionCrop,
  intendedChangeRegion,
  threshold,
  changedInsidePixels: changedInside,
  changedInsideRatio: changedInside / comparedInside,
  changedOutsidePixels: changedOutside,
  changedOutsideRatio: changedOutside / comparedOutside,
  maximumOutsideChannelDelta,
  meanOutsideAbsoluteChannelDelta: outsideAbsoluteDelta / (comparedOutside * channels),
  interpretation: "The intended region covers only the Intellectual Merits image. Nonzero outside-region deltas may reflect LibreOffice anti-aliasing and metadata-driven rerendering; inspect the diff image before accepting.",
};
await fs.writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
