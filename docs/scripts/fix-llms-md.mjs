#!/usr/bin/env node

/**
 * fix-llms-md.mjs — Post-build fixups for docusaurus-plugin-llms output.
 *
 * 1. Duplicate headings in .md files
 *    The plugin wraps each .md file with its own "# Title\n\n> Description"
 *    preamble, but the source MDX already starts with the same "# Title",
 *    producing a doubled heading. This script strips the plugin preamble when
 *    the heading is duplicated.
 *
 *    Alternatives considered:
 *     - Move headings into front matter `title:` across all MDX files (too invasive).
 *     - Patch the plugin or fork it (maintenance burden).
 *     - Accept duplicates (functional but looks sloppy).
 *
 * 2. Double-slash in llms.txt / llms-full.txt URLs
 *    The plugin constructs URLs as `siteConfig.url + baseUrl + path`. When
 *    baseUrl is "/" (root), this produces "https://example.dev//docs/..."
 *    instead of a single slash. Browsers normalize this, but it's cosmetically
 *    wrong and could confuse strict URL parsers.
 *
 *    Alternatives considered:
 *     - Plugin pathTransformation option (doesn't affect base URL joining).
 *     - Upstream fix (correct but not in our control; see github.com/rachfop/docusaurus-plugin-llms/issues/27).
 *     - Accept double-slash (functional but ugly).
 *
 * 3. Truncated descriptions in llms.txt
 *    The plugin hardcodes a 150-character limit on link descriptions
 *    (cleanDescriptionForToc in generator.js), cutting them mid-sentence.
 *    This script re-derives full first-paragraph descriptions from the
 *    generated .md files.
 *
 *    Alternatives considered:
 *     - Patch the 150-char limit via postinstall (fragile across upgrades).
 *     - File upstream issue for configurable descriptionMaxLength (not in our control).
 *     - Drop descriptions entirely (Stripe does this; agents fetch .md anyway).
 *
 * Execution order matters: Fix 1 (dedup headings in .md files) runs first so
 * that Fix 3 (descriptions) reads clean .md content when deriving paragraphs.
 *
 * Run after `docusaurus build`: see "build" script in package.json.
 */

import { readFileSync, writeFileSync, globSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const buildDir = resolve(__dirname, "..", "build");
const buildDocsDir = resolve(buildDir, "docs");

// --- Fix 1: Duplicate headings in individual .md files ---

function fixDuplicateHeading(filePath) {
  const text = readFileSync(filePath, "utf-8");
  const lines = text.split("\n");

  // Expect: line 0 = "# Title", line 1 = "", line 2 = "> ...", line 3 = "", line 4 = "# Title"
  if (lines.length < 5) return;

  const firstHeading = lines[0];
  if (!firstHeading.startsWith("# ")) return;

  const blockquote = lines[2];
  if (!blockquote.startsWith("> ")) return;

  const secondHeading = lines[4];
  if (firstHeading !== secondHeading) return;

  const fixed = lines.slice(4).join("\n");
  writeFileSync(filePath, fixed);
}

// --- Fix 2: Double-slash in llms.txt / llms-full.txt URLs ---

function fixDoubleSlashUrls(text) {
  return text
    .split("\n")
    .map((line) => line.replace(/(?<=https?:\/\/[^/]+)\/\//g, "/"))
    .join("\n");
}

// --- Fix 3: Restore full descriptions in llms.txt from .md files ---

const LINK_LINE_RE = /^- \[([^\]]+)\]\(([^)]+)\)(?::.*)?$/;

function extractFirstParagraph(mdPath) {
  let text;
  try {
    text = readFileSync(mdPath, "utf-8");
  } catch {
    return undefined;
  }
  const lines = text.split("\n");
  // Skip heading and blank line: "# Title\n\n<paragraph>"
  let start = 0;
  if (lines[start]?.startsWith("# ")) start++;
  while (start < lines.length && lines[start].trim() === "") start++;

  const para = [];
  for (let i = start; i < lines.length; i++) {
    const line = lines[i];
    if (line.trim() === "" && para.length > 0) break;
    // Stop at subheadings, fences, admonitions — first paragraph only.
    if (/^#{2,}\s|^```|^:::/.test(line)) break;
    para.push(line.trim());
  }
  return para.length > 0 ? para.join(" ") : undefined;
}

// 4. Framework prefix in llms.txt titles
//    The same recipe appears under each framework (dash, streamlit, reflex,
//    fastapi) with identical titles. Without disambiguation, llms.txt has
//    four "Connect an MCP server" entries that only differ by URL path.
//    This prefixes each title with the framework name (e.g., "Dash: Connect
//    an MCP server"). Only known frameworks are prefixed; new top-level
//    sections would need to be added here.
//
//    Alternatives considered:
//     - Parentheses suffix "(Dash)" — conflicts with Markdown link syntax.
//     - Group entries under ## Framework headers (cleaner but more complex).
//     - Do nothing — URL paths already contain the framework name.
const FRAMEWORK_LABELS = { dash: "Dash", fastapi: "FastAPI", reflex: "Reflex", streamlit: "Streamlit" };

function fixDescriptions(text) {
  return text
    .split("\n")
    .map((line) => {
      const m = line.match(LINK_LINE_RE);
      if (!m) return line;

      const [, title, url] = m;
      let urlPath;
      try {
        urlPath = new URL(url).pathname;
      } catch {
        return line;
      }

      const framework = urlPath.match(/^\/docs\/([^/]+)\//)?.[1];
      const prefix = FRAMEWORK_LABELS[framework] ? `${FRAMEWORK_LABELS[framework]}: ` : "";

      const mdPath = resolve(buildDir, urlPath.replace(/^\//, ""));
      const desc = extractFirstParagraph(mdPath);
      if (!desc) return line;
      return `- [${prefix}${title}](${url}): ${desc}`;
    })
    .join("\n");
}

// --- Run ---

// Fix 1 first: deduplicate .md headings so Fix 3 reads clean content.
const mdFiles = globSync(`${buildDocsDir}/**/*.md`);
for (const f of mdFiles) {
  fixDuplicateHeading(f);
}
console.log(`[fix-llms-md] Deduplicated headings in ${mdFiles.length} .md files.`);

// Fixes 2 + 3: patch llms.txt and llms-full.txt (URLs and descriptions).
for (const name of ["llms.txt", "llms-full.txt"]) {
  const filePath = resolve(buildDir, name);
  try {
    let text = readFileSync(filePath, "utf-8");
    text = fixDoubleSlashUrls(text);
    text = fixDescriptions(text);
    writeFileSync(filePath, text);
  } catch {
    // File may not exist if the plugin option was disabled; skip silently.
  }
}
console.log("[fix-llms-md] Fixed URLs and descriptions in llms*.txt.");
