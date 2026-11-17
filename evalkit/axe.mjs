#!/usr/bin/env node
// Run axe on each page a /design eval checks, while the app is still up, for the production-axe-clean check.
// Playwright and axe-core load from Pixie's cache, as /pixie:design-setup installs them.
//
//   node axe.mjs OUT.json ORIGIN LABEL=PATH...
//
// Writes one entry per page: {label, url, error, violations: [{id, impact, nodes}]}. A preview page that shows
// the harness's error marker, or answers with an error status, gets an error instead of an axe run. On a preview,
// axe checks only the rendered state: page-level rules (one main landmark, an h1) belong to the screen it's used on.
import { readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { homedir } from "node:os";
import { join } from "node:path";

const CACHE = join(homedir(), ".cache", "pixie", "playwright");
process.env.PLAYWRIGHT_BROWSERS_PATH = join(CACHE, "browsers");
const require = createRequire(join(CACHE, "noop.js"));
const { chromium } = require("playwright");
const axe = readFileSync(require.resolve("axe-core/axe.min.js"), "utf8");

async function check(browser, label, url) {
  const entry = { label, url, error: null, violations: [] };
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  try {
    const response = await page.goto(url, { waitUntil: "load", timeout: 30000 });
    if (response && response.status() >= 400) throw new Error(`HTTP ${response.status()}`);
    await page.waitForLoadState("networkidle", { timeout: 5000 }).catch(() => {});
    const preview = url.includes("/__preview/");
    if (preview) {
      // A preview renders after a lazy import, so wait for it, or its error, to settle.
      await page.waitForSelector("[data-pixie-preview], [data-pixie-preview-error]", { timeout: 15000 });
      const problem = await page.$("[data-pixie-preview-error]");
      if (problem) throw new Error((await problem.textContent()).trim());
    }
    await page.evaluate(axe);
    const result = await page.evaluate(
      (scope) => window.axe.run(scope ? document.querySelector(scope) : document, { resultTypes: ["violations"] }),
      preview ? "[data-pixie-preview]" : null,
    );
    entry.violations = result.violations.map((v) => ({ id: v.id, impact: v.impact, nodes: v.nodes.length }));
  } catch (error) {
    entry.error = String(error.message || error).split("\n")[0];
  } finally {
    await page.close();
  }
  return entry;
}

const [out, origin, ...pages] = process.argv.slice(2);
const browser = await chromium.launch();
const report = [];
try {
  for (const arg of pages) {
    const at = arg.indexOf("=");
    report.push(await check(browser, arg.slice(0, at), new URL(arg.slice(at + 1), origin).href));
  }
} finally {
  await browser.close();
}
writeFileSync(out, JSON.stringify(report, null, 2) + "\n");
