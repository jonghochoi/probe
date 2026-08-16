// Batch KaTeX renderer: one process per site build, not one per formula.
//
// stdin : {"items": [{"h": "<hash>", "tex": "...", "display": false}, ...]}
// stdout: {"html": {"<hash>": "<span class=\"katex\">…"}, "warnings": [...]}
//
// `throwOnError: false` renders a broken macro red-and-visible instead of
// aborting the build — docs/style.md §5-4 wants render failures to stay
// visible. Every failure is still reported on `warnings` so `--strict` can
// fail the build on a *new* one.

import { readFileSync } from "node:fs";
import katex from "katex";

const input = JSON.parse(readFileSync(0, "utf8"));
const html = {};
const warnings = [];

for (const { h, tex, display } of input.items) {
  let out;
  try {
    out = katex.renderToString(tex, {
      displayMode: !!display,
      throwOnError: false,
      strict: (code, msg) => {
        warnings.push({ h, tex, code, msg });
        return "ignore";
      },
      output: "html",
      trust: false,
    });
  } catch (err) {
    warnings.push({ h, tex, code: "fatal", msg: String(err && err.message) });
    // Keep the raw TeX visible rather than emitting nothing.
    out = `<code class="math-error">${tex.replace(/[&<>]/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" })[c]
    )}</code>`;
  }
  html[h] = out;
}

process.stdout.write(JSON.stringify({ html, warnings }));
