---
name: diagram-design
description: Design editorial-quality diagrams as self-contained inline SVG — architecture diagrams, flows, sequences, state machines, data models, timelines, layer stacks, quadrants, comparisons, system maps, change views, deployment maps, dependency graphs, journeys, story maps, event models, fishbones, cycles, and evolution maps. Use when explaining how a system is arranged, how a process moves, how components depend on each other, or how options compare; when a Mermaid or draw.io diagram needs to be converted into a document's design system; or when an existing diagram looks auto-generated and needs editorial judgment. Do not use for quantitative charts of measured data (use chart-design), for the surrounding report structure (use analytical-document-design), for UI mockups or wireframes, or for producing editable .drawio files.
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
| What a change adds, removes, and leaves alone | Change view |
| Where each part runs: cluster, namespace, replicas | Deployment map |
| What must finish before what, and which chain sets the date | Dependency graph |
| What a person does, feels and runs into, stage by stage | Journey (service blueprint is a variant) |
| The thinnest slice that works end to end | Story map |
| What the system records and what reads it back | Event model |
| Which families of cause could produce one effect | Fishbone |
| What reinforces what, round a loop | Cycle / flywheel |
| How visible and how evolved each part is | Value-chain evolution map |

Org chart is a tree, UML class and database schema are a data model, steps are a flow, and a pyramid is a layer stack; kanban and traceability are document modules, not figures. Exploded and axonometric views are declined. `references/semantic-patterns.md` says what each visual device claims and maps a reader's question to a form.

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

Decide the destination before drawing, because it is not a cosmetic difference — the same file cannot do both. For the second case, write literal colours for the light reading into the shapes, then add a `<style>` block inside the SVG whose `@media (prefers-color-scheme: dark)` rule overrides those fills and strokes by class, so one file serves both host themes without reaching for the page's tokens.

To get the second case from a tokened figure without redrawing it, run `scripts/export_diagram.mjs figure.svg --theme <name>`: it resolves every token against one theme in Chromium and writes a standalone SVG (or `--format png`). Keep the tokened SVG as the master and export per theme.

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
- **Never encode meaning in lightness alone.** Every theme is legible, and a dark theme inverts which fill reads heavier, so "darker means more" breaks the moment the theme changes. Legends name each encoding in words ("dashed: outside Platform"), never only by swatch.
- **Mark the structure.** `g.node` (`node-focal`, `node-external`, `node-muted`), `path.edge`, `g.edge-label`, `g.boundary`, `g.legend`, `g.callout`, `g.annotation` — the classes are what `scripts/check_diagrams.py` measures.
- **Text fits its box.** A node's label, at an estimated width, stays inside the box with 4px each side (`text-fit`). Shorten, wrap, or widen.
- **Stay inside the budget.** Each size preset allows a number of nodes and edges (`layout-budget`, table in `references/primitives.md`). Over it, split the figure.
- **Legible in every theme.** Text colour is resolved against every theme in `core/themes` and must hold 4.5:1 on its backing (`contrast`).

Full geometry, node, edge, and callout specifications are in `references/primitives.md`.

## Mermaid is an input, not an output

Mermaid is a good notation. Its default rendering is not — stock output brings its own fonts, its own colors, and its own spacing, none of which know about the document they land in. Shipping that into a designed document is visible immediately.

So: accept Mermaid as a source, convert it to a themed SVG, ship the SVG.

| Source | Path |
|---|---|
| Sequence, state, class, ER, flowchart where auto-layout is honest | `scripts/render_diagram.mjs` — renders via `beautiful-mermaid` into an SVG whose colors are `var(--…)` references, so it inherits the document's theme with zero JavaScript |
| Architecture, quadrant, layer stack, timeline, comparison, journey, story map, event model, fishbone, cycle, evolution map — anything where **position carries meaning** | Hand-author from `templates/diagram.svg`. Auto-layout does not know that "closer" means "coupled," so it will destroy the point of the diagram |
| Existing `.drawio`, `.excalidraw`, PlantUML sequence or class, or Mermaid flowchart | `scripts/import_diagram.py` extracts nodes, edges, and groups as JSON with no coordinates; redraw that structure under the rules above — never embed the original |

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
- [ ] Legends name every encoding in words; nothing relies on lightness alone.
- [ ] `scripts/check_diagrams.py figure.svg` reports no findings: shell, colour, markup, grid, overlap, bounds, `text-fit`, `layout-budget`, `contrast`, labels, attachments, legend, emphasis and callouts.

## Paths in this skill

`core/…`, `scripts/…` and `templates/…` are relative to this skill's directory — the
folder that contains this `SKILL.md` — not to your working directory. Each skill carries
its own copy, so it works however it was installed. Prefix them with that directory:

```bash
node "<skill-dir>/scripts/render_diagram.mjs" in.mmd --id x --title "…" --desc "…" --out x.svg
python3 "<skill-dir>/scripts/check_diagrams.py" x.svg          # markup and geometry rules
python3 "<skill-dir>/scripts/import_diagram.py" old.drawio     # structure only, as JSON
python3 "<skill-dir>/scripts/diagram_doctor.py"                # Node, pins, Chromium: what is missing and how to fix it
node "<skill-dir>/scripts/export_diagram.mjs" x.svg --theme executive-navy --format png   # tokens baked for <img>, email, slides
node "<skill-dir>/scripts/render_diagram.mjs" in.mmd --title "…" --desc "…" --system-fonts  # offline: OS font stack
```

## Reference files

- `references/diagram-families.md` — per-form construction rules and failure modes.
- `references/semantic-patterns.md` — what each visual device claims, and reader question to form.
- `references/primitives.md` — node, edge, label, callout, and grid specifications, and layout budgets per size preset.
- `references/mermaid-bridge.md` — the Mermaid renderer, theme bridging, coverage limits.
- `references/importing.md` — draw.io, Mermaid, Excalidraw and PlantUML import: the neutral model, the safety caps, and redrawing.

## Credits

The editorial standard here — deletion as the highest-quality move, every node earning its place, one accent for the one or two things that matter, density around 4/10, hairlines and a 4px grid — is adapted from **[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** (MIT), which established it for Claude Code.

This skill differs in scope: it is one member of a document design system, so its diagrams consume the same `core/` tokens as the reports, charts, and decks they sit inside, rather than carrying a diagram-specific style of their own.
