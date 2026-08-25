# Change request

```yaml
slug: change-request
title: Change request
aliases: [scope-change, variation-request, change-control]
example: examples/change-request.html
command: /document-design-system:change-request
pattern: decision
default-theme: executive-navy
default-format: markdown
path: docs/changes/
```

**Reader's question:** should we change the agreed baseline, given the impact?

## Sections

Identity and status; current baseline; requested change and reason; impact on
scope, schedule, effort/cost, quality, risk, and dependencies; options including
decline or defer; recommendation; approver, decision date, and implementation
conditions.

Do not rewrite the project history. Link the charter, estimate, requirements,
and delivery plan that will change after approval. Until approved, the baseline
remains authoritative.

## Output

Markdown in `docs/changes/`; pattern `decision`, theme `executive-navy`.
