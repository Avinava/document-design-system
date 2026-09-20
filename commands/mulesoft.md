---
description: Write a MuleSoft service documentation suite as Markdown using the backward-compatible service-docs profile. Produce designed HTML or PDF only when asked.
---

Use the `writing-documents` skill.
Compatibility profile for type slug: service-docs
Load `references/type-service-docs.md`, `references/profile-mulesoft.md`,
`references/writing.md`, and `references/evidence.md`.
Default output is Markdown in the user's project at this type's conventional path.
Do not assemble HTML, pick a theme, inline CSS, or run build_document.py unless
the user asked for HTML, PDF, print, or designed output.
If they did, also load `references/output.md` and `core/`.
