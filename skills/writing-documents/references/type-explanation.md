# Explanation

```yaml
slug: explanation
title: Explanation
aliases: [concept, why]
example: examples/explanation.html
command: /document-design-system:explanation
default-format: markdown
path: docs/explanation/
```

**Reader's question:** why is it like this, in the bigger picture?

Shape after [Diátaxis explanation](https://diataxis.fr/explanation/). Context and connections. Opinion is allowed.

## When to use

Study, not work. The reader wants to understand, not to perform a step.

When not: a procedure — that is `how-to` or `tutorial`. When not: a lookup — that is `reference`. When not: a decision record — that is `adr`.

## Shape

- Circle the subject. Approach from more than one direction if needed.
- Answer *why*.
- Link to the tutorial, how-to, or reference that the explanation is *not*.
- Keep it out of those other types; they link here.

## Failure modes

A tutorial stuffed with theory. A design-doc arguing for a change. Reference material rewritten as a blog post.

## Output

Markdown in `docs/explanation/`. Theme `field-notes` if HTML is asked for.
