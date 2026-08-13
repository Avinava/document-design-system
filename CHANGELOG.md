# Changelog

All notable changes to this project are documented here. Versions refer to the
`version` field in `.claude-plugin/plugin.json`.

## 0.2.0

**Breaking for anyone who already installed the plugin.** The marketplace was renamed, so
the old install identifier no longer resolves. Migration commands are at the bottom of
this entry.

### The marketplace is now `sfdxy`

Both the marketplace and the plugin inside it were called `document-design-system`, which
made the install line read `document-design-system@document-design-system`.

In `plugin@marketplace`, the `@` means "from". The identifier is supposed to name two
different things — which plugin, and which catalog it came from — so repeating the same
word on both sides is a stutter that tells you nothing and hides which half is which. A
marketplace is a catalog, not a product; it takes the name of whoever publishes it. That
is `sfdxy`, the same identity these skills are published under elsewhere (the `@sfdxy` npm
scope).

There is a practical reason on top of the readability one. Marketplace names are global
per user, not scoped to a repository: adding a second marketplace under a name that is
already taken silently *replaces* the first one. A topical name like
`document-design-system` is exactly the kind of name someone else plausibly picks, and the
collision is silent when it happens. A publisher-scoped name is far less likely to be
claimed by anyone but the publisher.

Renaming is safe because the marketplace name deliberately does not have to match the
repository path typed into `/plugin marketplace add`. Anthropic's own marketplaces work
this way: the `anthropics/claude-plugins-community` repo publishes a marketplace named
`claude-community`, and `anthropics/claude-code` publishes one named
`claude-code-plugins`. The repository path is how the catalog is *fetched*; the name is
how it is *referred to* afterwards.

The plugin itself keeps its name. Only the catalog changed.

### Fixed

- **Dead `$schema` URL.** `marketplace.json` pointed at
  `https://anthropic.com/claude-code/marketplace.schema.json`, which returns 404, so
  editors and CI had nothing to validate against. Both manifests now point at the live
  SchemaStore definitions (`claude-code-marketplace.json` and
  `claude-code-plugin-manifest.json`); `plugin.json` previously declared no `$schema` at
  all.
- **CI validated only half the packaging.** `claude plugin validate <dir> --strict`
  validates *only* the marketplace manifest when both manifests are present — it prints
  `Validating marketplace manifest: …` and stops there. The plugin manifest needs its own
  invocation against `.claude-plugin/plugin.json`. CI ran neither; it now runs both.
- **Redundant `skills` declaration.** `plugin.json` declared `"skills": "./skills/"`.
  `skills/` is scanned by default, so this was at best noise. It is worse than noise for a
  marketplace entry whose `source` resolves to the marketplace root, where an explicit
  skills declaration can *replace* the default scan instead of extending it — a line that
  looks cosmetic but can drop skills. Removed, and all six skills still load.
- **Install instructions.** The README's install block used the old identifier.
- **Author consistency.** `owner` in `marketplace.json` and `author` in both manifests now
  carry the same name and URL.

### Added

- Portability notes in `analytical-document-design`, `longform-document-design`, and
  `presentation-design`. Each of them names a script by a repo-root-relative path
  (`scripts/export_pdf.mjs` and friends) without saying how that path resolves for someone
  who installed the plugin, where the working directory is the user's own project and
  `scripts/` does not exist there. They now document the `${CLAUDE_PLUGIN_ROOT}` prefix,
  matching the three skills that already did.
- This changelog.

### Why 0.2.0 and not 1.0.0

Semantic versioning treats `0.x` as unstable, and the minor position is where a `0.x`
release signals a break. The rename is genuinely breaking for existing installs, so the
minor moves. It is not `1.0.0` because that would claim a stability commitment about the
token contract and the skill surface that this change does not earn — nothing about the
design system itself stabilized here.

### Migrating

`/plugin marketplace remove` uninstalls every plugin installed from that marketplace, so
check `/plugin` first if you added the old marketplace for anything else.

```
/plugin marketplace remove document-design-system
/plugin marketplace add Avinava/document-design-system
/plugin install document-design-system@sfdxy
```

## 0.1.0

Initial release: six skills — analytical reports, diagrams, charts, decks, long-form
documents, and brand theming — over one semantic token contract, with four shipped themes
and a brand template.
