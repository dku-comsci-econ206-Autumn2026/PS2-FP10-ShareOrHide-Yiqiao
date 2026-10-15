"use strict";

import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(scriptDir, "..");
const staticDir = path.join(root, "hf_static");
const output = path.join(root, "docs", "assets", "demo", "behavioral-decision-lab-fallback.png");
const contentTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
};

const server = http.createServer(async (request, response) => {
  try {
    const pathname = request.url === "/" ? "/index.html" : new URL(request.url, "http://localhost").pathname;
    const file = path.resolve(staticDir, `.${pathname}`);
    if (!file.startsWith(`${staticDir}${path.sep}`)) throw new Error("invalid path");
    const data = await fs.readFile(file);
    response.writeHead(200, { "Content-Type": contentTypes[path.extname(file)] ?? "application/octet-stream" });
    response.end(data);
  } catch {
    response.writeHead(404);
    response.end("Not found");
  }
});

await fs.mkdir(path.dirname(output), { recursive: true });
await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
const address = server.address();
const url = `http://127.0.0.1:${address.port}/`;

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: "domcontentloaded", timeout: 10000 });
  await page.waitForFunction(
    () => !document.querySelector("#load-status")?.textContent?.includes("Loading"),
    null,
    { timeout: 10000 },
  );
  await page.screenshot({ path: output, fullPage: false });
  console.log(JSON.stringify({ output, url, title: await page.title() }, null, 2));
} finally {
  await browser.close();
  await new Promise((resolve) => server.close(resolve));
}
