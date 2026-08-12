# Examples

Committed outputs, also used as CI fixtures.

| File | What it demonstrates |
|---|---|
| `inventory-report.html` | A self-contained analytical document: token block, limit ledger, metric cards, an inlined chart, an inlined diagram, and a methodology block. Opens with no build step and no JavaScript. |
| `footprint-by-function.svg` | Output of `scripts/render_chart.mjs` — a ranked bar chart with one focal bar. Colors are `var(--…)` references, not literals. |
| `ingestion-path.svg` | Output of `scripts/render_diagram.mjs` — a Mermaid sequence diagram prerendered to a themed SVG. |

## Regenerating

```bash
npm install beautiful-mermaid @observablehq/plot jsdom

node scripts/render_chart.mjs examples/specs/footprint.json \
  --out examples/footprint-by-function.svg

node scripts/render_diagram.mjs examples/specs/ingestion.mmd \
  --id ingest --title "Ingestion path" \
  --desc "Client posts events to the gateway, which enqueues them; the queue acknowledges." \
  --out examples/ingestion-path.svg

python3 scripts/build_document.py templates/document.html \
  --theme editorial-coral --out examples/inventory-report.html
# then inline the two SVGs into the chart frames
```

## The thing worth checking

Open `inventory-report.html`, then change one attribute:

```html
<html lang="en" data-theme="editorial-coral">   →   data-theme="executive-navy"
```

The page, the chart's focal bar, and the diagram's arrowheads all retheme together. Nothing re-renders and no JavaScript runs — the SVGs resolve their colors from the document's tokens at view time.

That is the whole architecture in one edit. It is why diagrams and charts are prerendered to SVG *strings* at authoring time while colors stay as live CSS custom properties.

Note that `data-theme` only switches between themes whose tokens are actually inlined in the document. `build_document.py` inlines one theme; to preview several, inline them all.
