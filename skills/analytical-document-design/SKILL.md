---
name: analytical-document-design
description: Design evidence-led analytical documents from structured data — executive reports, portfolio reviews, operational audits, inventory analyses, compliance summaries, metric dashboards, and standalone self-contained HTML reports. Use when turning a CSV, inventory, export, or metric set into a professional document; when asked to show where usage, cost, or risk is concentrated; when a report needs clear metric semantics, reconciled totals, accessible charts, and clean print/PDF output; or when an existing dashboard needs to be made defensible rather than merely decorated. Do not use for a single standalone chart (use chart-design), a slide deck (use presentation-design), a prose-first document such as an RFC or spec (use longform-document-design), an application UI, or a transactional product dashboard.
---

# Analytical Document Design

Create documents that help a reader understand what happened, where it is concentrated, why it matters, and what deserves review.

This skill is about the document, not the system that supplies its data. It applies to engineering portfolios, financial reviews, operational audits, inventory analyses, compliance summaries, and product metrics.

## The core standard

A strong analytical document has three layers:

1. **Decision layer** — the headline, current state, material risks, notable opportunities.
2. **Explanation layer** — concentration, time, ownership, composition, comparisons.
3. **Evidence layer** — detailed tables, source records, methodology, caveats.

Do not make every fact equally prominent. The document should be understandable in 30 seconds and defensible after 30 minutes. That tension is the whole design problem — a document that only satisfies the first is a poster, and one that only satisfies the second is a data dump.

## Workflow

### 1. Establish the evidence model

Before designing anything, pin down what the numbers actually mean: the unit being measured, the population included and excluded, which values are counts versus estimates, which fields are facts versus inferred classifications, what the dates mean, and whether the dataset is a snapshot or a series.

Write these distinctions into the report. Never depend on the reader guessing them.

Read `references/evidence-semantics.md` for the full set of distinctions and the traps in each.

### 2. Reconcile totals

Calculate the control totals before deriving any chart. Included groups must sum to the reported total, excluded populations must appear separately, every percentage needs a named denominator, and rounded labels must not conceal material discrepancies.

Stop and investigate unexplained differences. Styling inconsistent data into apparent authority is the single most damaging thing this skill can do.

### 3. Derive views that answer distinct questions

Each view should answer something the others do not: current-state ledger, functional concentration, ownership concentration, creation cohorts, recent activity, staleness, version posture, largest units, review candidates.

Do not add a chart merely because a field exists. `references/evidence-semantics.md` has the full view table with the question each one answers.

### 4. Separate facts from interpretations

Use explicit language:

- **Fact:** "42 records total 1.8 million units."
- **Interpretation:** "This concentration may increase dependency risk."
- **Recommendation:** "Review ownership and replacement options."

Avoid converting weak signals into conclusions. A large file is not automatically poor quality. An old version is not automatically broken. A test-like name does not prove a record is disposable.

### 5. Build the document

Use `templates/document.html` as the starting skeleton and the theme system in `core/`. Section order below.

## Document architecture

Default order. Remove sections that add no information rather than padding them.

1. **Identity bar** — organization/report name, snapshot status.
2. **Title block** — direct title, one-sentence purpose, source and as-of date.
3. **Section navigation** — short anchors, for long HTML reports.
4. **Primary ledger** — one dominant measurement against its context or limit.
5. **Decision metrics** — two or three varied-width cards for risk, exclusion, footprint.
6. **Concentration** — the primary categorical comparison.
7. **Time** — year cohorts and recent monthly detail.
8. **Version posture** — modernization or compatibility exposure.
9. **Ownership** — attribution, with an explicit proxy caveat.
10. **Priority review** — a transparent candidate rule and its impact.
11. **Largest units** — compact evidence table.
12. **Methodology** — definitions, limitations, provenance.
13. **Supporting files** — detailed CSV and concise Markdown when useful.

The title should describe the reader's question, not the implementation. Prefer "Where the work lives" over "Metrics Dashboard v2".

## Visual system

The design system itself lives in `core/`. Read `core/tokens.md` for the token contract and `core/a11y.md` for the accessibility rules — both apply here in full.

The principles specific to analytical documents:

- The highest-quality move is often deletion. Target visual density around 4/10.
- One accent color carries the primary signal. Repeated accent use destroys hierarchy.
- Hierarchy comes from borders and spacing, not shadows.
- No decorative gradients, glowing effects, or generic rounded-card grids.
- Radius between 0 and 8px; a 4px spacing grid where practical.
- No more than eight categories visible in one chart. Combine or split the remainder, and keep every row in the supporting data.

Set the theme once on the root element and let components consume semantic variables only:

```html
<html lang="en" data-theme="editorial-coral">
```

Use `editorial-coral` for general analytical reports, `executive-navy` for board and finance contexts, `field-notes` for research and audit work. Ask one short question only when brand fit materially changes the deliverable.

For chart construction rules — bar sorting, cohort columns, limit ledgers, table design — read `references/visual-system.md`.

## Output

Prefer one self-contained HTML document: embedded CSS, no JavaScript required, inline SVG for charts, responsive to mobile widths, printable with clean page breaks. No external charting library unless interactivity is an explicit requirement.

Also generate when useful:

- `README.md` for portable narrative findings.
- A record-level CSV carrying every classification and metric.
- Separate supporting CSVs for distinct populations.

## Print and PDF

Treat print as a distinct output mode, not the screen page with navigation hidden. A report that will be reviewed, archived, emailed, or presented to leadership must produce a deliberate PDF.

`core/print.css` is the baseline. Adapt it to the document's real class names — do not paste selectors that do not exist.

Do not declare print support based only on the presence of `@media print`. Read `references/print-production.md` before claiming a report prints correctly; it documents the failure patterns that repeatedly survive a casual check, and their remedies.

## Metric writing

Complete, precise labels:

- `Created in trailing 12 months`
- `No recorded modification in 5+ years`
- `Current footprint by creation year`
- `Share of included total`

Ambiguous labels to avoid:

- `Added this year` when only creation dates exist.
- `Owner` when the field is last modifier.
- `Legacy` without a defined threshold.
- `Savings` when the amount is only a review candidate.

Every threshold should be explainable, and editable in one place in the generator.

## Generating from code

When a generator produces the document, keep raw inventory, classification, aggregation, and rendering as separate stages; derive every displayed total from the same normalized records; make classification rules ordered and easy to edit; escape all external text before inserting it into HTML or SVG; sort deterministically so reports are stable across runs; and fail clearly when required fields or control totals are missing.

For recurring reports, make the generator reusable rather than hand-editing generated HTML. See `references/implementation.md`.

## Anti-patterns

Reject these:

- A wall of identical KPI cards.
- A rainbow palette assigning arbitrary colors to categories.
- A chart for every field.
- Tiny labels placed inside bars.
- Truncated axes that exaggerate differences.
- Mono typography used for body copy.
- "AI dashboard" styling: dark canvas, cyan glow, pills, gradients, shadows.
- Calling deployment accounts authors without qualification.
- Calling current size by creation date historical growth.
- Hiding excluded populations to make the headline cleaner.
- Presenting a naming heuristic as a deletion recommendation.

## Before delivering

Run the full checklist in `references/quality-gate.md` — evidence, narrative, design, theme, print, accessibility, delivery.

The three that catch the most real defects:

- [ ] Displayed totals reconcile to the detailed records.
- [ ] Snapshot cohorts are not described as historical growth.
- [ ] The exported PDF was actually inspected, or the lack of inspection is disclosed.

## Completion response

State concisely: the primary output path, supporting data paths, the control total or reconciliation result, the most material findings, and any limitation that changes interpretation.

Do not describe every CSS decision. The document should demonstrate the design system itself.

## Reference files

- `references/evidence-semantics.md` — evidence model, control totals, analytical views, time and change semantics, classification confidence.
- `references/visual-system.md` — typography roles, chart construction, table design.
- `references/print-production.md` — the print contract, page setup, fragmentation strategy, validated failure patterns and remedies, print verification.
- `references/implementation.md` — generator architecture and stage separation.
- `references/quality-gate.md` — the full pre-delivery checklist.

## Paths in this skill

`core/…` and `scripts/…` are relative to the repo root. When this is installed as a
plugin your working directory is your own project, not the plugin, so prefix them:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/render_chart.mjs" spec.json --out chart.svg
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin's own
directory. Working inside the repo itself, the bare paths are correct as written.
