# Changelog

All notable changes to this project are documented here. Versions refer to the
`version` field in `.claude-plugin/plugin.json`.

## Unreleased

## 0.5.0

Compose, don't enumerate. The writing skill now composes a document from a
pattern's modules when no preset fits, instead of forcing the nearest of its
thirty-four presets. Diagrams gain three forms, a checker and importers; charts
gain a waterfall that checks its totals; the toolchain is pinned; and the
GitHub Pages site follows one engagement in four acts by the reader's job.

### Added

- Composition in `writing-documents`: `references/composing.md` (match a type or
  familiar name, else pick the pattern by the reader's question, then compose
  from that pattern's allowed modules with the nearest type's discipline),
  `type: custom` front matter, the `/document-design-system:compose` command, and
  the promotion rule — a shape composed three times becomes a type.
- A "Start from the reader's question" table in `type-index.md` routing each
  question to its pattern and presets, and more familiar names routed to
  existing types.
- A module registry in `core/document-patterns.md` naming every module class,
  the patterns allowed to use it, and its purpose; CSS for the documented ask
  band and learning goal; and two new modules, the scope strip and the
  crosswalk (fit written as a word, never colour alone).
- A worked composed example, the platform primer (`learning` pattern, nearest
  type `explanation`), in Markdown and designed HTML.
- Three diagram forms with their own layouts — change view, deployment map and
  dependency graph — with worked figures in the design doc, migration plan,
  architecture guide, runbook and delivery plan.
- A waterfall bridge in `render_chart.mjs` that fails the render when a declared
  total is not the sum of its steps; the estimate bridges its work packages to
  24 engineer-weeks with the unapproved change request drawn but not counted.
- `scripts/check_diagrams.py`: eighteen geometry and markup rules read from SVG
  coordinates, each with a stable ID and a failing fixture.
- `scripts/check_render.py`: every example in Chromium at 1280px, 390px and
  print width under every theme, and site pages under light and dark colour
  schemes.
- `scripts/import_diagram.py`: draw.io (plain and compressed) and Mermaid
  flowchart structure as a neutral model with no coordinates, hardened against
  entities, oversized or deeply nested input, duplicate ids and dangling edges.
- A rewritten GitHub Pages site: a homepage that teaches one idea — the
  reader's question picks the pattern, the audience picks the theme, both on
  the same evidence-stated facts — then follows the engagement in four acts by
  the reader's job (understand, decide, deliver, run and hand on), ending on the
  composed primer; figures, a ledger of checks with counts read at build time,
  skills, what's new, and the pinned toolchain;
  a Patterns page that starts from the reader's question; and a Modules page
  with a specimen of every registered module. Shared navigation, per-page meta
  and social preview, and a dark palette that follows the reader's system.
- Pinned authoring toolchain: `package.json` with `package-lock.json` (Node
  22.22.2 or newer, `engine-strict`) and `requirements-authoring.txt`, read by
  `scripts/pins.py`.

### Changed

- The README is rewritten around the core — the question picks the shape, the
  audience picks the voice, both sit on the same facts — then the four acts, figures,
  checks, skills and install. Layout, tooling, verification and contribution rules
  move to `CONTRIBUTING.md`.
- `writing-documents` picks the shape, not only the type: a type when one fits,
  composition otherwise. `core/document-patterns.md` selection rules say the
  same.
- `scripts/catalog.py` is the single source for types, patterns, modules, the
  reader-question table and lifecycle stages; the build, site, validator and
  tests read it instead of keeping copies.
- The validator replaces the `SKILL.md` line warning with a 14,000-byte error,
  checks every type's pattern and default theme, the registry against the
  stylesheet and the bodies, the question table against the families table,
  every version mention against the pins, and the licence table against the
  scripts' imports.
- `build_site.py --check` derives its expectations from the catalog and the
  story: every act has stops, every stop's date read from its own example and
  its pattern and theme from the built page, every module and composed example
  linked, every back link landing on an anchor that exists, every image in
  `docs/screenshots/` shown somewhere, and the release on the site equal to
  `plugin.json`.
- `shoot_examples.py` writes a full-size screenshot only when the README, an
  example or the site shows it, and keeps the committed image when a capture
  differs only by rendering noise, so a full reshoot of unchanged pages leaves
  git clean. Unreferenced full-size images are no longer committed.
- Example pages on the site return to the story stop or pattern they came from.
- Install hints across scripts and skills say `npm ci` and the pinned
  requirements file in the repository, and an exact pinned line for a skill
  installed on its own.

### Fixed

- The diagram skill claimed a draw.io conversion it did not have; it now
  describes the importer that exists.
- `THIRD_PARTY_LICENSES.md`: vl-convert-python is BSD-3-Clause (1.9.x), unused
  D2 and Rough.js rows removed, mermaidx marked as a PyPI package, Playwright
  split into its npm and PyPI packages, Pillow added, and the design-influence
  credit extended.
- The architecture figure and diagram template follow the markup contract; the
  deck's marker ids are prefixed and its `@page` size is valid; a chart's x-axis
  label no longer clips its descenders.
- The output reference no longer describes a stale longform shell, and the
  diagram skill no longer points at a repository file an installed skill does
  not have.
- The site's patterns, lifecycle map and familiar names were hand-written HTML
  that could drift from the catalog; they are now generated.
- The local Patterns page's presentation-design card pointed at a deck
  thumbnail that was never generated.

## 0.4.1

The published site gets navigation and image fixes.

### Fixed

- Published showcase pages (figures, themes, brand, deck, report) had no way back
  to the site; they now carry a "← Home" control, and the site build fails if a
  published page lacks one.
- The brand page's proposal screenshot pointed at a repository path that does
  not exist on Pages and rendered as a broken image. The site build now rewrites
  those paths and fails on any local reference that does not resolve.
- On narrow screens the back control joins the page flow instead of covering the
  first line.

## 0.4.0

Every skill now installs on its own, which makes the repository installable with
`npx skills add` and eligible for the skills.sh listing.

### Changed

- Made every skill self-contained. Each skill now carries the `core/`, `scripts/`
  and `templates/` files it uses, generated from the repository-level originals by
  `scripts/sync_skill_assets.py`, so it works when installed on its own with
  `npx skills add`. Drift is a validation error.
- Skill prose resolves those files relative to the skill's own directory instead
  of `${CLAUDE_PLUGIN_ROOT}`, which is unset outside a plugin install.
- Documented `npx skills add` as an install path.

## 0.3.0

`writing-documents` now covers a practical software-consultancy lifecycle:
thirty-four canonical document types, eleven distinct reading patterns, shared
ownership rules, and one compatibility profile for an earlier specialized
service-documentation command.

### Changed

- Expanded the pattern system with `plan`, `assurance`, and `brief`. Delivery
  plans now lead with milestones and gates; assurance documents separate verdict,
  evidence, findings, and residual risk; short operational briefs foreground
  status, material change, required action, and the next checkpoint.
- Moved `test-report` from the contract family to assurance and made generic
  `service-docs` the canonical suite. The existing specialized suite command is
  retained as a compatibility profile rather than duplicated in the taxonomy.
- Redesigned the homepage and type gallery around the consultancy lifecycle,
  familiar aliases such as HLD, LLD, TDD, PRD, API spec, PRR, and RAID, and
  direct anchors for every canonical type.
- Extended repository guidance, routing, validation, responsive behavior, and
  print rules to keep all eleven patterns aligned with the semantic token
  contract.
- Cleared leftover 0.2 copy: the skills table now names thirty-four types, the
  output contract names eleven patterns, gallery default-theme notes match the
  catalog, and designed HTML uses each type's `default-theme` instead of asking
  or falling back to `field-notes`.

### Added

- Seventeen canonical types spanning mobilisation, commercial definition,
  requirements, planning, migration, testing, security, readiness, risk,
  reporting, release, workshops, incidents, support, and service documentation.
- A consultancy lifecycle reference that defines document ownership, hand-offs,
  source-of-truth boundaries, and safe handling of estimates and commercial or
  legal unknowns.
- Paired Markdown and designed HTML examples for every new type, all grounded in
  the shared example world, plus committed gallery screenshots and lightweight
  thumbnails.
- Validation for the 34-type command/catalog/example/reference matrix, the
  11-pattern gallery, compatibility routing, and characteristic modules for the
  three new layout families.

## 0.2.0

`writing-documents` replaces `longform-document-design`. Eighteen types,
Markdown by default, eight structural reading patterns, a pattern-first gallery,
and a fourteen-slide RFC 014 deck.

### Changed

- Replaced the single longform layout with eight structural document patterns:
  decision, record, contract, procedure, learning, system, incident, and suite.
  Pattern and theme are independent root attributes.
- Rewrote all eighteen Markdown and HTML examples against one explicit fact
  ledger, with parity checks to keep the two formats aligned.
- Redesigned the homepage and type catalog around reader movement rather than a
  uniform card grid. GitHub Pages now rebuilds examples from source before
  assembling and validating the deployable site.
- Increased tertiary-text contrast across the light themes and moved the
  field-notes accent from rust to plum so every shipped theme is distinguishable
  at thumbnail scale. The full theme audit now reports no warnings.
- **`longform-document-design` is now `writing-documents`.** Markdown in the user's repo is the default. Designed HTML/PDF only when asked. Slash commands: `/document-design-system:<slug>`.
- Existing RFC/ADR/spec/postmortem/proposal/runbook shapes live as `references/type-<slug>.md`.
- Plugin and marketplace descriptions name eighteen prose types, not "long-form specs". Writing is Markdown by default.

### Added

- `core/document-patterns.md` and `core/document-patterns.css`, including
  responsive and print behavior for pattern-specific modules.
- Lightweight gallery thumbnails, lazy image loading, Pages back-navigation,
  favicon metadata, and mobile overflow handling.
- Repository agent guidance and a pattern-first skill routing table, keeping
  future document changes aligned with the eight-family contract.
- Types: `api-contract`, `architecture`, `handoff`, `design-handoff`, `discovery`, `test-report`, `onboarding`, `tutorial`, `how-to`, `reference`, `explanation`, `mulesoft`.
- Shared `evidence.md`, `writing.md`, `output.md`, `suites.md`, `type-index.md`.
- Gallery: `examples/<slug>.html` + `.md` for every type, rebuilt from `templates/types/`. Shared fiction in `examples/WORLD.md`. Screenshots in `docs/screenshots/<slug>.png`.
- Document-type gallery page at `examples/index.html`. GitHub Pages workflow deploys `site/` from `scripts/build_site.py`.
- Richer 14-slide RFC 014 capacity deck: title, agenda, statement, divider, table, metric, chart, diagram, comparison, cost, closing.
- README skills table links each skill to its `SKILL.md` and a committed example. The type gallery opens with the same six-skill map.
- GitHub Pages site at https://avinava.github.io/document-design-system/ — homepage covers all six skills; eighteen types live at `/types.html`.
- `horizon` theme: a client brand from `brand-theme-design`. Same proposal in navy, horizon, and coral. Exhibit at `examples/brand.html`.

## 0.1.2

Marketplace listing metadata, and validation that the packaging invariants stay true.

### Added

- **Discovery metadata on the marketplace entry.** A marketplace browser reads the entry in
  `marketplace.json`, not `plugin.json`, so the entry has to carry its own copy. It declared
  neither `license` nor `repository` nor `tags` — the plugin is MIT, and said so in
  `plugin.json` and `LICENSE`, but not anywhere a browser would look. All three are now
  declared, and a check keeps the duplicated fields from drifting apart.
- **Manifest validation in `validate_repository.py`.** The manifests were checked only by
  `claude plugin validate` in CI, which needs node and a network fetch. The local validator
  now checks them too, and encodes two invariants the JSON schema cannot express: the
  marketplace must be named for the repository, and every field duplicated between the two
  manifests must agree. A reintroduced `"skills"` key is rejected outright.
- **Tests that the validator rejects.** Seven cases assert the new checks actually fire — a
  check that never fires is indistinguishable from no check at all. The suite goes from 28
  tests to 35.

### Note on `displayName`

Not added, despite appearing in some plugin manifests. It is in neither the marketplace nor
the plugin-manifest schema, and both schemas leave `additionalProperties` unset, so it
validates but is ignored — `plugin list` shows the plugin's `name`. A field that looks
load-bearing but does nothing is worse than an absent one.

## 0.1.1

Packaging corrections and documentation. Nothing about the skills, themes, or token
contract changed, and the install identifier is unchanged — existing installs need no
action.

### Fixed

- **Dead `$schema` URL.** `marketplace.json` pointed at
  `https://anthropic.com/claude-code/marketplace.schema.json`, which returns 404, so
  editors and CI had nothing to validate against. Both manifests now point at the live
  SchemaStore definitions (`claude-code-marketplace.json` and
  `claude-code-plugin-manifest.json`); `plugin.json` previously declared no `$schema` at
  all.
- **CI validated neither manifest, and one invocation would not have been enough.**
  `claude plugin validate <dir> --strict` validates *only* the marketplace manifest when
  both manifests are present — it prints `Validating marketplace manifest: …` and stops.
  The plugin manifest needs its own invocation against `.claude-plugin/plugin.json`. CI
  now runs both.
- **Redundant `skills` declaration.** `plugin.json` declared `"skills": "./skills/"`.
  `skills/` is scanned by default, so this was at best noise. It is worse than noise for a
  marketplace entry whose `source` resolves to the marketplace root, where an explicit
  skills declaration can *replace* the default scan rather than extend it — a line that
  looks cosmetic but can drop skills. Removed, and all six skills still load.
- **Author consistency.** `owner` in `marketplace.json` and `author` in both manifests now
  carry the same name and URL.

### Added

- Portability notes in `analytical-document-design`, `longform-document-design`, and
  `presentation-design`. Each of them names a script by a repo-root-relative path
  (`scripts/export_pdf.mjs` and friends) without saying how that path resolves for someone
  who installed the plugin, where the working directory is the user's own project and
  `scripts/` does not exist there. They now document the `${CLAUDE_PLUGIN_ROOT}` prefix,
  matching the three skills that already did.
- A note in the README explaining why `document-design-system@document-design-system`
  repeats itself, and tests covering the packaging invariants that were previously
  unasserted.
- This changelog.

### On the marketplace name

The install line is `document-design-system@document-design-system`, where `@` reads as
"from" — it names a plugin and the catalog it came from. Both halves are the same word
because this repository publishes its own catalog and that catalog contains this one
plugin.

That repetition is deliberate rather than an oversight, and it is worth writing down so it
does not get "tidied up" later. Marketplace names are **global per user**, not scoped to
the repository that published them. Adding a marketplace under a name already in use
silently *replaces* the one already there, and the plugins installed from the displaced
catalog are orphaned — they stop loading and can no longer be resolved. Naming each
catalog after the repository that publishes it makes the name unique by construction, so
that collision cannot happen. A shared name across repositories — a publisher or org name,
say — would reintroduce exactly this failure the moment a second repository used it.

Worth knowing, since it is the thing that makes the naming a real choice rather than a
constraint: a marketplace name does **not** have to match the repository path typed into
`/plugin marketplace add`. Anthropic's own catalogs differ from theirs — the
`anthropics/claude-plugins-community` repo publishes a marketplace named
`claude-community`, and `anthropics/claude-code` publishes one named
`claude-code-plugins`. The repository path is how a catalog is *fetched*; the name is how
it is *referred to* afterwards. Matching them here is a decision, not a requirement.

### Why 0.1.1

Every change is a packaging fix or added documentation. No skill behavior, no token
contract change, no change to how the plugin is installed — so the patch position moves.

## 0.1.0

Initial release: six skills — analytical reports, diagrams, charts, decks, long-form
documents, and brand theming — over one semantic token contract, with four shipped themes
and a brand template.
