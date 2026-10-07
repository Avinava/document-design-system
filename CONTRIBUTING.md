# Contributing

How the repository is laid out, how to build it, and the rules every change keeps.
Agent-facing guidance is in [AGENTS.md](AGENTS.md).

## Layout

```
core/            the shared design system — the single source of truth
  tokens.md        the semantic token contract
  themes/          editorial-coral · executive-navy · field-notes · console-violet · horizon · brand-template
  base.css         component→token mapping (contains no color literals)
  document-patterns.{md,css}  the eleven patterns and the module registry
  print.css        print as a distinct output mode
  a11y.md          SVG labelling, contrast, grayscale, focus
skills/          the six skills, each SKILL.md + references/
commands/        /document-design-system:<slug> for each preset, plus compose
scripts/         authoring-time tooling — never shipped to readers
templates/       document · longform · types/<slug> · composed/<slug> · deck · site · docs-gallery · modules · gallery · themes · diagram
examples/        committed outputs, doubling as CI fixtures and the README's screenshots
assets/          banner.svg — literal colors, because <img> is an isolated document
docs/screenshots/  only images the README, an example or the site shows
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
python3 scripts/inline_fonts.py rfc.html --font "Geist:400:geist.woff2" --out offline.html

node scripts/render_diagram.mjs in.mmd --id x --title "…" --desc "…" --out x.svg
node scripts/render_chart.mjs spec.json --out chart.svg
python3 scripts/import_diagram.py old.drawio      # draw.io or Mermaid flowchart → structure as JSON
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

```bash
python3 scripts/sync_skill_assets.py --check
python3 -m unittest discover -s tests
python3 scripts/validate_repository.py .
python3 scripts/check_diagrams.py
uv run python3 scripts/check_render.py
python3 scripts/audit_theme.py --all --quiet
python3 scripts/build_site.py --check
```

`.github/workflows/validate.yml` runs all of these, renders a diagram, a chart and a
waterfall to assert their output contracts (a waterfall whose total does not add up must
fail), rebuilds every example and fails if the committed output is stale, and
render-checks the built site pages in light and dark. Pushes to `main` deploy the site
via [`.github/workflows/pages.yml`](.github/workflows/pages.yml).

## Rules

1. Skills live at `skills/<name>/SKILL.md`, frontmatter limited to `name` and `description`.
2. The description states what it does, when to use it, and an explicit `Do not use for …` — these six skills sit close together and will otherwise compete for the same prompts.
3. Keep `SKILL.md` within 14,000 bytes and its description within 1,024 characters (the validator fails either); depth goes in `references/`, and every reference file must be named from `SKILL.md` or it will never load.
4. A type is edited in its `type-<slug>.md` YAML block only; `scripts/catalog.py` derives everything else. A new type comes from promotion: a composed shape seen three times.
5. Adding a token means adding it to every theme, including `brand-template.css`, and documenting it in `core/tokens.md`.
6. No color literals outside `core/themes/`. A dark theme restores a dark ink ramp for print.
7. Edit the repository-level `core/`, `scripts/` and `templates/`, then run `sync_skill_assets.py`; never edit a skill's generated copy.
8. The checks under [Verification](#verification) must pass.
