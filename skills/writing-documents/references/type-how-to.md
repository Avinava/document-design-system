# How-to

```yaml
slug: how-to
title: How-to guide
aliases: [howto, how-to-guide]
example: examples/how-to.html
command: /document-design-system:how-to
default-format: markdown
path: docs/how-to/
```

**Reader's question:** how do I get this particular job done?

Shape after [Diátaxis how-to guides](https://diataxis.fr/how-to-guides/). A recipe for a competent user at work.

## When to use

A real-world goal: configure X, rotate a key, troubleshoot a deploy. The user already knows the product.

When not: a first lesson — that is `tutorial`. When not: a complete catalogue of options — that is `reference`. Troubleshooting belongs here.

## Shape

- Title is the goal: "How to configure frame profiling".
- Prerequisites assumed, stated briefly.
- Ordered steps. Skip pedagogy.
- Name the expected result of each step.
- Include the failure path when that is why the guide exists.

## Failure modes

Teaching the domain from scratch. Mixing in reference tables. A tutorial's "we will build a simple…" framing.

## Output

Markdown in `docs/how-to/`. Theme `editorial-coral` if HTML is asked for.
