<p align="center">
  <img src="assets/banner.svg" alt="document-design-system — reports, diagrams, charts, decks, and thirty-four document types as self-contained HTML" width="960" />
</p>

<p align="center">
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-2d3142"></a>
  <img alt="6 skills" src="https://img.shields.io/badge/skills-6-eb6c36">
  <img alt="34 document types" src="https://img.shields.io/badge/document%20types-34-2d3142">
  <img alt="no runtime dependencies" src="https://img.shields.io/badge/runtime%20deps-none-2d3142">
  <a href="https://github.com/Avinava/document-design-system/actions/workflows/validate.yml"><img alt="validate" src="https://github.com/Avinava/document-design-system/actions/workflows/validate.yml/badge.svg"></a>
</p>

---

**A design system for documents, and a skill that writes them.** Six skills over one token contract — analytical reports, diagrams, charts, decks, thirty-four document types, and brand theming. Writing lands as Markdown in your repo by default. Designed HTML is opt-in: no JavaScript to read, no build step to open, and it prints.

Most document tooling is welded to one output format or one client's brand. This is the discipline itself: what to measure, when a chart earns its place, how to structure an argument, and one shared set of semantic tokens underneath so a report, the diagram inside it, and the deck derived from it all look like one system.

```
/plugin marketplace add Avinava/document-design-system
/plugin install document-design-system@document-design-system
```

Then `/plugin` to confirm it is installed. Ask for a report, or `/document-design-system:handoff` (or `adr`, `design-doc`, …) — Markdown in the repo unless you asked for HTML.

The repetition on the second line is not a typo. `@` reads as "from": it names a *plugin*
and the *catalog* it came from, and this repository publishes its own catalog containing
this one plugin, so both halves are the same word. The catalog is named after the
repository deliberately — marketplace names are global per user, so two repositories
publishing catalogs under a shared name would silently replace one another and orphan the
plugins installed from the loser. A per-repository name is unique by construction and
cannot collide that way.

<details>
<summary>Or install it as plain skills, without the plugin system</summary>

```bash
npx skills add Avinava/document-design-system                      # all six
npx skills add Avinava/document-design-system --skill chart-design # just one
```

Each skill is self-contained: it carries its own copy of the `core/` tokens, the
`scripts/` and the `templates/` it uses, so a skill works wherever it lands. Those copies
are generated from the repository-level `core/`, `scripts/` and `templates/` by
`python3 scripts/sync_skill_assets.py`; edit the originals and re-run it, never the copies.

Without the CLI, copy any `skills/<name>/` directory into `.claude/skills/` (or your
agent's skills directory).

The slash commands such as `/document-design-system:handoff` ship only with the plugin.

</details>

---

## What it produces

Every image below is a committed example in [`examples/`](examples/), rebuilt from source by `python scripts/build_examples.py` and captured by `python scripts/shoot_examples.py`. Nothing is a mockup.

### Several voices, one contract

Identical markup in all four panels — only `data-theme` differs. Surfaces, ink, accent, typography, border character, and the methodology treatment all follow from the token contract.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/themes-dark.png">
  <img alt="The same content block rendered under editorial-coral, executive-navy, field-notes, and console-violet" src="docs/screenshots/themes-light.png">
</picture>

| Theme | For | |
|---|---|---|
| `editorial-coral` | General analytical reports, portfolio reviews | light · default |
| `executive-navy` | Board, finance, governance | light |
| `field-notes` | Research, audit, operational review | light |
| `console-violet` | Engineering readouts, ops reviews, incident write-ups | **dark** |
| `horizon` | A client brand applied — what `brand-theme-design` produces | light |
| `brand-template` | Your own brand — copy, fill every TODO, rename | — |

<sub>This image follows your GitHub theme. [source](examples/themes-light.html)</sub>

### Analytical report — evidence-led, reconciled, printable

Metric semantics, named denominators, a limit ledger, and a methodology block. The one that refuses to call a snapshot cohort "growth".

[![Analytical report](docs/screenshots/analytical-report.png)](examples/inventory-report.html)

Further down the same document — cohort columns and an attribution table that flags which "owners" are actually deployment accounts:

[![Analytical report detail](docs/screenshots/analytical-report-detail.png)](examples/inventory-report.html)

<sub>`analytical-document-design` · theme `editorial-coral` · [source](examples/inventory-report.html) · prints to 3 A4 pages</sub>

### Document types — the writing gallery

`writing-documents` writes Markdown in *your* repo by default (`/document-design-system:handoff`, `requirements`, `delivery-plan`, …). Designed HTML is opt-in. The files below are the designed gallery: one Northwind Ingestion world, thirty-four canonical shapes.

Browse them on the [live site](https://avinava.github.io/document-design-system/types.html), or [`examples/index.html`](examples/index.html) locally.

The visual system has two independent axes. A **pattern** controls how the page
is read; a **theme** controls its voice. Prose stays at 62–72 characters while
maps, tables, timelines, comparisons, and registers use the space they need.

| Pattern | Reading movement | Types |
|---|---|---|
| `decision` | ask → choices → trade-offs → next move | `design-doc`, `discovery`, `proposal`, `project-charter`, `estimate`, `change-request` |
| `record` | status → decision → consequences | `adr` |
| `contract` | definitions → exact rules → specimens → compliance | `spec`, `api-contract`, `reference`, `requirements`, `statement-of-work`, `support-model` |
| `procedure` | safety → steps → verification → recovery | `handoff`, `how-to`, `runbook` |
| `learning` | context → practice → checkpoint → takeaway | `explanation`, `onboarding`, `tutorial` |
| `system` | map → boundaries → interfaces → states | `architecture`, `design-handoff` |
| `incident` | impact → timeline → cause → owned action | `postmortem` |
| `suite` | document map → ownership → freshness | `service-docs` |
| `plan` | baseline → workstreams → dependencies → gates | `delivery-plan`, `migration-plan`, `test-strategy` |
| `assurance` | verdict → evidence → findings → residual risk | `test-report`, `threat-model`, `readiness-review`, `risk-register` |
| `brief` | current state → material change → action → next update | `status-report`, `release-notes`, `workshop-summary`, `incident-update` |

| | |
|---|---|
| [![Decision pattern](docs/screenshots/design-doc.png)](examples/design-doc.html) | [![Contract pattern](docs/screenshots/api-contract.png)](examples/api-contract.html) |
| `decision` — comparison and decision rail | `contract` — wide rules and specimens |
| [![Procedure pattern](docs/screenshots/runbook.png)](examples/runbook.html) | [![Incident pattern](docs/screenshots/postmortem.png)](examples/postmortem.html) |
| `procedure` — safety and checkpoints | `incident` — impact strip and timeline |

| | |
|---|---|
| [![Plan pattern](docs/screenshots/delivery-plan.png)](examples/delivery-plan.html) | [![Assurance pattern](docs/screenshots/threat-model.png)](examples/threat-model.html) |
| `plan` — milestone rail, workstreams, dependencies, gates | `assurance` — verdict beside evidence and residual risk |
| [![Brief pattern](docs/screenshots/status-report.png)](examples/status-report.html) | [![Suite pattern](docs/screenshots/service-docs.png)](examples/service-docs.html) |
| `brief` — health, material movement, required action | `suite` — document ownership and freshness |

The [live pattern gallery](https://avinava.github.io/document-design-system/types.html)
shows all eleven families and all thirty-four canonical types. The full contract lives in
[`core/document-patterns.md`](core/document-patterns.md).

[![Eleven document patterns and consultancy lifecycle navigation](docs/screenshots/patterns-gallery.png)](examples/index.html)

<sub>Pattern-first navigation, reader questions, default themes, and lightweight previews. [Open locally](examples/index.html).</sub>

#### Canonical catalog

Every slug in the pattern table above is a `/document-design-system:<slug>`
command with paired HTML and Markdown in [`examples/`](examples/). Familiar
names such as HLD, LLD, TDD, PRD, API spec, PRR, and RAID route to those
owners instead of becoming duplicate types.

`/document-design-system:mulesoft` remains a backward-compatible specialized
profile of `service-docs`.

### Deck — a presented ask, not a document with page breaks

RFC 014 for the Platform director. Fourteen slides, one idea each, claim titles. Every `presentation-design` slide type is in the file. Type scales with the slide via container queries. No JavaScript: a deck that renders blank without JS is not a deliverable.

| | |
|---|---|
| [![Title slide](docs/screenshots/deck-title.png)](examples/capacity-deck.html) | [![Statement slide](docs/screenshots/deck-statement.png)](examples/capacity-deck.html) |
| Title names the argument, not the meeting | Statement slides are reserved for the two or three lines that should stick |
| [![Comparison slide](docs/screenshots/deck-compare.png)](examples/capacity-deck.html) | [![Chart slide](docs/screenshots/deck-chart.png)](examples/capacity-deck.html) |
| Three options on the same criteria — accenting a column is a recommendation | Chart at `full-width`. A document chart dropped on a slide shrinks its labels to nothing |
| [![Metric slide](docs/screenshots/deck-metric.png)](examples/capacity-deck.html) | [![Incident table](docs/screenshots/deck-table.png)](examples/capacity-deck.html) |
| Three numbers, one accent, one ledger underneath | Six rows is the ceiling; the last halt is the focal row |
| [![Diagram slide](docs/screenshots/deck-diagram.png)](examples/capacity-deck.html) | [![Section divider](docs/screenshots/deck-divider.png)](examples/capacity-deck.html) |
| One path, one failure — the current queue has no failover | Dividers mark a shift; a few words on an accent field |

<sub>`presentation-design` · theme `executive-navy` · [source](examples/capacity-deck.html) · 14 slides → 14 PDF pages · also [closing](docs/screenshots/deck-close.png)</sub>

### Figures — diagrams and charts on one token set

Six forms, one accent, all resolving against the document's tokens at view time. This image follows your GitHub theme — and both renderings use the **same SVG files**, which is the clearest proof the token indirection works.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/gallery-dark.png">
  <img alt="Figure gallery: architecture diagram, sequence diagram, ranked bars, columns, line chart, and a limit ledger" src="docs/screenshots/gallery-light.png">
</picture>

<sub>`diagram-design` + `chart-design` · rendered in `editorial-coral` and `console-violet` — the same SVG files, no re-render · [source](examples/gallery-light.html)</sub>

| Figure | Path | Why that path |
|---|---|---|
| Architecture | Hand-authored SVG | Position carries coupling — auto-layout would assert relationships nobody intended |
| Sequence | Mermaid → prerendered SVG | Order is dictated by the protocol, so auto-layout is honest |
| Ranked bars | Observable Plot → SVG | Sorted descending, zero baseline, one focal bar |
| Columns | Observable Plot → SVG | Chronological, never sorted by value |
| Line | Observable Plot → SVG | Straight segments; a spline invents readings between points |
| Limit ledger | Hand-authored SVG | A linear track beats a gauge — same value, stated precisely |

### Same document, three voices

The proposal you send. Identical markup; only `data-theme` changes. Navy is the system's board voice. Horizon is a client brand. Coral is the default analytical voice.

| | | |
|---|---|---|
| [![Proposal in executive-navy](docs/screenshots/proposal.png)](examples/proposal.html) | [![Proposal in horizon](docs/screenshots/proposal-horizon.png)](examples/proposal-horizon.html) | [![Proposal in editorial-coral](docs/screenshots/proposal-coral.png)](examples/proposal-coral.html) |
| `executive-navy` — board packet | `horizon` — client brand, the one you send | `editorial-coral` — default analytical |

<sub>Same `templates/types/proposal.html` body. [How horizon was built](examples/brand.html).</sub>

### Brand theming — a guide in, a theme out

Point it at a brand guide PDF, a website, a screenshot, or a few hex values. It extracts with provenance, maps to the semantic roles, and audits the result — because brand colors are chosen for logos, and routinely fail contrast for body text.

`horizon` is that process, finished: the mapping in [`examples/brand.html`](examples/brand.html), the theme in `core/themes/horizon.css`, the document in [`proposal-horizon.html`](examples/proposal-horizon.html).

```bash
python3 scripts/extract_site_theme.py https://example.com   # computed styles, not pixels
python3 scripts/audit_theme.py core/themes/horizon.css      # every pair, exact thresholds
```

The auditor is the part that matters. Building it immediately found two defects in this repo's own default theme: `--accent-ink` on `--accent` was **3.12:1**, failing AA, and the accent sat 13° from `--warning`. Both are fixed. Horizon's brand green/orange/red failed as text on white and were darkened (mapping.md remedy 2) before the theme shipped.

<sub>`brand-theme-design` · [skill](skills/brand-theme-design/SKILL.md) · [exhibit](examples/brand.html) · [themes](examples/themes-light.html)</sub>

---

## The one idea

> **Everything renders to an SVG string at authoring time. The only thing still live in the shipped HTML is CSS custom properties.**

That single rule is what makes the rest cohere. Diagrams, charts, decks, and reports share one token set, retheme with zero JavaScript, survive print, and stay one file.

It also settles the perennial Mermaid question. Mermaid is a fine *notation* and a poor *output format* — its default rendering brings its own fonts, colors, and spacing, none of which know about the document they land in. So Mermaid is an input: prerendered through [`beautiful-mermaid`](https://github.com/lukilabs/beautiful-mermaid) into an SVG whose colors are `var(--…)` references.

Open any example and change one attribute:

```html
<html lang="en" data-theme="editorial-coral">   →   data-theme="executive-navy"
```

The page, the chart's focal bar, and the diagram's arrowheads all move together. Nothing re-renders and no JavaScript runs.

---

## The skills

Each row is a committed example in [`examples/`](examples/), not a description of intent. The gallery above is the proof.

| Skill | Owns | Does **not** own | Example |
|---|---|---|---|
| **[analytical-document-design](skills/analytical-document-design/SKILL.md)** | Evidence models, control totals, metric semantics, cohort/time semantics, classification confidence, report architecture, methodology | Prose-first docs, slides, standalone charts | [inventory-report](examples/inventory-report.html) |
| **[diagram-design](skills/diagram-design/SKILL.md)** | When a diagram earns its place, form routing, layout/edge/label rules, Mermaid→SVG prerender, hand-SVG for concept diagrams | Quantitative charts, UI mockups, editable `.drawio` | [figure gallery](examples/gallery-light.html) |
| **[chart-design](skills/chart-design/SKILL.md)** | Chart-type selection, axis honesty, encoding rules, palettes derived from tokens, grayscale survival | Narrative structure, dashboards-as-applications | [figure gallery](examples/gallery-light.html) |
| **[presentation-design](skills/presentation-design/SKILL.md)** | 16:9 HTML slides; claim titles; one idea per slide; title, agenda, statement, divider, metric, chart, diagram, comparison, table, closing; PDF one slide per page | Documents meant to be read rather than presented; editable `.pptx` | [capacity-deck](examples/capacity-deck.html) |
| **[writing-documents](skills/writing-documents/SKILL.md)** | Thirty-four types across eleven patterns (design-doc, requirements, delivery-plan, readiness-review, Diátaxis, service-docs, …); Markdown by default; designed HTML only when asked | Metric-led reports; casual edits to existing markdown; restyling into HTML unprompted | [type gallery](examples/index.html) |
| **[brand-theme-design](skills/brand-theme-design/SKILL.md)** | Turning a brand into a theme — extraction from a guide, site, or screenshot; mapping to semantic roles; contrast auditing | Picking between themes that already ship; restyling one document | [themes](examples/themes-light.html) |

Each `SKILL.md` is a lean index — under 200 lines — with the depth in `references/` loading only when relevant.

---

## Layout

```
core/            the shared design system — the single source of truth
  tokens.md        the semantic token contract
  themes/          editorial-coral · executive-navy · field-notes · console-violet · brand-template
  base.css         component→token mapping (contains no color literals)
  print.css        print as a distinct output mode
  a11y.md          SVG labelling, contrast, grayscale, focus
skills/          the six skills, each SKILL.md + references/
commands/        /document-design-system:<slug> for each writing-documents type
scripts/         authoring-time tooling — never shipped to readers
templates/       document · longform (writing-documents shell) · types/<slug> · deck · site · docs-gallery · gallery · themes · diagram
examples/        committed outputs, doubling as CI fixtures and the shots above
assets/          banner.svg — literal colors, because <img> is an isolated document
docs/screenshots/
tests/           standard library only, so CI needs no install step
```

## Themes

Four themes plus a documented brand slot — see [the comparison above](#several-voices-one-contract).

`console-violet` is the dark one. Its accent is violet rather than the obvious amber because amber measured **6° from `--warning`**, and in a system where status colors are load-bearing an accent that close makes every genuine warning ambiguous. Teal was rejected too — 4° from `executive-navy`, so the two would have been hard to tell apart at thumbnail size.

A dark theme must also restore a dark ink ramp for print. `core/print.css` flattens surfaces to white but deliberately leaves the ink ramp alone, so a dark theme that skips this prints white on white. A test fails any dark theme without it.

Because themes select on `[data-theme]` rather than `:root`, and `core/base.css` re-derives its computed tokens at every theme boundary, a single page can carry several themes at once — [`examples/themes-light.html`](examples/themes-light.html) is one document, not four.

A theme changes the visual voice, never the information architecture. It must not change metric definitions, category order, chart scales, included records, or conclusions.

## Tooling

All of it runs on the authoring machine. The delivered artifact is plain HTML and SVG. Node 22.22.2 or newer is required (`.npmrc` sets `engine-strict`, so an older Node fails at install); the validator, tests and document build need only the Python standard library.

```bash
nvm use && npm ci                                           # renderers + PDF export, pinned in package-lock.json
uv venv && uv pip install -r requirements-authoring.txt     # screenshots + brand extraction, pinned
uv run playwright install chromium

python3 scripts/build_examples.py       # reports, decks, figures, all 34 types, gallery index
uv run python3 scripts/shoot_examples.py   # refresh the screenshots above
python3 scripts/build_site.py           # GitHub Pages homepage + types gallery in site/ (gitignored)
python3 scripts/inline_fonts.py rfc.html --font "Geist:400:geist.woff2" --out offline.html
python3 scripts/validate_repository.py .
python3 -m unittest discover -s tests

node scripts/render_diagram.mjs in.mmd --id x --title "…" --desc "…" --out x.svg
node scripts/render_chart.mjs spec.json --out chart.svg
node scripts/export_pdf.mjs report.html --out report.pdf
node scripts/export_pdf.mjs deck.html --out deck.pdf --preset deck   # one slide per page
```

Both renderers wrap their upstream library rather than calling it directly, because raw output is not safe to inline into a designed document. Between them they strip an external Google Fonts request from inside the SVG, namespace generic element IDs that would otherwise collide across two figures on one page, remove fixed pixel dimensions that break print scaling, neutralize a hardcoded white background, and add the accessibility shell. Each is a verified upstream behavior, documented at the point it is handled.

## Verification

`.github/workflows/validate.yml` runs the tests, the repository linter, a template assembly check, and renders a diagram and a chart to assert their output contracts.

`scripts/validate_repository.py` reads the same files the skills read — `core/tokens.md` for the required tokens and `core/themes/*.css` for the palette — so the prose rules and the machine check cannot drift apart. It enforces the two-key frontmatter schema, name↔folder agreement, a mandatory `Do not use for …` clause in every description, complete token coverage in every theme, no color literals outside `core/themes/`, and no broken relative links.

Print is verified by exporting a PDF and looking at it, not by the presence of `@media print`. That check is what caught the report printing its title twice.

## It's working if

- `/document-design-system:handoff` (or any slug in the catalog) writes Markdown at the conventional path and does not load `core/` unless you asked for HTML.
- A routine “write an ADR” loads `writing-documents` plus `type-adr.md` — not the RFC outline, not a theme.
- [`examples/index.html`](examples/index.html) opens offline and every card reaches a real HTML example.
- `python3 scripts/validate_repository.py .` and `python3 -m unittest discover -s tests` pass.

The live site is [avinava.github.io/document-design-system](https://avinava.github.io/document-design-system/) — homepage for all six skills, [types](https://avinava.github.io/document-design-system/types.html) for the thirty-four canonical writing-document cards and compatibility profiles. Pushes to `main` deploy it via [`.github/workflows/pages.yml`](.github/workflows/pages.yml).

## Attribution

- **[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** (MIT, © 2025 Cathryn Lavery) — the editorial standard in `diagram-design` is adapted from it: deletion as the highest-quality move, every node earning its place, one accent for the one or two things that matter, density around 4/10, hairlines over shadows, geometry on a 4px grid, and the position that Mermaid is an input to redraw rather than an output to embed. No code is used; the influence is on judgment, and it is credited in the skill itself.
- **[lukilabs/beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid)** (MIT, Craft Docs) — Mermaid parsing and layout to SVG strings. Its CSS-custom-property theming is what makes the zero-JavaScript retheme possible.
- **[Observable Plot](https://observablehq.com/plot/)** (ISC) — chart scales and layout.
- Anthropic's **skill-creator** conventions — progressive disclosure and description-writing patterns.

Full dependency licensing, with the pinned version of every authoring-time package, is in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Contributing

1. Skills live at `skills/<name>/SKILL.md`, frontmatter limited to `name` and `description`.
2. The description states what it does, when to use it, and an explicit `Do not use for …` — these six skills sit close together and will otherwise compete for the same prompts.
3. Keep `SKILL.md` under 400 lines; depth goes in `references/`, and every reference file must be named from `SKILL.md` or it will never load.
4. Adding a token means adding it to every theme, including `brand-template.css`, and documenting it in `core/tokens.md`.
5. No color literals outside `core/themes/`.
6. `python3 scripts/validate_repository.py .` and `python3 -m unittest discover -s tests` must pass.

## License

MIT — see [LICENSE](LICENSE).
