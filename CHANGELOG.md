# Changelog

All notable changes to this project are documented here. Versions refer to the
`version` field in `.claude-plugin/plugin.json`.

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
