# How the design system works

This page explains the moving parts and where each one is defined. It restates
no rule that another file owns; it points at the file. Decisions behind the
structure are recorded in [docs/adr/](adr/adr-001.md).

## Two independent axes

Every document declares both on the root element:

```html
<html lang="en" data-theme="field-notes" data-pattern="decision">
```

| Axis | Attribute | Controls | Defined in |
|---|---|---|---|
| Pattern | `data-pattern` | Reading structure: where the answer sits, which modules repeat | [core/document-patterns.md](../core/document-patterns.md), [core/document-patterns.css](../core/document-patterns.css) |
| Theme | `data-theme` | Visual voice, through semantic tokens | [core/tokens.md](../core/tokens.md), `core/themes/*.css` |

Changing the theme must not change the information architecture. Changing the
pattern must not invent facts or alter the evidence state. There are eleven
patterns (`decision`, `record`, `contract`, `procedure`, `learning`, `system`,
`incident`, `suite`, `plan`, `assurance`, `brief`) and six theme files in
`core/themes/`, one of which, `brand-template`, is a slot to fill rather than a
finished theme. The `proposal-horizon` and `proposal-coral` examples render one
body under two themes to prove the axes are independent.

A pattern constrains reading movement; it is not a page template. Prose stays at
62 to 72 characters while maps, tables, timelines and registers may use the
wider shell.

## The token contract

Components name roles, never colours. `core/base.css` and
`core/document-patterns.css` map components to tokens, and a theme file only
supplies values. [core/tokens.md](../core/tokens.md) is the contract. The
required groups are:

- Surfaces: `--paper`, `--surface`, `--surface-muted`
- Ink: `--ink`, `--muted`, `--soft`
- Structure: `--rule`, `--rule-strong`
- Accent: `--accent`, `--accent-tint`, `--accent-ink`
- Status: `--positive`, `--warning`, `--critical`
- Methodology: `--method-bg`, `--method-ink`, `--method-muted`
- Typography: `--display`, `--sans`, `--mono`
- Geometry: `--radius-sm`, `--radius-md`

`scripts/audit_theme.py` reads the required set from the tables in
`tokens.md` (any section whose heading says "optional" is skipped), so the
document and the check cannot drift. Derived tokens (`--comparison-fill`,
`--track-fill`) are declared on `:root, [data-theme]` so a nested scoped theme
re-derives them instead of inheriting the root's values.

The validator rejects a theme missing a required token and rejects colour
literals outside `core/themes/`. Dark themes must restore their ink ramp in a
`@media print` block.

Today the contract covers colour, three font stacks and two radii. Heading sizes
and the hero are fixed in CSS (`core/base.css` sets `h1` to 2rem, `h2` to
1.375rem and `h3` to 1.0625rem; `.doc-hero h1` uses a `clamp()` in
`core/document-patterns.css`). [ADR-002](adr/adr-002.md) records the decision to
move type scale, density and ornament into the contract.

## The opening registry (planned)

Today every body opens with the same `.doc-hero` shell class: a 3px accent rule,
a mono eyebrow, an h1, a lede and a bordered `.doc-meta`. [ADR-003](adr/adr-003.md)
decides that a pattern owns its opening. The plan is an `## Openings` table in
`core/document-patterns.md`, beside the module registry, with one row per
pattern:

| Pattern | Opening |
|---|---|
| `decision` | Split hero with the ask band at the side |
| `record` | Status stamp plus ADR number |
| `contract` | Index masthead |
| `procedure` | Precondition checklist cover |
| `learning` | Outcome-first, with generous measure |
| `system` | Map in the hero |
| `incident` | Full-width severity band with impact numbers |
| `suite` | Service index |
| `plan` | Milestone-rail masthead |
| `assurance` | Verdict stamp |
| `brief` | Dated compact masthead, one-screen grid |

`scripts/catalog.py` would parse the table the way it parses the module
registry, and a check would confirm every body uses its own pattern's opening
and that no two openings are the same. Until that lands, this section describes
intent, not behaviour.

## How the catalog is derived

A document type is declared once, in the fenced `yaml` block of
`skills/writing-documents/references/type-<slug>.md`. The block is flat
`key: value` lines with a fixed key set: `slug`, `title`, `aliases`, `example`,
`command`, `pattern`, `default-theme`, `default-format`, `path`.
`scripts/catalog.py` rejects an unknown key, a duplicate key or a missing field.

`catalog.py` reads exactly these sources and nothing else:

| Source | Gives |
|---|---|
| `type-<slug>.md` yaml blocks | Types: slug, aliases, pattern, default theme |
| `core/document-patterns.md`, "The eleven families" table | Patterns, their reader movement, characteristic modules and types |
| `core/document-patterns.md`, "Modules" table | The module registry: class, allowed patterns, purpose |
| `type-index.md`, "Start from the reader's question" table | Reader question to pattern routing |
| `consultancy-lifecycle.md` | Engagement stages and their candidate owner types |

Everything else (the example build, the Pages site, the validator, the tests)
imports from it. `python3 scripts/catalog.py` prints the types grouped by
pattern and reports disagreements, for example a type whose pattern's families
row does not list it, a `default-theme` that is not a file in `core/themes/`, or
a module the stylesheet does not define.

Two things live in `catalog.py` itself: `COMPOSED`, the composed examples
(`{slug: (theme, pattern)}`, bodies in `templates/composed/`), and the shell
class and module-part lists that distinguish a module from the frame around it.
A composed shape seen three times is promoted to a type; that is the only way
the catalog grows.

## Generated files

```text
core/ scripts/ templates/        canonical, edit these
  |
  |  scripts/sync_skill_assets.py   (MANIFEST maps each skill to the files it needs)
  v
skills/<name>/{core,scripts,templates}   generated copies, never edited
```

A skill installed on its own receives only its own directory, so each carries the
subset of shared files it needs. The `--check` flag fails when a copy has drifted.
A skill that starts using another shared file needs it added to `MANIFEST` in
`scripts/sync_skill_assets.py`.

A designed HTML document is built, not written by hand:

1. `templates/types/<slug>.html` (a preset) or `templates/composed/<slug>.html`
   supplies the body.
2. `scripts/build_examples.py` places it in the `templates/longform.html` shell,
   sets `data-pattern` and the font link, and calls `build()` in
   `scripts/build_document.py`.
3. `build()` replaces each `@@INLINE` marker with the file it names, resolving
   `${THEME}` to the chosen theme, and sets `data-theme` to match, so one theme's
   tokens are inlined per document.
4. The result is written to `examples/<slug>.html`. The Markdown form,
   `examples/<slug>.md`, is canonical and carries the same title and facts from
   `examples/WORLD.md`.

`site/` is built by `scripts/build_site.py` and is gitignored; the Pages workflow
rebuilds the examples before assembling it.

## Regenerate order

```bash
python3 scripts/build_examples.py
python3 scripts/sync_skill_assets.py
python3 scripts/build_site.py
uv run python3 scripts/shoot_examples.py   # site shots need build_site.py first
```

Then run the check list in [AGENTS.md](../AGENTS.md) and
[CONTRIBUTING.md](../CONTRIBUTING.md). A second `build_examples.py` run must
leave `examples/` unchanged.
