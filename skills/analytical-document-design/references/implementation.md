# Generator implementation

When a script produces the document rather than hand-authoring it, the structure of the generator determines whether the report stays trustworthy across runs.

## Stage separation

Keep four stages distinct, each with an inspectable output:

1. **Raw inventory** — the source records, unmodified, with their original field names.
2. **Normalization** — types coerced, dates parsed, populations marked included or excluded.
3. **Classification** — ordered rules applied, each record carrying its category and confidence.
4. **Aggregation** — every displayed total derived here, from the normalized records.
5. **Rendering** — HTML/SVG emitted from aggregates only.

Rendering must never reach back into raw records. The moment a template computes its own total, two numbers in the document can disagree and nothing will catch it.

## Requirements

- **Preserve a record-level output.** A CSV carrying every record with its classification, confidence, and metrics is what makes the report auditable. Without it, a reader who disputes a number has no recourse.
- **Derive every displayed total from the same normalized records.** One source, many views.
- **Make classification rules ordered and easy to edit.** A list of rules in priority order, in one place — not conditionals scattered through the aggregation code.
- **Escape all external text** before inserting it into HTML or SVG. Record names, owner names, and source descriptions are untrusted input.
- **Sort deterministically.** Stable ties (sort by value, then by name) mean two runs on the same data produce identical documents, which makes diffs meaningful.
- **Store the generation timestamp and source identifier.** These belong in the methodology block.
- **Fail clearly when required fields or control totals are missing.** A generator that silently emits a report with a missing denominator has produced a confident-looking wrong answer.
- **Store the theme ID as one configuration value** and render it on the root element. Reject unknown theme IDs, or fall back explicitly to `editorial-coral` — never emit a partially themed document.
- **Keep semantic component CSS separate from theme token definitions.** This mirrors the `core/base.css` / `core/themes/` split.

## Thresholds

Every threshold in the document — what counts as stale, what counts as legacy, what makes a review candidate — should be:

- Defined in one place in the generator.
- Named in the document where it is used.
- Explainable in a sentence.

`Legacy` without a defined threshold is not a finding, it is a mood.

## Recurring reports

For reports that regenerate on a schedule, make the generator reusable rather than hand-editing the generated HTML. Hand edits are lost on the next run, and their loss is silent.

Where a report needs a one-off annotation, add it as an input to the generator (a notes file, a config entry) rather than as a post-hoc edit to the output.

## Rendering diagrams and charts

Prerender to SVG strings at generation time. Nothing renders in the reader's browser.

- `scripts/render_chart.mjs` — data plus a spec to a static SVG.
- `scripts/render_diagram.mjs` — Mermaid source to a token-themed inline SVG.
- `scripts/inline_fonts.py` — subset and base64-embed WOFF2 when the document must be genuinely offline.

The output SVGs reference `var(--…)` tokens, so a theme change reaches them without re-rendering.
