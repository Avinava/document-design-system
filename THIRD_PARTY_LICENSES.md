# Third-party licenses

This repository ships no third-party code. The packages below are **authoring-time dependencies** — they run on the machine generating a document and contribute nothing to the delivered artifact, which is plain HTML and SVG.

They are listed because the skills instruct you to install and use them.

## Authoring-time dependencies

Pinned exactly. The Node packages install with `npm ci` from `package.json` and `package-lock.json` (Node 22.22.2 or newer); the Python packages install with `uv pip install -r requirements-authoring.txt`. `scripts/validate_repository.py` fails if a version here, or anywhere else in the repository, disagrees with those two files.

| Package | Registry | Version | License | Used by |
|---|---|---|---|---|
| [`beautiful-mermaid`](https://github.com/lukilabs/beautiful-mermaid) | npm | 1.1.3 | MIT — Craft Docs (Lukilabs) | `scripts/render_diagram.mjs` |
| [`@observablehq/plot`](https://github.com/observablehq/plot) | npm | 0.6.17 | ISC — Observable, Inc. | `scripts/render_chart.mjs` |
| [`jsdom`](https://github.com/jsdom/jsdom) | npm | 30.1.2 | MIT | `scripts/render_chart.mjs` |
| [`playwright`](https://github.com/microsoft/playwright) | npm | 1.63.0 | Apache-2.0 — Microsoft | `scripts/export_pdf.mjs` |
| [`playwright`](https://github.com/microsoft/playwright-python) | PyPI | 1.63.0 | Apache-2.0 — Microsoft | `scripts/shoot_examples.py`, `scripts/extract_site_theme.py` |
| [`pillow`](https://github.com/python-pillow/Pillow) | PyPI | 12.3.0 | MIT-CMU (historical PIL licence, also listed as HPND) | `scripts/shoot_examples.py` |

## Optional escape hatches

Referenced by the skills as alternatives for cases the defaults do not cover. Not installed by default.

| Package | Registry | Version | License | Referenced by |
|---|---|---|---|---|
| [`mermaidx`](https://github.com/MohammadRaziei/mermaidx) | PyPI | unpinned | MIT | `diagram-design` — Mermaid types beautiful-mermaid does not cover |
| [`@hpcc-js/wasm-graphviz`](https://github.com/hpcc-systems/hpcc-js-wasm) | npm | 1.29.2 | Apache-2.0 | `diagram-design` — dense directed graphs |
| [`vl-convert-python`](https://github.com/vega/vl-convert) | PyPI | 1.9.x — avoid the 2.0 release candidates | BSD-3-Clause | `chart-design` — Vega-Lite spec to static SVG |

## Fonts

The themes reference Manrope, Inter, Geist, Geist Mono, IBM Plex Mono, Source Sans 3, and Source Code Pro. All are open-licensed (SIL OFL 1.1 or Apache-2.0) and are loaded from Google Fonts or embedded as subsets by `scripts/inline_fonts.py`. No font files are committed to this repository.

Every token stack ends in a system fallback, so a document remains usable when web fonts fail to load.

## Design influence

**[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** — MIT, Copyright (c) 2025 Cathryn Lavery.

No code from that project is used here. The `diagram-design` skill adapts its editorial standard: deletion as the highest-quality move, every node earning its place, one accent reserved for the one or two things that matter, a density target of 4/10, hairlines over shadows, and geometry on a 4px grid. Its position that Mermaid is an input format to redraw rather than an output format to embed also shaped this repo's approach. This release adapts three further principles from it: label geometry is verified from coordinates rather than reviewed by eye; an imported diagram is structure to redraw, never layout to keep; and a new diagram form is added only for a genuinely new layout. The license was re-checked for this release and is unchanged (MIT). See `skills/diagram-design/SKILL.md` for the in-skill credit.
