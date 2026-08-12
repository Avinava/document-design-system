# Third-party licenses

This repository ships no third-party code. The packages below are **authoring-time dependencies** — they run on the machine generating a document and contribute nothing to the delivered artifact, which is plain HTML and SVG.

They are listed because the skills instruct you to install and use them.

## Authoring-time dependencies

| Package | License | Used by |
|---|---|---|
| [beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid) | MIT — Craft Docs (Lukilabs) | `scripts/render_diagram.mjs` |
| [@observablehq/plot](https://github.com/observablehq/plot) | ISC — Observable, Inc. | `scripts/render_chart.mjs` |
| [jsdom](https://github.com/jsdom/jsdom) | MIT | `scripts/render_chart.mjs` |
| [Playwright](https://github.com/microsoft/playwright) | Apache-2.0 — Microsoft | `scripts/export_pdf.mjs` |

## Optional escape hatches

Referenced by the skills as alternatives for cases the defaults do not cover. Not installed by default.

| Package | License | Referenced by |
|---|---|---|
| [mermaidx](https://github.com/MohammadRaziei/mermaidx) | MIT | `diagram-design` — Mermaid types beautiful-mermaid does not cover |
| [@hpcc-js/wasm-graphviz](https://github.com/hpcc-systems/hpcc-js-wasm) | Apache-2.0 | `diagram-design` — dense directed graphs |
| [vl-convert](https://github.com/vega/vl-convert) | Apache-2.0 | `chart-design` — Vega-Lite spec to static SVG |
| [D2](https://github.com/terrastruct/d2) | **MPL-2.0** — file-level copyleft, unlike the rest of this list | `diagram-design` — architecture diagram layout |
| [Rough.js](https://github.com/rough-stuff/rough) | MIT | `diagram-design` — sketch aesthetic variant |

## Fonts

The themes reference Manrope, Inter, Geist, Geist Mono, IBM Plex Mono, Source Sans 3, and Source Code Pro. All are open-licensed (SIL OFL 1.1 or Apache-2.0) and are loaded from Google Fonts or embedded as subsets by `scripts/inline_fonts.py`. No font files are committed to this repository.

Every token stack ends in a system fallback, so a document remains usable when web fonts fail to load.

## Design influence

**[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** — MIT, Copyright (c) 2025 Cathryn Lavery.

No code from that project is used here. The `diagram-design` skill adapts its editorial standard: deletion as the highest-quality move, every node earning its place, one accent reserved for the one or two things that matter, a density target of 4/10, hairlines over shadows, and geometry on a 4px grid. Its position that Mermaid is an input format to redraw rather than an output format to embed also shaped this repo's approach. See `skills/diagram-design/SKILL.md` for the in-skill credit.
