# Examples

Committed outputs. They serve three jobs at once: CI fixtures, the screenshots in the root README, and a working reference for what each skill produces.

Every example belongs to one fictional engagement, Northwind Ingestion and its RFC 014; the facts are in [`WORLD.md`](WORLD.md). The GitHub Pages homepage walks that engagement in four acts by the reader's job: understand, decide, deliver, run and hand on.

The local Patterns page is [`index.html`](index.html): the reader's-question table first, then the eleven patterns, each with its characteristic modules, its presets and any composed example, followed by the lifecycle map, familiar names, the compatibility profile, and the six-skill strip. GitHub Pages publishes the same page at `/types.html`, beside the story homepage and a modules page with a specimen of every registered module.

All of them rebuild from source — nothing here is hand-maintained.

```bash
npm ci   # Node 22.22.2 or newer; see .nvmrc
python3 scripts/build_examples.py
```

## Documents

| File | Skill | Theme |
|---|---|---|
| `inventory-report.html` | analytical-document-design | editorial-coral |
| `design-doc.html` (and 33 other canonical slugs) | writing-documents | see table below |
| `platform-primer.html` | writing-documents, composed in the `learning` pattern (`type: custom`) | field-notes |
| `capacity-deck.html` | presentation-design | executive-navy |
| `gallery-light.html` / `gallery-dark.html` | diagram-design + chart-design | editorial-coral / console-violet |
| `themes-light.html` / `themes-dark.html` | the token contract itself | four house styles + horizon |
| `proposal-horizon.html` / `proposal-coral.html` | writing-documents (same body as proposal) | horizon / editorial-coral |
| `brand.html` | brand-theme-design exhibit | editorial-coral |

The `-light` / `-dark` pairs exist so the README can swap them with the reader's GitHub theme via `<picture>`. Both halves of each pair inline the **same** SVG figures — only the root `data-theme` differs, so the pair is also a direct demonstration that nothing needs re-rendering.

### writing-documents types

Bodies live in `templates/types/<slug>.html`. The shared world is [`WORLD.md`](WORLD.md). Rebuild with `python3 scripts/build_examples.py`. Each slug also has a Markdown twin `examples/<slug>.md`.

| Pattern | Files | Default themes |
|---|---|---|
| decision | `design-doc`, `discovery`, `proposal`, `project-charter`, `estimate`, `change-request` | field-notes (`design-doc`, `discovery`); executive-navy (the rest) |
| record | `adr` | field-notes |
| contract | `spec`, `api-contract`, `reference`, `requirements`, `statement-of-work`, `support-model` | field-notes; console-violet (`api-contract`, `reference`); executive-navy (`statement-of-work`) |
| procedure | `handoff`, `how-to`, `runbook` | field-notes, editorial-coral, console-violet |
| learning | `explanation`, `onboarding`, `tutorial` | field-notes, editorial-coral |
| system | `architecture`, `design-handoff` | field-notes, editorial-coral |
| incident | `postmortem` | console-violet |
| suite | `service-docs` | field-notes |
| plan | `delivery-plan`, `migration-plan`, `test-strategy` | executive-navy, console-violet, editorial-coral |
| assurance | `test-report`, `threat-model`, `readiness-review`, `risk-register` | editorial-coral, console-violet, console-violet, executive-navy |
| brief | `status-report`, `release-notes`, `workshop-summary`, `incident-update` | executive-navy, editorial-coral, field-notes, console-violet |

`mulesoft` remains a compatibility profile of canonical `service-docs`; it is
not a second type.

### Composed examples

A composed example has no type. Its Markdown front matter declares `type:
custom`, its `pattern`, the `modules` it uses, and its `nearest-type`; its body
lives in `templates/composed/<slug>.html` and may use only modules the registry
allows for that pattern. `platform-primer` is the worked example: a primer for
engineers joining Platform from batch work, nearest type `explanation`.

Pattern and theme are independent root attributes. See
[`../core/document-patterns.md`](../core/document-patterns.md) for the contract.

## Figures

| File | Form | Produced by |
|---|---|---|
| `platform-architecture.svg` | Architecture diagram | Hand-authored from `templates/diagram.svg` |
| `queue-split-change.svg` | Change view | Hand-authored |
| `ingest-deployment.svg` | Deployment map | Hand-authored |
| `workstream-dependencies.svg` | Dependency graph | Hand-authored |
| `ingestion-path.svg` | Sequence diagram | `render_diagram.mjs` (Mermaid → SVG) |
| `footprint-by-function.svg` | Ranked bars | `render_chart.mjs` |
| `cohorts-by-year.svg` | Columns | `render_chart.mjs` |
| `latency-p99.svg` | Line | `render_chart.mjs` |
| `estimate-bridge.svg` | Waterfall bridge | `render_chart.mjs` |

Sources live in `specs/` — a `.mmd` for the rendered diagram, a JSON spec per chart. Hand-authored figures are their own source and pass `scripts/check_diagrams.py`.

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

The report is 3 pages of A4; the deck is 14 slides on 14 pages (title, agenda, statements, dividers, table, metrics, chart, diagrams, comparison, closing). Open the PDF and look at it — page count alone proves nothing, since a drop in pages can mean clipped overflow rather than better layout.
