# Tutorial

```yaml
slug: tutorial
title: Tutorial
aliases: [lesson]
example: examples/tutorial.html
command: /document-design-system:tutorial
default-format: markdown
path: docs/tutorials/
```

**Reader's question:** can I learn this by doing it, safely, once?

Shape after [Diátaxis tutorials](https://diataxis.fr/tutorials/). A tutorial is a lesson. The instructor is responsible for the learner's success.

## When to use

A beginner acquiring skill. One successful path. Practical — the user *does* something.

When not: a competent user with a real-world goal — that is `how-to`. When not: explaining why — that is `explanation`. Do not overload a tutorial with theory.

## Shape

- Learning-oriented, not task-oriented.
- Linear. Each step is attainable and produces a concrete result.
- Minimal explanation inline ("we use HTTPS because it is safer"); link `explanation` for depth.
- No digressions, no "or you could also…".
- End when the learner has basic competence, not when the product is fully described.

## Failure modes

A how-to in disguise (get from A to B). A reference dump. Explanation stuffed into every step. Optional branches that strand a beginner.

## Output

Markdown in `docs/tutorials/`. Theme `editorial-coral` if HTML is asked for.
