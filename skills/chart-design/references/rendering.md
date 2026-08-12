# Rendering charts from data

Charts render to an SVG string at authoring time. Nothing renders in the reader's browser.

That is what keeps a chart sharp in print, correct when the document is emailed as a single file, visible when JavaScript is unavailable, and free of the several hundred kilobytes a client-side charting library costs.

## Hand-authored or generated

**Hand-author** when there are fewer than about eight marks, or when the layout is doing something a layout engine will not do — an annotated limit ledger, a chart with callouts, a comparison built around one specific point. Hand-authoring a five-bar chart takes less time than writing the spec for it.

**Generate** when the data is large, changes on a schedule, or the chart is one of many that must stay consistent.

## The renderer

```bash
npm install @observablehq/plot jsdom   # authoring-time only

node scripts/render_chart.mjs spec.json --out chart.svg
```

The spec:

```json
{
  "form": "bars",
  "id": "fn-footprint",
  "title": "Ingestion holds 41% of the footprint",
  "desc": "Five functions ranked by current size. Ingestion holds 41 percent of the 1.8 million unit total, more than the next three combined.",
  "data": [
    {"k": "Ingestion", "v": 41},
    {"k": "Transform", "v": 22},
    {"k": "Serving",   "v": 18},
    {"k": "Archive",   "v": 12},
    {"k": "Other",     "v": 7}
  ],
  "x": "v",
  "y": "k",
  "focal": "Ingestion",
  "xLabel": "Share of included total (%)",
  "size": "doc-inline"
}
```

| Field | Notes |
|---|---|
| `form` | `bars`, `columns`, `line`, `scatter` |
| `id` | Prefixes every generated ID so charts can share a document |
| `title` | **States the finding**, not the variables |
| `desc` | What a screen-reader user gets instead of the chart |
| `focal` | The category that carries the accent. Omit for no focal mark |
| `series` | Grouping field for `line` and `scatter` |
| `size` | `doc-inline` (720), `full-width` (1100), `print-portrait` (640), `print-landscape` (980) |

`title` and `desc` are required. Writing the description is the fastest way to find out whether the chart has a point — if the sentence is "here are some values," the chart is a table.

Pie, donut, radar, and dual-axis are not supported forms, and the script says so with a pointer to the alternative. That is deliberate: making the honest chart the easy one is more effective than a warning nobody reads.

## What the wrapper fixes

[Observable Plot](https://observablehq.com/plot/) (ISC) does the scales and layout. Its raw output is not safe to drop into a designed document, and each of these is verified behavior:

1. **It writes `--plot-background: white` into a scoped style block** and a `font-family` attribute onto the root `<svg>`. Neither knows about the theme, so a chart on a `field-notes` warm-paper background arrives with a white rectangle behind it. The wrapper rewrites both to `transparent` and `var(--sans)`.

2. **It sets fixed `width` and `height` attributes.** A pixel-sized chart will not scale into a print page. The wrapper removes both, keeps the `viewBox`, and sets `width="100%"` with a `max-width` — merged into the existing `style` attribute, because an element may carry only one and parsers silently discard the extras.

3. **It emits no accessibility shell.** The wrapper adds `role="img"`, `aria-labelledby`, and a namespaced `<title>`/`<desc>` pair, `<title>` first.

4. **Its default mark colors are not the document's tokens.** The wrapper drives fills and strokes from `var(--accent-tint)`, `var(--accent)`, `var(--comparison-fill)`, and `var(--muted)`.

If you render charts by some other route, you still owe the document all four.

## Size to the surface, not to the source

`--size` is not a rendering detail; it is baked into the SVG as a `max-width`, and no amount of CSS on the host page undoes it. A `doc-inline` chart placed on a slide centers itself in the middle of the frame with its labels at reading size, which looks like a design failure rather than a sizing mistake.

Render one variant per surface from the same spec:

```bash
node scripts/render_chart.mjs spec.json --out chart.svg            # doc-inline, 720
node scripts/render_chart.mjs spec-wide.json --out chart-wide.svg  # full-width, 1100
```

## The trap worth knowing about

The obvious way to give one bar the accent is to split the data into two marks — focal and everything else — and style each mark. **This silently breaks the chart.**

Each Plot mark derives its own scale domain from its own data. Split the data and the focal datum lands on one domain and the rest on another, so the bars either misalign or fail to render entirely, while the axes still look correct. It is a convincing failure.

Use one mark with a per-datum `fill` function instead. `scripts/render_chart.mjs` does this, and the comment there explains why.

## Alternatives

**Vega-Lite + `vl-convert`** — if you would rather specify charts as JSON data than as JS calls. `vl-convert` is a Rust binary with Python bindings that renders a spec to static SVG with no browser and no Node. The tradeoff: it bakes colors into the output, so a theme change means re-rendering rather than a CSS swap.

**matplotlib** — for a Python-only toolchain, `savefig(format='svg')` is offline and dependency-light. Its defaults need substantial styling work to match this system, and its text-as-paths behavior needs care or the labels stop being selectable and stop inheriting `var(--sans)`.

**Plotly with Kaleido** — avoid. Kaleido v1 no longer bundles Chrome and looks for a system installation, which reintroduces a heavyweight environment dependency. Plotly's self-contained HTML mode inlines several megabytes of JavaScript and requires JS at read time. Both fail the self-contained rule.
