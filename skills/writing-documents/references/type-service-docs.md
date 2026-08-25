# Service documentation suite

```yaml
slug: service-docs
title: Service documentation suite
aliases: [application-docs, service-handbook, application-handbook]
example: examples/service-docs.html
command: /document-design-system:service-docs
pattern: suite
default-theme: field-notes
default-format: markdown
path: docs/
```

**Reader's question:** what does this service do, and where is each fact owned?

## When to use

Use for a navigable documentation set around one application or service. It is
an adaptive suite, not one exhaustive file.

When not: a single known reader question. Route directly to its owning type.

## Minimum shape

1. `README.md` or index: boundary, two-minute orientation, document map.
2. `architecture.md`: current system and dependencies.
3. Contract/reference pages supported by machine definitions or code.
4. Onboarding, runbooks, support model, test reports, and handoff only when
   evidence and the service lifecycle justify them.

One fact has one owner. Other pages link instead of copying it. Every page has
an owner and review state; missing evidence becomes an open question, not a
stub.

## Output

Markdown set under `docs/`. Designed HTML is the suite index only unless the
user asks for designed copies of child documents.
