# Reference

```yaml
slug: reference
title: Reference
aliases: [api-reference]
example: examples/reference.html
command: /document-design-system:reference
default-format: markdown
path: docs/reference/
```

**Reader's question:** what is the exact fact, without a story around it?

Shape after [Diátaxis reference](https://diataxis.fr/reference/). Neutral, complete, structured like the thing it describes.

## When to use

Lookups: flags, fields, error codes, CLI verbs, configuration keys. The user is at work and already competent.

When not: the human API companion that explains conventions and mismatches — prefer `api-contract` when a machine spec exists. When not: a tutorial or how-to.

## Shape

- Architecture mirrors the product (a method lives under its class under its module).
- Accurate, complete, free of interpretation.
- No "getting started". No opinions.
- Examples only as illustrations of the fact, not as a path to follow.

## Failure modes

Narrative. Incomplete tables. Mixing how-to steps into a field listing.

## Output

Markdown in `docs/reference/`. HTML with `data-layout="contract"` when asked. Theme `console-violet`.
