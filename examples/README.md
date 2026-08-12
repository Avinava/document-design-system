# Examples

Committed outputs. They serve three jobs at once: CI fixtures, the screenshots in the root README, and a working reference for what each skill produces.

All of them rebuild from source — nothing here is hand-maintained.

```bash
npm install beautiful-mermaid @observablehq/plot jsdom
python3 scripts/build_examples.py
```

## Documents

| File | Skill | Theme |
|---|---|---|
| `inventory-report.html` | analytical-document-design | editorial-coral |
| `platform-rfc.html` | longform-document-design | field-notes |
| `capacity-deck.html` | presentation-design | executive-navy |
| `gallery-light.html` / `gallery-dark.html` | diagram-design + chart-design | editorial-coral / console-violet |
| `themes-light.html` / `themes-dark.html` | the token contract itself | all four panels |

The `-light` / `-dark` pairs exist so the README can swap them with the reader's GitHub theme via `<picture>`. Both halves of each pair inline the **same** SVG figures — only the root `data-theme` differs, so the pair is also a direct demonstration that nothing needs re-rendering.

## Figures

| File | Form | Produced by |
|---|---|---|
| `platform-architecture.svg` | Architecture diagram | Hand-authored from `templates/diagram.svg` |
| `ingestion-path.svg` | Sequence diagram | `render_diagram.mjs` (Mermaid → SVG) |
| `footprint-by-function.svg` | Ranked bars | `render_chart.mjs` |
| `cohorts-by-year.svg` | Columns | `render_chart.mjs` |
| `latency-p99.svg` | Line | `render_chart.mjs` |

Sources live in `specs/` — a `.mmd` for the diagram, a JSON spec per chart.

## The thing worth checking

Open any document and change one attribute:

```html
<html lang="en" data-theme="editorial-coral">   →   data-theme="executive-navy"
```

The page, the chart's focal bar, and the diagram's arrowheads all retheme together. Nothing re-renders and no JavaScript runs — the SVGs resolve their colors from the document's tokens at view time.

That is the whole architecture in one edit, and it is why figures are prerendered to SVG *strings* at authoring time while colors stay as live CSS custom properties.

One caveat: `data-theme` only switches between themes whose tokens are actually inlined. `build_document.py` inlines one theme, so to preview several, inline them all.

## Adding a theme

Use the `brand-theme-design` skill — it extracts from a brand guide, site, or screenshot, maps to the semantic roles, and runs `scripts/audit_theme.py` over the result. Doing it by hand means copying `core/themes/brand-template.css` and filling in every TODO.

## Print

```bash
node scripts/export_pdf.mjs examples/inventory-report.html --out report.pdf
node scripts/export_pdf.mjs examples/capacity-deck.html --out deck.pdf --preset deck
```

The report is 3 pages of A4; the deck is 7 slides on 7 pages. Open the PDF and look at it — page count alone proves nothing, since a drop in pages can mean clipped overflow rather than better layout.
