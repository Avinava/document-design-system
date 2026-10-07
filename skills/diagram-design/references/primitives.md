# Primitives

Geometry and component specifications. These exist so diagrams from different sessions look like they came from the same system.

All values are on a 4px grid. Off-grid geometry is the most reliable visual tell of an auto-generated diagram, and it is free to avoid.

## Contents

- [Markup contract](#markup-contract)
- [Canvas and grid](#canvas-and-grid)
- [Nodes](#nodes)
- [Edges](#edges)
- [Labels](#labels)
- [Boundaries and groups](#boundaries-and-groups)
- [Callouts](#callouts)
- [Legends](#legends)
- [Form geometry](#form-geometry)
- [The SVG shell](#the-svg-shell)
- [Checking the rules](#checking-the-rules)

## Markup contract

A hand-authored diagram marks its structure with classes, so a checker can measure it and a reader of the source can find the parts. Every element directly under `<svg>` (after `<title>`, `<desc>`, `<defs>`) is one of these:

| Element | Class | Holds |
|---|---|---|
| `<g>` | `node` + optional `node-focal`, `node-external`, `node-muted` | The box `<rect>` first, then its `<text>` lines |
| `<path>` or `<line>` | `edge` | One connector |
| `<g>` | `edge-label` | A backing `<rect>` first, then the `<text>` |
| `<g>` | `boundary` | The dashed `<rect>` and its label |
| `<g>` | `legend` | Everything in the key, including a change ledger |
| `<g>` | `callout` | The leader `<path>` and its italic `<text>` |
| `<g>` | `annotation` | Free text: state labels, column tags, notes |

Nothing is drawn unmarked. A bare `<g>` or a loose `<text>` is a part the checker cannot reason about and a reviewer cannot find.

## Canvas and grid

| Size | viewBox width | Use |
|---|---|---|
| `doc-inline` | 720 | Fits a text column in a report |
| `full-width` | 1100 | Full content width, standalone figure |
| `print-portrait` | 640 | A4 portrait with 14mm margins |
| `print-landscape` | 980 | A4 landscape appendix |

Height follows content. Never fix a height that crops.

- Base unit: **4px**. Every x, y, width, height, and gap is a multiple.
- Outer padding: **24px** minimum on all sides. Content touching the viewBox edge clips in print.
- Node gap: **32px** minimum horizontally, **24px** vertically. Tighter than this and grouping stops reading.
- Target density around **4/10**. If the frame looks full, remove something rather than shrinking everything.

## Nodes

```html
<g class="node">
  <rect x="24" y="24" width="160" height="64" rx="6"
        fill="var(--surface)" stroke="var(--rule-strong)" stroke-width="1"/>
  <text x="104" y="60" class="node-label" text-anchor="middle">Gateway</text>
</g>
```

| Property | Value |
|---|---|
| Default size | 160 × 64 (grows to fit label; keep width a multiple of 8) |
| Radius | `var(--radius-md)` — 0–8px, never more |
| Fill | `var(--surface)` |
| Stroke | `var(--rule-strong)`, 1px |
| Label | `var(--sans)`, 13px, `var(--ink)`, centered |

Variants:

- **Focal** — `fill: var(--accent-tint)`, `stroke: var(--accent)`. One or two per diagram.
- **External** — `stroke-dasharray: 4 3`, label in `var(--soft)`. For systems outside the boundary.
- **Muted** — `stroke: var(--rule)`, label in `var(--muted)`. For context nodes that are present but not the subject.

Never use fill color to encode a category. Categories get labels or shape, so they survive grayscale.

## Edges

```html
<path class="edge" d="M184 56 H 248" marker-end="url(#arrow)"/>
```

| Property | Value |
|---|---|
| Stroke | `var(--muted)`, 1px |
| Focal stroke | `var(--accent)`, 1.5px |
| Arrowhead | 8px, filled, same color as the stroke |
| Corners | Orthogonal with a 8px radius, or a single gentle curve — never a diagonal through other nodes |

Semantics:

- **Solid** — synchronous, direct, or primary.
- **Dashed** (`4 3`) — asynchronous, optional, or inferred.
- **Dotted** (`1 3`) — a reference or a weak relationship.

Define the arrow marker once per document:

```html
<defs>
  <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4"
          markerWidth="8" markerHeight="8" orient="auto-start-reverse">
    <path d="M0,0 L8,4 L0,8 z" fill="var(--muted)"/>
  </marker>
</defs>
```

Marker IDs are document-global. Prefix them per diagram (`dg-ingest-arrow`) when a page carries more than one figure, or the second diagram will silently reuse the first one's markers.

### Routing rules

Four rules that separate a drawn diagram from a generated one. All four are checkable, which is why they are worth stating numerically.

**1. Orthogonal, with rounded corners.** Every bend is a quarter-arc at `r=8` (`r=6` in tight layouts). Use a straight `<line>` only when the endpoints share an x or a y. Diagonals through a layout read as auto-generated.

```html
<!-- right then down, from (x1,y1) to (x2,y2), mid = (x1+x2)/2 -->
<path d="M x1,y1 H mid-8 Q mid,y1 mid,y1+8 V y2-8 Q mid,y2 mid+8,y2 H x2"
      fill="none" stroke="var(--muted)" stroke-width="1"
      marker-end="url(#dg-slug-arrow)"/>
```

**2. Labels sit near the edge, not on it.** The backing rect prevents the line striking through the text, but the label still needs a **6–10px gap** from the stroke. A label flush against its edge makes the edge untraceable, which defeats the label.

**3. Edges must not overlap or cross where it can be avoided.** A crossing implies a relationship that is not there. Where two edges genuinely must cross, bridge one with a hop — and bridge the less important of the two, never both:

```html
<path d="M x1,y H cx-8 a 8,8 0 0,1 16,0 H x2" fill="none" stroke="var(--muted)"/>
```

If you find yourself stacking connectors, the layout is wrong or the diagram is too big.

**4. Fan the attachment points on a shared edge.** Several edges meeting one side of a node must not converge on the same point. For `N` connectors on an edge of length `L`, connector `k` (counting from 1) attaches at `L * k / (N + 1)` from the leading corner — at least 12px apart, 8px for small nodes.

An edge that must pass behind a node it does not connect to should be dashed, to signal transit rather than interaction. Better: reroute.

## Labels

| Role | Font | Size | Color |
|---|---|---|---|
| Diagram title | `var(--display)` | 15px, 600 | `var(--ink)` |
| Node label | `var(--sans)` | 13px | `var(--ink)` |
| Edge label | `var(--sans)` | 11px | `var(--muted)` |
| Technical identifier | `var(--mono)` | 11px | `var(--muted)` |
| Boundary label | `var(--sans)` | 11px, uppercase, 0.06em tracking | `var(--soft)` |

Edge labels sit **beside** their edge, 6–10px clear of the stroke (routing rule 2), in a `g.edge-label` with a `var(--paper)` backing rect so any other line that passes behind does not strike through the text:

```html
<g class="edge-label">
  <rect x="200" y="36" width="48" height="16" fill="var(--paper)"/>
  <text x="224" y="48" text-anchor="middle">async</text>
</g>
```

Paint the label before the nodes it sits between, and keep its backing clear of every node: a node painted after a label hides it.

SVG has no text wrapping. Break long labels into explicit `<tspan>` lines with a 15px line step, or shorten the label. Do not let a label overflow its node.

## Boundaries and groups

```html
<g class="boundary">
  <rect x="16" y="16" width="400" height="200" rx="6"
        fill="none" stroke="var(--rule-strong)" stroke-width="1" stroke-dasharray="4 3"/>
  <text x="28" y="36" class="boundary-label">VPC</text>
</g>
```

- Dashed, no fill — a filled boundary competes with its nodes.
- Label top-left, inside the boundary.
- Minimum 16px padding between the boundary and the nodes it contains.
- Nesting beyond two levels stops reading. Split the diagram instead.

## Callouts

An editorial aside pointing at one element — the reason a diagram makes an argument rather than just documenting.

```html
<g class="callout">
  <path d="M320 120 C 360 120, 380 96, 408 96"
        fill="none" stroke="var(--accent)" stroke-width="1" stroke-dasharray="3 3"/>
  <text x="416" y="100" class="callout-text">no failover</text>
</g>
```

- Dashed Bézier leader in `var(--accent)`, never an arrowhead — a callout points, it does not flow.
- Text in `var(--sans)` italic, 12px, `var(--ink)`.
- At most **two** callouts per diagram. A third means the diagram is trying to make too many arguments.

## Legends

Prefer direct labelling. A legend is a lookup table the reader has to hold in memory.

When one is genuinely needed (repeated encodings across several diagrams):

- Place it inside the `viewBox`, or it will be lost on export and in print.
- Horizontal, below the diagram, 11px minimum, `var(--muted)`.
- Encode by line style or shape, not by fill color alone.
- Name each encoding in words next to its swatch: "dashed: outside Platform", not "dashed".
- Never let lightness carry meaning on its own. A dark theme inverts which fill reads heavier, so a "darker means more" key is true in one theme and false in the next.

## Form geometry

**Change view.** Two states stacked on shared columns: column pitch is node width plus gap (88 + 28 = 116 at `doc-inline`), so an unchanged node sits directly above itself. State labels (`TODAY`, `RFC 014 · PROPOSED`) are boundary-label style at the top-left of each band; a 1px `var(--rule)` divides the bands. Change tags are 11px `var(--mono)` set 8px above the node or column they mark. The ledger sits below a second divider: identifier column in `var(--mono)` 11px, change word in `var(--muted)`, note in 12px sans, rows 22px apart.

**Deployment map.** Cluster boundary, then namespace boundary 16px inside it, then workloads 16px inside that. Replica pips are 24 × 16, `rx` 2, 8px apart, on a row 12px above the workload's bottom edge; the next replica is the same pip dashed (`3 2`). Dependencies sit at least 40px outside the outermost boundary so their edges visibly cross it.

**Dependency graph.** One column per date, node pitch 140 at `doc-inline` (112 + 28); rows 88 apart (64 + 24). Edges bend once each way with `r=6` quarter-arcs in the column gap. Inputs converging on one gate fan along its side at least 12px apart; the worked example spaces three of them 20px apart, centred on the node.

## The SVG shell

```html
<figure class="diagram">
  <svg role="img" aria-labelledby="dg-ingest-title dg-ingest-desc"
       viewBox="0 0 720 380" width="100%">
    <title id="dg-ingest-title">Ingestion path</title>
    <desc id="dg-ingest-desc">Events enter through the gateway, buffer in the queue, and land in the warehouse. The queue is the only component without a failover.</desc>
    <defs><!-- markers, prefixed per diagram --></defs>
    <!-- boundaries, then edges, then nodes, then callouts -->
  </svg>
  <figcaption>Ingestion path, as of 2026-08-12.</figcaption>
</figure>
```

Paint order matters: boundaries first, then edges, then nodes, then callouts. Nodes drawn after edges hide the line ends that would otherwise poke through their borders.

Keep `<figure>` non-breaking in print so the caption never separates from the diagram — `core/print.css` handles this.

The root `<svg>` carries a `viewBox` and either no size or `width="100%"`, never a pixel width or height: a fixed size stops the figure scaling into a column or a printed page. Every `id` starts with the figure's slug — the `<title>` id minus `-title`.

## Checking the rules

`scripts/check_diagrams.py` reads the coordinates and reports each broken rule by a stable ID, without rendering anything:

```bash
python3 scripts/check_diagrams.py figure.svg        # or a page: every titled inline <svg>
python3 scripts/check_diagrams.py --rules           # list the rule IDs
```

It checks the shell, `var()`-only colour, the markup contract, the 4px grid on rects, node overlap, the `viewBox` bounds (text estimated at 0.6em per character), edge-label occlusion and its 6px gap, the 12px attachment fan, the 11px legend floor, one emphasis family, and at most two callouts. Output of `scripts/render_diagram.mjs` is marked `data-renderer` and gets only the shell and bounds rules, because the renderer owns its layout.
