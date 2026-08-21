# Design doc

```yaml
slug: design-doc
title: Design doc
aliases: [rfc, tdd, technical-design, erd]
example: examples/design-doc.html
command: /document-design-system:design-doc
default-format: markdown
path: docs/design/
```

**Reader's question:** should we do this, and is the approach sound?

Shape after [Design Docs at Google](https://www.industrialempathy.com/posts/design-docs-at-google/). Company RFC / ERD processes are the same artifact. IETF RFCs are normative specs — use `spec`.

## When to use

The solution is ambiguous — problem complexity, solution complexity, or both. Senior review, organisational consensus, or cross-cutting concerns (security, privacy, observability) would change the outcome.

When not: an implementation manual with no trade-offs. Write the code. When not: a one-decision record — that is `adr`.

## Sections

| Section | Content |
|---|---|
| Summary | Three sentences. What, why, what changes. Written last |
| Context | What a reader needs to hold in mind. Objective background, not a history lesson |
| Problem | What is wrong now, with evidence. Numbers where they exist |
| Goals | What success looks like, ideally measurable |
| Non-goals | Things that could reasonably have been goals and are explicitly not |
| Design | The approach, starting with an overview. Trade-offs are the point |
| Alternatives considered | Real options, with real reasons for rejection |
| Cross-cutting | Security, privacy, observability — how the design addresses each |
| Risks and mitigations | What could go wrong and what happens if it does |
| Rollout | How it ships, how it is verified, how it rolls back |
| Open questions | With owners and dates |

Length: 10–20 pages for a large project; 1–3 page mini-docs are valid for a bounded change.

## Evidence to inspect

Existing ADRs, related design docs, incident history that motivates the problem, the current interface of the thing being changed. A system-context diagram is the default figure (`diagram-design`). Sketch APIs; do not paste IDL. Discuss data storage as trade-offs, not dumped schemas.

## Failure modes

- A proposal section that describes the implementation without stating the design. If a reader cannot restate the approach in a sentence, the section is describing code.
- Strawman alternatives.
- Non-goals omitted, so review sprawls.
- Summary written first, describing the document intended rather than the one produced.

## Output

Markdown in `docs/design/` (or the team's RFC folder). HTML when the user asked for a designed or printable copy. Theme `field-notes`.
