---
description: Compose a document from a reading pattern when no canonical type fits, as Markdown in the user's repository. Use when invoked as /document-design-system:compose. Produce designed HTML or PDF only when asked.
---

Use the `writing-documents` skill.
Type slug: custom
Load `references/type-index.md` first; if a type or alias fits, use that type
instead and say so in one line.
Otherwise load `references/composing.md`, the nearest type's
`references/type-<slug>.md`, `references/writing.md`, and
`references/evidence.md`. Pick the pattern by the reader's question, use only
modules that pattern allows, and declare `type: custom`, `pattern`, `modules`,
and `nearest-type` in the front matter.
Default output is Markdown in the user's project at the nearest type's
conventional path.
Do not assemble HTML, pick a theme, inline CSS, or run build_document.py unless
the user asked for HTML, PDF, print, or designed output.
If they did, also load `references/output.md` and `core/`.
