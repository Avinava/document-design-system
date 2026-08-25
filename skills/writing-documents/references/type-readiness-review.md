# Readiness review

```yaml
slug: readiness-review
title: Production readiness review
aliases: [prr, orr, operational-readiness-review, go-live-review]
example: examples/readiness-review.html
command: /document-design-system:readiness-review
pattern: assurance
default-theme: console-violet
default-format: markdown
path: docs/readiness/
```

**Reader's question:** is this change ready to enter production, and what blocks it?

Lead with go, no-go, or conditional-go. Assess service ownership, capacity,
reliability objectives, observability, security, support, deployment, rollback,
data, testing, incident response, documentation, and unresolved gaps. Link
evidence for every criterion.

Shape after evidence-led production readiness practice described by
[Google SRE](https://sre.google/workbook/engagement-model/). A checked box
without evidence is not readiness. Name waiver owner and expiry.

## Output

Markdown in `docs/readiness/`; pattern `assurance`, theme `console-violet`.
