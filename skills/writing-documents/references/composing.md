# Composing from a pattern

Load this file when no type or alias in `type-index.md` fits the reader. The
34 types are presets: each is a pattern plus a tested section order. When none
of them matches, compose a document from the pattern directly instead of
forcing the nearest preset. A primer for engineers arriving from another
discipline is not an onboarding setup checklist with the steps removed.

## Three steps

1. **Match a type or alias first.** Check the canonical catalog and the
   common-names list in `type-index.md`. If one fits, stop here and load that
   type. Composition is the fallback, not a second catalog.
2. **Pick the pattern by the reader's question.** Use the "Start from the
   reader's question" table in `type-index.md`. The pattern fixes the reading
   movement: where the answer sits, what repeats, what the reader does last.
3. **Compose from the pattern's allowed modules, with the nearest type's
   discipline.** Name the nearest type — the preset in that pattern closest to
   the job — and load its `type-<slug>.md` for its failure modes and section
   habits. Choose modules only from those the module registry in
   `core/document-patterns.md` allows for the pattern. On the Markdown path
   the modules become plain structures (a table, a short list, a labelled
   paragraph); on the HTML path they are the registry's classes.

The theme is the nearest type's `default-theme`, unless the user or a client
brand named another. A pattern has no theme of its own.

## Declare it

A composed document says what it is, so a reviewer can check it against the
pattern rather than against a type it never claimed to be. Markdown front
matter:

```yaml
---
type: custom
title: <the document's h1>
pattern: learning
modules: [scope-strip, learning-goal, crosswalk, takeaway]
nearest-type: explanation
---
```

`modules` lists registry classes. Every one must be allowed for `pattern`, and
the HTML rendering uses exactly those modules. State the assumption in one line
as for a type:

> Writing `docs/primers/batch-to-ingestion.md` as a composed `learning`
> document (nearest type `explanation`). Designed HTML on request.

## Section discipline

- Lead with the reader's starting point, not the system's history.
- Each section ends in a conclusion the reader can carry — on the HTML path a
  section takeaway.
- When the reader arrives with another vocabulary, map it explicitly: a
  crosswalk of their term, the term here, how well the old intuition fits
  (holds, partial, breaks), and what to adjust. Write the fit as a word.
- Say what the document is not and which documents to read with it.
- Mark what the evidence does not cover. A composed page has no type checklist
  to hide a gap behind, so name the gap and its owner.

## Rules that do not change

- Evidence states and privacy (`evidence.md`) apply unchanged.
- Delivery-commercial documents never get invented parties, rates, payment
  terms, legal clauses, approvals, or dates — composed or not.
- Composition does not widen scope. MSAs, NDAs, invoices, procurement, HR, and
  legal boilerplate stay out; metric-led reports go to
  `analytical-document-design`; slides go to `presentation-design`.
- If two reader questions apply, write two documents. Composition is not a way
  to merge a decision with a procedure.

## Promotion

A composed shape seen three times becomes a type: a `type-<slug>.md` with its
pattern, default theme, aliases, and failure modes, plus its command and worked
example. That is the only way the catalog grows. Until then, compose.
