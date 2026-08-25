# Suites

Prefer a small, navigable set over a single exhaustive dump. One fact lives in one owning document; others link to it.

## When to emit more than one file

- The user asked for "the docs" or "full documentation" with no type.
- Two slugs both apply (a design-doc *and* a runbook).
- A living architecture guide would bury a one-decision ADR.
- Diátaxis types mixing (tutorial material inside reference) — split rather than blend.

Do not create an empty file to satisfy a table. If evidence is missing, keep a short Open questions section in the closest owning document.

## How

1. Pick a README or index as the entry. Two minutes of orientation, then links.
2. Map existing files to roles before adding new ones. Update in place when a document already owns the topic.
3. Preserve topology the user already has (`docs/`, `adr/`, a wiki path).
4. For a targeted request, update only the requested document and directly affected cross-references.

## Anti-patterns

- One 40-page HTML file that is architecture, runbook, and API contract.
- Duplicating the same table in three files so they "stand alone".
- A generated suite of stub pages with TODO headings.
