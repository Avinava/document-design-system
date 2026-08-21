# Architecture

```yaml
slug: architecture
title: Architecture guide
aliases: [architecture-guide, c4]
example: examples/architecture.html
command: /document-design-system:architecture
default-format: markdown
path: docs/architecture.md
```

**Reader's question:** how is this system arranged *today*, and where can I change it?

Living current-state guide. Distinct from `design-doc`, which is a decision to change. Shape after [C4](https://c4model.com/) and the mule-docs architecture blueprint.

## When to use

Onboarding to a running system, or keeping a map next to the code. Update it when the system changes.

When not: proposing a change — that is `design-doc`. When not: one decision — that is `adr`.

## Sections

| Section | Content |
|---|---|
| Boundary | What this application owns |
| System context | What calls it and what it calls (C4 context) |
| Containers | Independently deployable parts (C4 container) |
| Primary runtime path | How one representative request or event moves end to end |
| Data | Where schemas and transforms apply |
| Failures | What continues, propagates, retries, writes back, or notifies |
| Trust boundaries | Auth and external systems, without exposing values |
| Extension points | How a new route, mapping, or event is added |
| Known gaps | What could not be verified |

Figures: context + container from `diagram-design`. Code-level C4 is usually a code tour, not a diagram.

Cite repository-relative source paths near detailed claims.

## Failure modes

A design-doc in disguise (proposed future as if it were current). Filename inventory with no responsibilities. Invented topology.

## Output

Markdown at `docs/architecture.md`. HTML when asked. Theme `field-notes`.
