# Contributing

How the repository is laid out, how to build it, how to add to it, and the rules every
change keeps. Agent-facing guidance is in [AGENTS.md](AGENTS.md); how the parts fit
together is in [docs/DESIGN.md](docs/DESIGN.md).

## Layout

```
core/            the shared design system, the single source of truth
  tokens.md        the semantic token contract: colour, type, geometry, voice (type scale, density, ornament)
  themes/          editorial-coral, executive-navy, field-notes, serif-editorial, condensed-report, console-violet, horizon, brand-template
  base.css         component to token mapping (contains no color literals)
  document-patterns.{md,css}  the eleven patterns, their openings, the full-width option and the module registry
  print.css        print as a distinct output mode
  a11y.md          SVG labelling, contrast, grayscale, focus
skills/          the six skills, each SKILL.md + references/ (generated core/, scripts/, templates/ copies)
commands/        /document-design-system:<slug> for each preset, plus compose and the mulesoft profile
scripts/         authoring-time tooling, never shipped to readers
templates/       document, longform, types/<slug>, composed/<slug>, deck, site pages, docs-gallery, modules, gallery, themes, diagram
examples/        committed outputs, doubling as CI fixtures and the README's screenshots
  diagrams/        one specimen per newer diagram form
  specs/           sources for the rendered diagram and charts
docs/            design overview and decisions
  DESIGN.md        how the axes, tokens, openings and catalog fit together
  adr/             architecture decision records, adr-NNN.md
  screenshots/     only images the README, an example or the site shows (thumbs/ holds one per type)
assets/          banner.svg, mark.svg, wordmark.svg: literal colors, because <img> is an isolated document
tests/           standard library only, so CI needs no install step for them
```

## Tooling

All of it runs on the authoring machine. Node 22.22.2 or newer is required (`.npmrc` sets
`engine-strict`, so an older Node fails at install); the validator, tests and document
build need only the Python standard library.

```bash
nvm use && npm ci                                           # renderers + PDF export, pinned in package-lock.json
uv venv && uv pip install -r requirements-authoring.txt     # screenshots, render check, brand extraction, pinned
uv run playwright install chromium

python3 scripts/build_examples.py          # reports, decks, figures, every preset and composed example, Patterns page
python3 scripts/sync_skill_assets.py       # refresh each skill's generated copies of core/, scripts/, templates/
python3 scripts/build_site.py              # GitHub Pages site in site/ (gitignored)
uv run python3 scripts/shoot_examples.py   # refresh referenced screenshots; noise-only captures keep the committed image
python3 scripts/build_document.py templates/longform.html --theme field-notes --width full --out wide.html   # --width full: whole viewport
python3 scripts/inline_fonts.py rfc.html --font "Geist:400:geist.woff2" --out offline.html

node scripts/render_diagram.mjs in.mmd --id x --title "..." --desc "..." --out x.svg
node scripts/render_chart.mjs spec.json --out chart.svg
python3 scripts/import_diagram.py old.drawio      # draw.io, Mermaid, Excalidraw or PlantUML, as structure JSON
python3 scripts/diagram_doctor.py                 # is Node, the pinned renderers and Chromium ready
node scripts/export_diagram.mjs fig.svg --theme executive-navy --format png   # bake one theme into a standalone SVG or PNG
node scripts/export_pdf.mjs report.html --out report.pdf
node scripts/export_pdf.mjs deck.html --out deck.pdf --preset deck   # one slide per page

python3 scripts/extract_site_theme.py https://example.com   # brand: computed styles, not pixels
python3 scripts/audit_theme.py core/themes/horizon.css      # brand: every contrast pair, exact thresholds
```

Both renderers wrap their upstream library rather than calling it directly, because raw
output is not safe to inline into a designed document. Between them they strip an external
font request from inside the SVG, namespace generic element IDs that would otherwise collide
across two figures on one page, remove fixed pixel dimensions that break print scaling,
neutralize a hardcoded white background, and add the accessibility shell.

## Verification

Regenerate in this order, then run the check list.

```bash
python3 scripts/build_examples.py
python3 scripts/sync_skill_assets.py
python3 scripts/build_site.py
uv run python3 scripts/shoot_examples.py   # site shots need build_site.py first
```

```bash
python3 scripts/sync_skill_assets.py --check
python3 -m unittest discover -s tests
python3 scripts/validate_repository.py .
python3 scripts/check_diagrams.py
uv run python3 scripts/check_render.py
python3 scripts/audit_theme.py --all --quiet
python3 scripts/build_site.py --check
```

A second `build_examples.py` run must leave `examples/` unchanged.

### Checked, not eyeballed

Each claim in the README is a check that fails the build.

| Check | Fails when |
|---|---|
| `validate_repository.py` | a type, pattern, module, opening or theme disagrees with the catalog; a body does not use its own pattern's opening; a type body uses no module of its own; a colour literal appears outside `core/themes/`; a version disagrees with the pins; a licence row disagrees with the imports |
| `check_diagrams.py` | any of 21 geometry and markup rules breaks: overlap, out-of-bounds, text that does not fit its box, a figure over its node budget, text below 4.5:1 in any theme, a hidden edge label, off-grid boxes, a second accent |
| `check_render.py` | at 1280px, 390px or print (and 1920px for full-width pages), under any theme, a page scrolls sideways, a figure collapses, or SVG text leaves its box |
| `audit_theme.py` | a required token is missing, a text pair misses its contrast threshold, an accent sits too close to a status colour, or two themes share a voice |
| `build_site.py --check` | a story stop, pattern, module or screenshot is missing or unlinked, a navigation link is dead, or a page has no way back |
| `unittest` | Markdown and HTML disagree on a title or fact, a type's default theme dominates the catalog, or a bad fixture passes |

Print is checked by exporting the PDF and looking at it, not by the presence of
`@media print`.

`.github/workflows/validate.yml` runs all of these, renders a diagram, a chart and a
waterfall to assert their output contracts (a waterfall whose total does not add up must
fail), rebuilds every example and fails if the committed output is stale, and
render-checks the built site pages in light and dark. Pushes to `main` deploy the site
via [`.github/workflows/pages.yml`](.github/workflows/pages.yml).

## Adding to the system

The catalog is derived from a few source files by `scripts/catalog.py`, so each addition
has one place to edit. Rebuild, regenerate and run the check list after any of them.

**A type.** Types grow only by promotion: a shape composed three times. Write
`skills/writing-documents/references/type-<slug>.md` with its `yaml` block (slug, aliases,
`pattern`, `default-theme`), list it in the families table in `core/document-patterns.md`
and in `type-index.md`, add `commands/<slug>.md`, `templates/types/<slug>.html` (it must
use its pattern's opening and one module no other type uses) and `examples/<slug>.md`,
and add its gallery copy to `TYPE_QUESTIONS` in `scripts/build_examples.py`. Choose a
default theme that keeps the catalog spread.

**A module.** Add a row to the Modules table in `core/document-patterns.md` (class, allowed
patterns, purpose), the CSS class to `core/document-patterns.css` using tokens only, and use
it in a body. The Modules page picks up its specimen.

**A theme.** Copy `core/themes/brand-template.css` (or use the `brand-theme-design` skill),
fill every token including the voice tokens, give it a distinct voice, add a `FONTS` entry
in `scripts/build_examples.py` and a panel in `templates/themes.html`, document it in
`core/tokens.md`, and run `audit_theme.py --all`.

**A diagram form.** Add one only when its layout is new: a `## ` section in
`skills/diagram-design/references/diagram-families.md`, a specimen at
`examples/diagrams/<form>.svg` that passes `check_diagrams.py`, and a row in the form table
of the skill. A variant of an existing form is folded into it, and decorative forms are
declined ([ADR-005](docs/adr/adr-005.md)).

**A decision record.** Write `docs/adr/adr-NNN.md` (next number) with Context, Decision and
Consequences. Link it from `docs/DESIGN.md` when it shapes the structure.

## Rules

1. Skills live at `skills/<name>/SKILL.md`, frontmatter limited to `name` and `description`.
2. The description states what it does, when to use it, and an explicit `Do not use for ...`; these six skills sit close together and will otherwise compete for the same prompts.
3. Keep `SKILL.md` within 14,000 bytes and its description within 1,024 characters (the validator fails either); depth goes in `references/`, and every reference file must be named from `SKILL.md` or it will never load.
4. A type is edited in its `type-<slug>.md` YAML block only; `scripts/catalog.py` derives everything else.
5. Adding a token means adding it to every theme, including `brand-template.css`, and documenting it in `core/tokens.md`.
6. No color literals outside `core/themes/`. A dark theme restores a dark ink ramp for print.
7. Edit the repository-level `core/`, `scripts/` and `templates/`, then run `sync_skill_assets.py`; never edit a skill's generated copy or `site/`.
8. Do not name the outside diagram project that influenced `diagram-design` anywhere but `THIRD_PARTY_LICENSES.md`, the skill's credits and the "Built on" sections.
9. The checks under [Verification](#verification) must pass.
