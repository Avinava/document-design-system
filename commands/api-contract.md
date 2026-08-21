---
description: Write a human-readable API contract companion as Markdown in the user's repository. Use when invoked as /document-design-system:api-contract. Produce designed HTML or PDF only when asked.
---

Use the `writing-documents` skill.
Type slug: api-contract
Load `references/type-api-contract.md`, `references/writing.md`, `references/evidence.md`.
Default output is Markdown in the user's project at this type's conventional path.
Do not assemble HTML, pick a theme, inline CSS, or run build_document.py unless
the user asked for HTML, PDF, print, or designed output.
If they did, also load `references/output.md` and `core/`.
