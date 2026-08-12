---
name: diagram-design
description: Design editorial-quality diagrams as self-contained inline SVG — architecture diagrams, flows, sequences, state machines, data models, timelines, layer stacks, quadrants, comparisons, and system maps. Use when explaining how a system is arranged, how a process moves, how components depend on each other, or how options compare; when a Mermaid or draw.io diagram needs to be converted into a document's design system; or when an existing diagram looks auto-generated and needs editorial judgment. Do not use for quantitative charts of measured data (use chart-design), for the surrounding report structure (use analytical-document-design), for UI mockups or wireframes, or for producing editable .drawio files.
---

# Diagram Design

A diagram earns its place when the **arrangement itself carries meaning** that a sentence or a list cannot carry as fast.

That is the whole test. Boxes-and-arrows restating a numbered list is slower than the list. A flowchart of a linear three-step process is worse than three sentences. Before drawing anything, say what the reader will understand from the *shape* that they would not get from the prose.

If the answer is "nothing," write the prose.

## The standard

The highest-quality move is usually deletion. Every node earns its place. Target density around 4/10 — a diagram that fills its frame is almost always doing too much.

The accent color is reserved for the one or two things the reader should look at first. Everything else is ink and hairlines.

*(This standard is adapted from [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design), MIT. See Credits.)*

## Choosing a form

Match the form to the relationship being shown, not to the data you happen to have.

| The reader needs to understand | Form |
|---|---|
| How parts are arranged and what talks to what | Architecture / system map |
| How something moves through steps, with branches | Flow |
| Who calls whom, in what order, over time | Sequence |
| What states exist and what transitions between them | State machine |
| How entities relate and what they hold | Data model |
| What happened when, and in what order | Timeline |
| How responsibility is divided across actors | Swimlane |
| How options compare on two independent axes | Quadrant |
| What sits on top of what | Layer stack |
| How something narrows or concentrates | Funnel |
| How sets overlap | Venn |
| How one thing decomposes into parts | Tree / nested |

If the answer is "several of these," the diagram is doing too much. Split it. Two clear diagrams beat one complete one — a reader who has to decode a diagram has already lost the time the diagram was meant to save.

For per-form construction rules — what to label, where to place the accent, how to handle overflow — read `references/diagram-families.md`.

## Output

Inline SVG in the document. Not a linked image, not a canvas, not a client-side renderer.

Inline SVG is the only form that scales into print without blurring, inherits the document's tokens, stays selectable and searchable, and survives being emailed as a single file.

Every diagram:

```html
<svg role="img" aria-labelledby="dg-ingest-title dg-ingest-desc" viewBox="0 0 720 380">
  <title id="dg-ingest-title">Ingestion path</title>
  <desc id="dg-ingest-desc">Events enter through the gateway, buffer in the queue, and land in the warehouse. The queue is the only component without a failover.</desc>
  ...
</svg>
```

`<title>` first, unique IDs prefixed with the diagram's slug, and a `viewBox` on every SVG. The `<desc>` states what the arrangement shows — including the thing the accent is pointing at. See `core/a11y.md`.

### Inline or `<img>` changes the rules

An SVG referenced through `<img src="…">` — a README banner, an email, an embed on a site you do not control — renders as an **isolated document**. The host page's custom properties never reach it, so `fill="var(--accent)"` resolves to nothing and the shape disappears.

| Destination | Colors | Theming |
|---|---|---|
| Inline in the document | `var(--…)` references | Follows the document's `data-theme` |
| `<img>`, email, external embed | Literal values | Self-contained; use `@media (prefers-color-scheme: dark)` inside the SVG's own `<style>` |

Decide the destination before drawing, because it is not a cosmetic difference — the same file cannot do both. `assets/banner.svg` is the worked example of the second case.

## Visual rules

The token contract is in `core/tokens.md` and applies in full. Diagram-specific rules:

- **One accent.** Reserved for the one or two elements the reader should see first — the bottleneck, the boundary, the thing that changed. An accent on every node is the same as no accent.
- **Hairlines.** 1px strokes, `var(--rule)` for structure and `var(--rule-strong)` for boundaries. Thick borders read as UI chrome.
- **No shadows, no gradients, no glow.** Depth comes from grouping and whitespace.
- **Everything on a 4px grid.** Positions, sizes, gaps. Off-grid geometry is the single most reliable tell of an auto-generated diagram.
- **Three type roles.** `var(--display)` for the diagram title, `var(--sans)` for node labels, `var(--mono)` for technical identifiers, ports, and versions. Nothing else.
- **Label every edge that isn't obvious.** An unlabelled arrow means "leads to," and nothing else. If it means "on failure," "async," or "read-only," say so.
- **Direction is a decision.** Left-to-right for process and time. Top-to-bottom for hierarchy and layers. Do not mix within one diagram.
- **No orphan nodes.** Anything unconnected either needs an edge or does not belong.

Full geometry, node, edge, and callout specifications are in `references/primitives.md`.

## Mermaid is an input, not an output

Mermaid is a good notation. Its default rendering is not — stock output brings its own fonts, its own colors, and its own spacing, none of which know about the document they land in. Shipping that into a designed document is visible immediately.

So: accept Mermaid as a source, convert it to a themed SVG, ship the SVG.

| Source | Path |
|---|---|
| Sequence, state, class, ER, flowchart where auto-layout is honest | `scripts/render_diagram.mjs` — renders via `beautiful-mermaid` into an SVG whose colors are `var(--…)` references, so it inherits the document's theme with zero JavaScript |
| Architecture, quadrant, layer stack, timeline, comparison — anything where **position carries meaning** | Hand-author from `templates/diagram.svg`. Auto-layout does not know that "closer" means "coupled," so it will destroy the point of the diagram |
| Existing `.mmd`, `.drawio`, or a diagram in a doc | Convert, then apply the rules above — do not embed as-is |

The rule underneath: **auto-layout is acceptable when the arrangement is arbitrary, and unacceptable when the arrangement is the message.**

See `references/mermaid-bridge.md` for the renderer, its theme bridge, and its coverage limits.

## Sizing and audience

Two dials worth setting deliberately, because they change what belongs in the diagram:

**Size** — `doc-inline` (fits a text column, ~720px wide), `full-width` (~1100px), `print-portrait`, `print-landscape`. A diagram drawn for full width and dropped into a text column becomes unreadable rather than smaller.

**Audience** — an engineer diagram can name protocols, ports, and versions; an executive diagram cannot, and showing them is not rigor, it is noise. When both audiences need it, make two diagrams from the same model rather than one that half-serves each.

## Before delivering

- [ ] The arrangement carries meaning prose could not carry as fast.
- [ ] Every node earns its place; nothing is there for symmetry.
- [ ] The accent marks one or two things, not a category.
- [ ] Every non-obvious edge is labelled.
- [ ] Geometry sits on the 4px grid.
- [ ] `viewBox`, `<title>` first, `<desc>`, unique IDs.
- [ ] Legible in grayscale and at print width.
- [ ] No color-only encoding.
- [ ] No shadows, gradients, or glow.
- [ ] Renders correctly at the intended size, not just at authoring size.

## Paths in this skill

`core/…` and `scripts/…` are relative to the repo root. When this is installed as a
plugin your working directory is your own project, not the plugin, so prefix them:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit_theme.py" theme.css
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin's own
directory. Working inside the repo itself, the bare paths are correct as written.

## Reference files

- `references/diagram-families.md` — per-form construction rules and failure modes.
- `references/primitives.md` — node, edge, label, callout, and grid specifications.
- `references/mermaid-bridge.md` — Mermaid and draw.io import, the renderer, theme bridging, coverage limits.

## Credits

The editorial standard here — deletion as the highest-quality move, every node earning its place, one accent for the one or two things that matter, density around 4/10, hairlines and a 4px grid — is adapted from **[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** (MIT), which established it for Claude Code.

This skill differs in scope: it is one member of a document design system, so its diagrams consume the same `core/` tokens as the reports, charts, and decks they sit inside, rather than carrying a diagram-specific style of their own.
