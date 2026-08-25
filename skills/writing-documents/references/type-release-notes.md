# Release notes

```yaml
slug: release-notes
title: Release notes
aliases: [whats-new, release-changelog, deployment-notes]
example: examples/release-notes.html
command: /document-design-system:release-notes
pattern: brief
default-theme: editorial-coral
default-format: markdown
path: docs/releases/
```

**Reader's question:** what changed in this release, who is affected, and what must they do?

State product/version/date and audience. Put breaking changes and required
actions before highlights, fixes, deprecations, known issues, rollout state,
support path, and links to machine changelogs or migrations.

Do not dump commit subjects or claim a fix without release evidence. Distinguish
released, rolling out, and planned work.

## Output

Markdown in `docs/releases/`; pattern `brief`, theme `editorial-coral`.
