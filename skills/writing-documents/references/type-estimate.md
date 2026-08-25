# Estimate

```yaml
slug: estimate
title: Basis of estimate
aliases: [basis-of-estimate, effort-estimate, cost-estimate]
example: examples/estimate.html
command: /document-design-system:estimate
pattern: decision
default-theme: executive-navy
default-format: markdown
path: docs/estimates/
```

**Reader's question:** what will this take, how confident are we, and what moves the number?

Lead with a range, confidence, unit, and as-of date. Then show scope, method,
work breakdown, assumptions, exclusions, dependencies, risks, contingency, and
validity window.

Never present a point estimate as certainty. Separate effort from elapsed time
and cost; derive money only from provided rates. Changes to assumptions require
a new estimate or version.

## Output

Markdown in `docs/estimates/`; pattern `decision`, theme `executive-navy`.
