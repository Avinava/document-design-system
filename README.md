<p align="center">
  <img src="assets/banner.svg" alt="document-design-system — documents that get a reader to a decision, as Markdown or self-contained HTML" width="960" />
</p>

<p align="center">
  <a href="LICENSE"><img alt="MIT" src="https://img.shields.io/badge/license-MIT-2d3142"></a>
  <img alt="6 skills" src="https://img.shields.io/badge/skills-6-eb6c36">
  <img alt="34 presets, compose when none fits" src="https://img.shields.io/badge/presets-34%20%2B%20compose-2d3142">
  <img alt="11 reading patterns" src="https://img.shields.io/badge/patterns-11-2d3142">
  <img alt="no runtime dependencies" src="https://img.shields.io/badge/runtime%20deps-none-2d3142">
  <a href="https://github.com/Avinava/document-design-system/actions/workflows/validate.yml"><img alt="validate" src="https://github.com/Avinava/document-design-system/actions/workflows/validate.yml/badge.svg"></a>
</p>

# Documents that get a reader to a decision

Most documents fail by being complete, accurate and unreadable: the reader cannot find
the decision, cannot tell what is settled from what is proposed, and has to rebuild the
author's thinking to act. This repository is six Claude skills that write the document
around its reader instead.

```
/plugin marketplace add Avinava/document-design-system
/plugin install document-design-system@document-design-system
```

Then ask in plain words: *"write the cutover plan for RFC 014"*, *"make a primer for
engineers joining from batch"*, *"turn this inventory export into a report for the platform
review"*. Writing lands as Markdown in your repository. Designed HTML is opt-in, needs no
JavaScript to read, and prints.

**Site:** [avinava.github.io/document-design-system](https://avinava.github.io/document-design-system/) ·
**Install options:** [below](#install)

---

## The core

Name the reader and the question they bring. Three things follow, and they are kept
independent on purpose.

### The question picks the shape

A **pattern** fixes reading order: where the answer sits, what repeats, what the reader
does last. There are eleven. The thirty-four document types are presets inside them.

| The reader asks | Pattern | Reading movement | Presets |
|---|---|---|---|
| Should we do this, and what do you need from me? | `decision` | ask → options → trade-offs → next move | `design-doc` `discovery` `proposal` `project-charter` `estimate` `change-request` |
| Why is it like this, and is that settled? | `record` | status → decision → consequences | `adr` |
| What exactly must be true, and how do I check it? | `contract` | definitions → rules → specimens → compliance | `spec` `api-contract` `reference` `requirements` `statement-of-work` `support-model` |
| What do I do, in what order, and how do I recover? | `procedure` | safety → steps → verification → recovery | `handoff` `how-to` `runbook` |
| How does this work, so I can reason about it myself? | `learning` | context → practice → checkpoint → takeaway | `explanation` `onboarding` `tutorial` |
| How is it arranged, and where are the boundaries? | `system` | map → boundaries → interfaces → states | `architecture` `design-handoff` |
| What happened, and what stops it recurring? | `incident` | impact → timeline → cause → owned action | `postmortem` |
| Where is each fact about this service owned? | `suite` | document map → ownership → freshness | `service-docs` |
| How will the work get done, and what gates it? | `plan` | baseline → workstreams → dependencies → gates | `delivery-plan` `migration-plan` `test-strategy` |
| Is it good enough, on what evidence? | `assurance` | verdict → evidence → findings → residual risk | `test-report` `threat-model` `readiness-review` `risk-register` |
| Where are we now, and what needs my attention? | `brief` | current state → change → action → next update | `status-report` `release-notes` `workshop-summary` `incident-update` |

Familiar names — HLD, LLD, TDD, PRD, API spec, PRR, RAID — route to the preset that owns
them in [`type-index.md`](skills/writing-documents/references/type-index.md). A familiar
filename never becomes a second type.

**When no preset fits, compose.** Pick the pattern by the reader's question, then build
from the [modules](core/document-patterns.md#modules) that pattern allows — 51 are
registered, each one CSS class with one reading job — borrowing the nearest preset's
section discipline. A shape composed three times becomes a preset; that is the only way
the catalog grows. `/document-design-system:compose` runs it directly.

### The audience picks the voice

A **theme** sets type, colour and density through semantic tokens. Identical markup in
every panel; only `data-theme` differs, and no section moves.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/themes-dark.png">
  <img alt="The same content block rendered under editorial-coral, executive-navy, field-notes, console-violet and horizon" src="docs/screenshots/themes-light.png">
</picture>

<sub>Follows your GitHub theme · [source](examples/themes-light.html)</sub>

| Theme | Voice for |
|---|---|
| `editorial-coral` | Analysis for a wider review — the default |
| `executive-navy` | Leadership deciding and funding |
| `field-notes` | Internal working documents, research, audit |
| `console-violet` | Engineers on the incident, the gate and the pager — the dark theme |
| `horizon` | A client's brand, produced by `brand-theme-design` |
| `brand-template` | Your own brand: copy it, fill every TODO, rename it |

One proposal body, three voices:

| | | |
|---|---|---|
| [![Proposal in executive-navy](docs/screenshots/proposal.png)](examples/proposal.html) | [![Proposal in editorial-coral](docs/screenshots/proposal-coral.png)](examples/proposal-coral.html) | [![Proposal in horizon](docs/screenshots/proposal-horizon.png)](examples/proposal-horizon.html) |
| `executive-navy` — board | `editorial-coral` — analytical | `horizon` — the [client brand](examples/brand.html) |

### Both sit on the same facts

Changing the pattern or the theme never changes a fact. Every claim carries an evidence
state, and a missing fact stays open rather than being filled in:

| Claim | State |
|---|---|
| Four of the last six incidents trace to the shared queue | **Verified** — from incident tickets |
| Two independently recoverable queues reduce blast radius | **Recommended** — by RFC 014 |
| Shed and alert rather than block | **Unresolved** — Reliability owns the decision |

The full set is Verified, Provided, Inferred, Unresolved and Recommended
([`evidence.md`](skills/writing-documents/references/evidence.md)). Markdown is the
canonical form; designed HTML is built from the same title and facts, and the build fails
when the two disagree. Commercial documents never invent parties, rates, terms or dates.

---

## One engagement, four acts

Every example comes from one fictional engagement, and every fact from one ledger,
[`examples/WORLD.md`](examples/WORLD.md). Northwind Ingestion runs every producer through
one shared queue, and that queue keeps stopping all of them at once; RFC 014 splits it in
two. The acts follow the readers' jobs, not the calendar.

**1. Understand.** Something broke. What is actually true?

| For | The reader asks | The document |
|---|---|---|
| Platform and Reliability | What happened, why, and what stops it recurring? | [Postmortem](examples/postmortem.html) · `incident` — impact before narrative |
| The platform review | Where does the platform footprint sit, measured? | [Analytical report](examples/inventory-report.html) — 41% is 1.84M of 2.50M units, denominator named |
| Platform, before funding the build | What did we learn, and should we proceed? | [Discovery brief](examples/discovery.html) · `decision` — ends on go, stop or reframe |

**2. Decide.** Should we do this, and what will it take?

| For | The reader asks | The document |
|---|---|---|
| The Platform director, with reviewers | Should we do this, and is the approach sound? | [Design doc](examples/design-doc.html) · `decision` — the ask and its deadline first |
| The Platform director | What will this take, and how confident are we? | [Basis of estimate](examples/estimate.html) · `decision` — a waterfall to 24 engineer-weeks |
| The Platform director, in the room | What are you asking me for, and by when? | [Deck](examples/capacity-deck.html) — the same decision, one claim per slide |

**3. Deliver.** How do we get there without breaking producers?

| For | The reader asks | The document |
|---|---|---|
| Platform, Reliability, producer teams | How will the agreed outcome be delivered and governed? | [Delivery plan](examples/delivery-plan.html) · `plan` — the critical path is the one accent |
| Director, Platform and Reliability | Where are we now, and what needs attention? | [Status report](examples/status-report.html) · `brief` — Amber first, then each reader's action |
| Reliability, which approves the gate | Is this change ready for production? | [Readiness review](examples/readiness-review.html) · `assurance` — the verdict beside its evidence |
| Platform, running the cutover | How do we move safely and back out? | [Migration plan](examples/migration-plan.html) · `plan` — one partition at a time |

**4. Run and hand on.** Who keeps it alive, and how does the next engineer learn it?

| For | The reader asks | The document |
|---|---|---|
| On-call, while the lag alert fires | What do I do right now? | [Runbook](examples/runbook.html) · `procedure` — safety before steps |
| An engineer joining from batch work | Can I reuse what I know from batch loads here? | [Platform primer](examples/platform-primer.html) · `learning`, **composed** — no preset fits |

| | |
|---|---|
| [![Postmortem](docs/screenshots/postmortem.png)](examples/postmortem.html) | [![Analytical report](docs/screenshots/analytical-report.png)](examples/inventory-report.html) |
| Postmortem — impact strip, timeline, owned actions | Analytical report — the denominator named |
| [![Design doc](docs/screenshots/design-doc.png)](examples/design-doc.html) | [![Delivery plan](docs/screenshots/delivery-plan.png)](examples/delivery-plan.html) |
| Design doc — the ask, then a change view | Delivery plan — milestones, dependency graph, gates |
| [![Title slide](docs/screenshots/deck-title.png)](examples/capacity-deck.html) | [![Comparison slide](docs/screenshots/deck-compare.png)](examples/capacity-deck.html) |
| Deck — the title names the argument | Three options on the same criteria; the accent is the recommendation |

[![Platform primer, composed in the learning pattern](docs/screenshots/platform-primer.png)](examples/platform-primer.html)

<sub>The composed primer: a scope strip, a learning goal, a crosswalk that says where the
batch analogy holds, bends and breaks, and a takeaway per section.</sub>

Every preset and pattern, starting from the reader's question, is on the
[Patterns page](https://avinava.github.io/document-design-system/types.html); every module
has a specimen on the [Modules page](https://avinava.github.io/document-design-system/modules.html).

[![The Patterns page](docs/screenshots/patterns-gallery.png)](examples/index.html)

---

## Figures that stay true

Diagrams and charts are SVG whose colours are `var(--…)`, so they follow the page's theme
with nothing re-rendered. Both renderings below are the **same SVG files**:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/gallery-dark.png">
  <img alt="Figure gallery: architecture, change view, deployment map, dependency graph, sequence, ranked bars, columns, line, waterfall bridge and a limit ledger" src="docs/screenshots/gallery-light.png">
</picture>

<sub>Follows your GitHub theme · [source](examples/gallery-light.html)</sub>

| Figure | The reader asks |
|---|---|
| Architecture | How is it arranged? |
| Change view | What changes, and what stays the same? |
| Deployment map | Where does each part run? |
| Dependency graph | What blocks what, and which path sets the date? |
| Sequence | In what order do the calls happen? |
| Ranked bars · columns · line | Which is largest? How did it change by period? What is the trend? |
| Waterfall bridge | How do the parts add up to the total? — the render fails if they don't |
| Limit ledger | How close are we to the limit? |

Mermaid and draw.io files are inputs, not outputs: their structure is imported and the
figure is redrawn on tokens. Open any example and change one attribute —

```html
<html lang="en" data-theme="editorial-coral">   →   data-theme="executive-navy"
```

— and the page, the chart's focal bar and the diagram's arrowheads move together.

---

## Checked, not eyeballed

Each claim above is a check that fails the build.

| Check | Fails when |
|---|---|
| `validate_repository.py` | a type, pattern, module or theme disagrees with the catalog; a colour literal appears outside `core/themes/`; a version disagrees with the pins; a licence row disagrees with the imports |
| `check_diagrams.py` | any of 18 geometry and markup rules breaks: overlap, out-of-bounds, a hidden edge label, off-grid boxes, a second accent |
| `check_render.py` | at 1280px, 390px or print, under any theme, a page scrolls sideways, a figure collapses, or SVG text leaves its box |
| `audit_theme.py` | a text pair misses its contrast threshold, or an accent sits too close to a status colour |
| `build_site.py --check` | a story stop, pattern, module or screenshot is missing or unlinked |
| `unittest` | Markdown and HTML disagree on a title or fact, or a bad fixture passes |

Print is checked by exporting the PDF and looking at it, not by the presence of
`@media print`.

---

## The skills

| Skill | Owns | Does **not** own | Example |
|---|---|---|---|
| **[writing-documents](skills/writing-documents/SKILL.md)** | 34 presets in 11 patterns, composition when none fits, evidence states; Markdown by default | Metric-led reports, casual edits, unrequested restyling | [Patterns page](examples/index.html) |
| **[analytical-document-design](skills/analytical-document-design/SKILL.md)** | Evidence models, control totals, metric and cohort semantics, methodology | Prose-first documents, slides | [Inventory report](examples/inventory-report.html) |
| **[diagram-design](skills/diagram-design/SKILL.md)** | When a diagram earns its place; 15 forms; layout and label rules; Mermaid and draw.io import | Quantitative charts, UI mockups | [Figure gallery](examples/gallery-light.html) |
| **[chart-design](skills/chart-design/SKILL.md)** | Chart choice, axis honesty, token palettes, a waterfall that checks its totals | Narrative, dashboards as applications | [Estimate](examples/estimate.html) |
| **[presentation-design](skills/presentation-design/SKILL.md)** | 16:9 HTML slides, claim titles, one idea per slide, PDF one slide per page | Documents meant to be read; `.pptx` | [Deck](examples/capacity-deck.html) |
| **[brand-theme-design](skills/brand-theme-design/SKILL.md)** | A brand turned into a theme: extraction with provenance, role mapping, contrast audit | Choosing between shipped themes | [Brand exhibit](examples/brand.html) |

---

## Install

As a Claude Code plugin, with the slash commands:

```
/plugin marketplace add Avinava/document-design-system
/plugin install document-design-system@document-design-system
```

The name appears twice because `@` reads "from": the plugin, from the catalog of the same
name. The catalog is named after this repository so it cannot collide with another.

As plain skills, without the plugin system:

```bash
npx skills add Avinava/document-design-system                      # all six
npx skills add Avinava/document-design-system --skill chart-design # just one
```

Each skill carries its own copy of the tokens, scripts and templates it uses, so it works
wherever it lands. Without the CLI, copy any `skills/<name>/` into `.claude/skills/`.

---

## Built on

Readers need nothing installed: a delivered document is HTML and SVG. The authoring
toolchain runs only where the document is written, pinned to exact versions; licences
and versions are in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

- **[beautiful-mermaid](https://github.com/lukilabs/beautiful-mermaid)** (MIT) — Mermaid to SVG; its CSS-custom-property theming makes the zero-JavaScript retheme possible.
- **[Observable Plot](https://observablehq.com/plot/)** (ISC) with **jsdom** (MIT) — chart scales and layout, rendered server-side.
- **Playwright** (Apache-2.0) and **Pillow** (MIT-CMU) — PDF export, screenshots, brand extraction and the render check.
- **Design influence: [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design)** (MIT, © 2025 Cathryn Lavery) — the editorial standard in `diagram-design` is adapted from it: deletion as the highest-quality move, every node earning its place, one accent, density around 4/10, hairlines over shadows, a 4px grid, label geometry verified rather than eyeballed, and diagram files as structure to redraw. No code is used; the credit is also in the skill.
- Anthropic's **skill-creator** conventions — progressive disclosure and description writing.

## Contributing

Repository layout, the authoring toolchain, the full check list and the rules for skills,
types and tokens are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
