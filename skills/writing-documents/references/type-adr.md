# Architecture decision record

```yaml
slug: adr
title: Architecture decision record
aliases: [architecture-decision]
example: examples/adr.html
command: /document-design-system:adr
default-format: markdown
path: docs/adr/adr-NNN.md
```

**Reader's question:** why is it like this?

Shape after [Nygard, Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions).

## When to use

One architecturally significant decision: structure, non-functional characteristics, dependencies, interfaces, or construction techniques.

When not: a design with several interacting choices — that is `design-doc`. When not: a living current-state tour of the system.

## Sections

| Section | Content |
|---|---|
| Title | The decision, as a statement: "Use Postgres for the event store" |
| Status | Proposed / Accepted / Superseded by \<link\> / Deprecated |
| Context | The forces at play — technical, organisational, temporal. Value-neutral |
| Decision | What was decided, in the active voice: "We will …" |
| Consequences | What follows, both good and bad |

Numbered sequentially (`adr-NNN.md`). Numbers are not reused. One or two pages.

## Notes

- **One decision per record.** A record with three decisions cannot be superseded cleanly.
- **Immutable once accepted.** To change a decision, write a new ADR that supersedes it. The old record keeps its content and gains a pointer.
- Context includes what was true *at the time*.
- Consequences must include the bad ones. An ADR listing only benefits is marketing.

## Failure modes

ADRs written after the fact to justify a decision already made. They read as reasonable and teach nothing, because the real forces are absent.

## Output

Markdown is primary. HTML optional. Theme `field-notes`.
