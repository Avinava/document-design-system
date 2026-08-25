# Risk register

```yaml
slug: risk-register
title: Risk and RAID register
aliases: [raid-log, risk-log, issue-log, dependency-log]
example: examples/risk-register.html
command: /document-design-system:risk-register
pattern: assurance
default-theme: executive-navy
default-format: markdown
path: docs/risk-register.md
```

**Reader's question:** where is delivery exposed, what changed, and who owns the response?

Define the rating method, then keep stable IDs for risks, assumptions, issues,
and dependencies. Each row needs statement, impact, likelihood where relevant,
exposure, treatment, owner, due/review date, status, and movement since review.

Use Markdown/HTML for a compact register. Route high-volume or frequently
updated registers to a spreadsheet or tracker and let this page summarize and
link to that source. Never use color without a written rating.

## Output

Markdown at `docs/risk-register.md`; pattern `assurance`, theme
`executive-navy`.
