---
description: Write a design doc / RFC as Markdown in the user's repository. Use when invoked as /document-design-system:design-doc. Produce designed HTML or PDF only when asked.
---

Use the `writing-documents` skill.
Type slug: design-doc
Load `references/type-design-doc.md`, `references/writing.md`, `references/evidence.md`.
Default output is Markdown in the user's project at this type's conventional path.
Do not assemble HTML, pick a theme, inline CSS, or run build_document.py unless
the user asked for HTML, PDF, print, or designed output.
If they did, also load `references/output.md` and `core/`.
