# Repository guidance

This repository treats document design as two independent axes:

- **Document pattern** controls reading structure and is declared with
  `data-pattern`.
- **Theme** controls visual voice through semantic tokens and is declared with
  `data-theme`.

Do not reduce the writing examples to one generic longform layout. Select one
of the eleven patterns in `core/document-patterns.md`, then use the modules that
support that reader movement. Keep prose readable at 62–72 characters while
allowing maps, tables, comparisons, timelines, and registers to use the wider
shell.

A third, smaller switch is width: `<html data-width="full">` (build flag
`--width full`) lets the shell use the whole viewport. It is not a pattern or a
theme and nothing may depend on it.

Voice is part of the contract. `core/tokens.md` requires 33 tokens, including
type scale, density and ornament; every theme declares all of them, and
`audit_theme.py --all` fails two themes that share a voice. Each pattern owns
one opening, in the Openings table of `core/document-patterns.md` (hero parts,
not modules); a body uses its own pattern's. Every type body uses one module no
other type uses. Why the structure is this way is in `docs/DESIGN.md` and the
records in `docs/adr/`; a decision that changes it gets a new `adr-NNN.md`.

Markdown in `examples/<slug>.md` is the canonical repository-friendly form.
Designed HTML is generated from `templates/types/<slug>.html` (presets) or
`templates/composed/<slug>.html` (composed examples); both forms must use the
same title and factual anchors from `examples/WORLD.md`.

## Types, composition and promotion

A request that matches a type or one of its familiar names uses that type.
When none fits, compose: pick the pattern by the reader's question
(`skills/writing-documents/references/type-index.md`), use only the modules the
registry in `core/document-patterns.md` allows for that pattern, and borrow the
nearest type's section discipline (`references/composing.md`). Do not force the
nearest preset, and do not add a type for a one-off request. A composed shape
seen three times is promoted to a type; that is the only way the catalog grows.

The catalog is edited in one place. A type's slug, aliases, `pattern` and
`default-theme` live only in its `type-<slug>.md` `yaml` block, and the
families table in `core/document-patterns.md` lists it. `scripts/catalog.py`
derives everything else — the build, the Patterns page, the site, the
validator and the tests — from those files, the module registry, the
reader-question table in `type-index.md` and the stages in
`consultancy-lifecycle.md`. Gallery card copy lives in `TYPE_QUESTIONS` and
`COMPOSED_GALLERY` in `scripts/build_examples.py`; the homepage story lives in
`STORY` in `scripts/build_site.py`, with every date taken from the example it
links to.

When changing a writing-document type or composed example:

1. Edit the type's `yaml` block (or `catalog.COMPOSED`), never a second copy.
2. Update both Markdown and HTML examples.
3. Rebuild and regenerate (see below).
4. Run the full check list.

Canonical consultancy aliases such as HLD, LLD, TDD, PRD, API spec, PRR, and
RAID route through `type-index.md`; do not create duplicate types or commands
for a familiar filename. The `mulesoft` command is a compatibility profile of
canonical `service-docs`, not another type; `compose` is the only command that
is not a type.

For statements of work, estimates, and other delivery-commercial documents,
never invent parties, rates, payment terms, legal clauses, approvals, or dates.
Use the evidence states and leave missing terms unresolved.

## Toolchain

```bash
nvm use && npm ci                                        # Node 22.22.2+, pinned renderers
uv venv && uv pip install -r requirements-authoring.txt  # Playwright + Pillow, pinned
uv run playwright install chromium
```

Versions are read from `package.json` and `requirements-authoring.txt` by
`scripts/pins.py`; the validator fails on any other version mention that
disagrees.

Regenerate in this order:

```bash
python3 scripts/build_examples.py
python3 scripts/sync_skill_assets.py
python3 scripts/build_site.py
uv run python3 scripts/shoot_examples.py   # site shots need build_site.py first
```

Check list — all must pass:

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
`check_render.py` also renders pages that declare `data-width="full"` at 1920px.

Diagram tooling (`scripts/`): `check_diagrams.py` runs 21 rules, including
`text-fit`, `layout-budget` and `contrast` (`--rules` lists them);
`import_diagram.py` reads draw.io, Mermaid, Excalidraw and PlantUML;
`diagram_doctor.py` reports a missing renderer; `export_diagram.mjs` bakes one
theme into a standalone SVG or PNG. A diagram form is added only when its
layout is new (`ADR-005`), with a specimen in `examples/diagrams/`.

## Generated files

`skills/<name>/{core,scripts,templates}` are generated copies, so each skill
works when installed on its own. Edit the repository-level `core/`, `scripts/`,
and `templates/`, then run `python3 scripts/sync_skill_assets.py`; never edit a
copy. A skill that starts using another shared file needs it added to `MANIFEST`
in that script.

GitHub Pages is source-built. Do not hand-edit `site/`; the workflow rebuilds
examples before assembling the deployable site.

Do not add source-provenance, copied product naming, or private reference links
to repository documents, examples, screenshots, commit messages, or release
notes. Express the design principle in this repository's own vocabulary. The
design-influence credit lives only in `THIRD_PARTY_LICENSES.md`, the
`diagram-design` skill's credits, and the "Built on" sections of the README and
the site.
