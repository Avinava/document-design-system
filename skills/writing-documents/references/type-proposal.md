# Proposal

```yaml
slug: proposal
title: Proposal
aliases: []
example: examples/proposal.html
command: /document-design-system:proposal
default-format: markdown
path: docs/proposals/
```

**Reader's question:** should I approve this?

## When to use

A decidable ask: time, money, people, or a go/no-go. Shorter than a design-doc; it is not the design.

When not: the design itself — that is `design-doc`. When not: a discovery of whether to proceed at all — that is not this type until `discovery` ships; use a proposal only if they already want a yes/no on a defined ask.

## Sections

| Section | Content |
|---|---|
| The ask | What you want, stated first, in one sentence |
| Rationale | Why it is worth it |
| Cost | Time, money, people, opportunity cost |
| Alternatives | Including doing nothing |
| Decision needed | Who decides, by when, and what happens if they do not |

## Notes

- The ask goes first. A proposal that builds to its request wastes the reader's most attentive minute.
- Include doing nothing as an alternative, with its cost. It is always an option and is often chosen by default.
- State the cost honestly, including the parts that are hard to quantify. A proposal that understates cost damages the next one you write.

## Failure modes

An ask so vague it cannot be approved. "Investment in platform reliability" is not decidable; "two engineers for one quarter to add staging gates to the deploy pipeline" is.

## Output

Markdown in `docs/proposals/`. HTML when the audience will not open git; theme `executive-navy`.
