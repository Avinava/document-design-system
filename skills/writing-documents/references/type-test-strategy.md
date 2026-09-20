# Test strategy

```yaml
slug: test-strategy
title: Test strategy
aliases: [test-plan, qa-strategy, quality-strategy]
example: examples/test-strategy.html
command: /document-design-system:test-strategy
pattern: plan
default-theme: editorial-coral
default-format: markdown
path: docs/test-strategy.md
```

**Reader's question:** how will quality risks be tested before a release decision?

Define quality risks, in/out scope, test levels, traceability, environments,
data, automation, non-functional testing, defect handling, entry/exit criteria,
roles, schedule, evidence retention, and unresolved constraints.

Do not report results here. A named build's verdict belongs in `test-report`.
Test counts without denominators or an environment identity are not evidence.

## Output

Markdown at `docs/test-strategy.md`; pattern `plan`, theme `editorial-coral`.
