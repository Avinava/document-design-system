# Design handoff

```yaml
slug: design-handoff
title: Design-to-engineering handoff
aliases: [figma-handoff, dev-handoff]
example: examples/design-handoff.html
command: /document-design-system:design-handoff
default-format: markdown
path: docs/design-handoff.md
```

**Reader's question:** what exactly should I build, in every state, and how do I know I am done?

Shape after [Figma's handbook for developer handoff](https://www.figma.com/blog/the-designers-handbook-for-developer-handoff/) and engineer-facing checklists.

## When to use

A product or visual design is ready for implementation. The document is the packet, not a replacement for Figma.

When not: transferring operational ownership of a running system — that is `handoff`. When not: arguing the product should exist — that is `discovery` or `proposal`.

## Sections

| Section | Content |
|---|---|
| Overview | User problem, in-scope flow |
| User flow | Steps, not screenshots of every frame |
| Screens | Happy, empty, loading, error, success — named |
| Components | Design-system component + props; call out custom |
| Interaction | Motion, validation, focus order, keyboard |
| Responsive | Breakpoints that change layout, not "it scales" |
| Content | Copy, truncation, empty strings, error text |
| Data | Fields, empty/null, permissions that hide UI |
| Accessibility | Contrast exceptions, names, reduced motion |
| Acceptance criteria | Given/when/then, one per state |

## Failure modes

Happy-path only. "See Figma." No empty or error states. Tokens described as hex instead of names.

Link the design file. Do not screenshot the whole file into HTML.

## Output

Markdown at `docs/design-handoff.md`. HTML when sharing outside git. Theme `editorial-coral`.
