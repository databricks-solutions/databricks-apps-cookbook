#!/usr/bin/env node
// Runtime regression checks that the production build alone does not catch.
//
//   1. Lucide-react named-import audit. Scans src/ for every named import
//      from "lucide-react" and verifies the icon is actually exported by the
//      installed version. Catches major-bumps that remove icons (e.g.
//      lucide-react 1.x dropped all brand icons, breaking <Github />).
//
//   2. Headless render check. Boots `docusaurus serve` and visits a list of
//      pages. Fails if the Docusaurus error boundary fires. Best-effort —
//      pages that only crash with live third-party data (Sanity, etc.) won't
//      reproduce in CI, but blow-ups on initial render are caught.

import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, readdirSync, readFileSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DOCS_ROOT = resolve(__dirname, "..");
const SRC_DIR = join(DOCS_ROOT, "src");
const PORT = Number(process.env.PORT || 4321);
const PAGES_TO_RENDER = ["/", "/gallery/", "/gallery/pixels", "/resources"];
const BASE = `http://127.0.0.1:${PORT}`;
const SERVE_START_TIMEOUT_MS = 60_000;

function walk(dir) {
  const out = [];
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    const s = statSync(p);
    if (s.isDirectory()) out.push(...walk(p));
    else if (/\.(tsx?|jsx?|mjs)$/.test(entry)) out.push(p);
  }
  return out;
}

// Extract named imports from a single `import { ... } from "lucide-react"`
// statement. Handles multi-line imports.
function findLucideImports(source) {
  const re = /import\s*\{([^}]+)\}\s*from\s*['"]lucide-react['"]/g;
  const names = new Set();
  let m;
  while ((m = re.exec(source)) !== null) {
    for (const part of m[1].split(",")) {
      const name = part.trim().split(/\s+as\s+/)[0].trim();
      if (name) names.add(name);
    }
  }
  return names;
}

function auditLucideImports() {
  const files = walk(SRC_DIR);
  const usages = new Map(); // name -> [files]
  for (const f of files) {
    const src = readFileSync(f, "utf8");
    for (const name of findLucideImports(src)) {
      if (!usages.has(name)) usages.set(name, []);
      usages.get(name).push(f.replace(DOCS_ROOT + "/", ""));
    }
  }

  if (usages.size === 0) {
    console.log("Lucide audit: no lucide-react imports found, skipping.");
    return [];
  }

  const require = createRequire(import.meta.url);
  const lucide = require(require.resolve("lucide-react", { paths: [DOCS_ROOT] }));
  const missing = [];
  for (const [name, files] of usages) {
    if (lucide[name] === undefined) {
      missing.push({ name, files });
      console.error(
        `FAIL lucide: \`${name}\` is not exported by the installed lucide-react. Used in: ${files.join(", ")}`,
      );
    } else {
      console.log(`OK   lucide: ${name}`);
    }
  }
  return missing;
}

function findChrome() {
  if (process.env.CHROME_BIN) return process.env.CHROME_BIN;
  for (const bin of ["google-chrome", "chromium-browser", "chromium"]) {
    const r = spawnSync("which", [bin], { encoding: "utf8" });
    if (r.status === 0 && r.stdout.trim()) return r.stdout.trim();
  }
  return null;
}

async function waitForServer(url, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(url, { method: "HEAD" });
      if (res.ok || res.status === 404) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Server at ${url} did not become ready in ${timeoutMs}ms`);
}

function renderDom(chrome, url) {
  const tmp = mkdtempSync(join(tmpdir(), "smoke-chrome-"));
  try {
    const r = spawnSync(
      chrome,
      [
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        `--user-data-dir=${tmp}`,
        "--virtual-time-budget=15000",
        "--run-all-compositor-stages-before-draw",
        "--dump-dom",
        url,
      ],
      { encoding: "utf8", maxBuffer: 50 * 1024 * 1024 },
    );
    if (r.status !== 0) {
      throw new Error(
        `Chrome exited ${r.status} for ${url}: ${r.stderr.slice(0, 500)}`,
      );
    }
    return r.stdout;
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

async function renderCheck() {
  const chrome = findChrome();
  if (!chrome) {
    console.warn(
      "Skipping render check: no Chrome/Chromium binary on PATH (set CHROME_BIN to enable).",
    );
    return [];
  }
  console.log(`Render check: using Chrome ${chrome}`);

  console.log(`Starting docusaurus serve on port ${PORT}...`);
  const docusaurusBin = join(DOCS_ROOT, "node_modules", ".bin", "docusaurus");
  const serve = spawn(
    docusaurusBin,
    ["serve", "--port", String(PORT), "--no-open"],
    {
      stdio: ["ignore", "pipe", "pipe"],
      cwd: DOCS_ROOT,
      detached: true, // own process group so we can kill the whole tree
    },
  );
  serve.stdout.on("data", (b) => process.stdout.write(`[serve] ${b}`));
  serve.stderr.on("data", (b) => process.stderr.write(`[serve] ${b}`));

  const cleanup = () => {
    if (serve.pid && !serve.killed) {
      try {
        process.kill(-serve.pid, "SIGTERM");
      } catch {}
    }
  };
  process.on("exit", cleanup);
  process.on("SIGINT", () => {
    cleanup();
    process.exit(130);
  });

  const failures = [];
  try {
    await waitForServer(`${BASE}/`, SERVE_START_TIMEOUT_MS);
    for (const path of PAGES_TO_RENDER) {
      const url = `${BASE}${path}`;
      const html = renderDom(chrome, url);
      const crashed = /This page crashed|Minified React error/.test(html);
      if (crashed) {
        failures.push(path);
        console.error(`FAIL render: ${path} tripped the error boundary`);
      } else {
        console.log(`OK   render: ${path}`);
      }
    }
  } finally {
    cleanup();
  }
  return failures;
}

async function main() {
  const missingIcons = auditLucideImports();
  const renderFailures = await renderCheck();

  if (missingIcons.length || renderFailures.length) {
    console.error("\nSmoke test failed.");
    if (missingIcons.length)
      console.error(
        `  Missing lucide icons: ${missingIcons.map((m) => m.name).join(", ")}`,
      );
    if (renderFailures.length)
      console.error(`  Crashing pages: ${renderFailures.join(", ")}`);
    process.exit(1);
  }
  console.log("\nAll smoke checks passed.");
}

main().catch((err) => {
  console.error(err.stack || err.message);
  process.exit(1);
});
