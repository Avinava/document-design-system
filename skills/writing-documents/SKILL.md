---
name: writing-documents
description: Write structured software-delivery and consultancy documents as Markdown in the repo by default. Use for canonical decision, contract, procedure, learning, system, incident, suite, plan, assurance, and brief types, including design and architecture docs, requirements, delivery plans, reviews, status, release, support, and service documentation, and for composed documents (primers, orientation guides) built from a reading pattern when no type fits. Produce designed HTML or PDF only when asked. Do not use for casual edits, metric-led reports (analytical-document-design), slides (presentation-design), standalone charts or diagrams, legal boilerplate, back-office commercial records, or unprompted restyling.
---

# Writing Documents

A technical document exists to get a reader to a decision, or to a working understanding, without them having to reconstruct the author's thinking.

The failure mode is not ugliness. It is a document that is complete, accurate, and unreadable — where the reader cannot find the decision, cannot tell what is settled versus proposed, and cannot see what changed since they last read it.

This skill is two layers. Do not glue them together.

1. **Writing** (default) — pick the shape (a type, or a composition from a pattern), write from evidence. Output is Markdown in the user's tree.
2. **Design system** (opt-in) — tokens, themes, print, self-contained HTML. Load `core/` only when the user asked for HTML, PDF, print, a designed page, or "use the design system".

## Format first

`format = markdown`, unless the user asked for `html`, `pdf`, `print`, `designed`, `themed`, or "use the design system".

| Format | Load | Do not load |
|---|---|---|
| `markdown` | this file, the type file (or `references/composing.md` plus the nearest type's file), `references/writing.md`, `references/evidence.md` | `core/`, themes, `templates/longform.html`, print.css, `build_document.py` |
| `html` / `pdf` | the above plus `references/output.md` and `core/` | — |
| `both` | Markdown first (canonical in-repo), then HTML from that source | — |

Full dial, conventional paths, and HTML assembly: `references/output.md`.

On the Markdown path, leave Mermaid as fenced blocks. Prerender to themed SVG only on the HTML path.

State the assumption in one line. Do not quiz.

> Writing `docs/adr/adr-014.md` as type `adr` (markdown). Designed HTML on request.

Ask only when the slug is actually ambiguous or the request conflicts with another skill. If they asked for HTML and named no theme, use the type file's `default-theme`. Do not quiz. `field-notes` is only a fallback when the type has not been resolved yet.

Never offer a designed HTML version unprompted.

## Pick the shape

Type first; compose when none fits.

1. **A type fits.** Load `references/type-index.md` if the slug is unclear,
   then load that `references/type-<slug>.md` before writing. The canonical
   catalog has 34 types grouped by reader movement; common labels such as HLD,
   LLD, TDD, PRD, API spec, PRR, and RAID route there as aliases rather than
   duplicate files or commands.
2. **No type fits.** Do not force the nearest preset. Pick the pattern from the
   reader's-question table in `references/type-index.md`, then follow
   `references/composing.md`: modules allowed for that pattern, the nearest
   type's section discipline, and front matter `type: custom` with `pattern`,
   `modules`, and `nearest-type`. A composed shape seen three times becomes a
   type.

If several reader questions apply, split. Two clear documents beat one that mixes a
decision with a 3am checklist. Use `references/consultancy-lifecycle.md` for an
engagement-spanning request and `references/suites.md` for linked sets.

The compatibility command `mulesoft` loads `type-service-docs.md` plus
`references/profile-mulesoft.md`; it is not a second canonical type.

## Evidence before prose

Mark claims the reader might not be able to check:

| State | Treatment |
|---|---|
| Verified | State as fact, cite a repo-relative path |
| Provided | Attribute to the stakeholder; cannot prove runtime |
| Inferred | Label it and list supporting evidence |
| Unresolved | Open questions; do not pick an answer |
| Recommended | Keep separate from current-state |

Full rules, privacy, and the optional business-context checkpoint: `references/evidence.md`.

## Writing

The design system cannot rescue unclear writing, and clear writing survives bad formatting. Depth in `references/writing.md`.

- Lead each section with its conclusion.
- One idea per paragraph.
- Prefer prose to bullets for reasoning. Bullets are for enumerable things.
- Define terms on first use; use the same term throughout.
- Put numbers in the sentence when numbers exist.
- Name the actors. "It was decided" hides who can revisit it.
- Non-goals, real alternatives, and open questions with owners — omit only on purpose.
- Status explicit: `Draft`, `Proposed`, `Accepted`, `Superseded by <link>`, `Deprecated`.
- Headings are claims or questions, not labels. Stable IDs derived from the text, never auto-numbered.
- Cross-references by name, not section number.

## HTML path only

When format is `html` or `pdf`, `references/output.md` applies in full. Short version:

- Assemble from `templates/longform.html`. The type reference — or a composed document's front matter — declares the root `data-pattern`; theme stays independently selectable on `data-theme`.
- Keep prose at 62–72 characters. Let maps, tables, timelines, comparisons, and registers use the wider shell when the pattern calls for them.
- Diagrams from `diagram-design`; charts from `chart-design`.
- Print via `core/print.css`. Inspect the PDF; do not claim print support from `@media print` alone.
- No JavaScript required to read the file.

### Pattern before theme

Pattern answers how the reader moves; theme answers what visual voice they
hear. Do not use theme changes to simulate structural distinction.

| Pattern | Reading movement | Types |
|---|---|---|
| `decision` | ask → options → trade-offs → next move | design-doc, discovery, proposal, project-charter, estimate, change-request |
| `record` | status → settled choice → consequences | adr |
| `contract` | definitions → rules → specimens → compliance | spec, api-contract, reference, requirements, statement-of-work, support-model |
| `procedure` | safety → steps → verification → recovery | handoff, how-to, runbook |
| `learning` | context → practice → checkpoint → takeaway | explanation, onboarding, tutorial |
| `system` | map → boundaries → interfaces → states | architecture, design-handoff |
| `incident` | impact → timeline → cause → owned action | postmortem |
| `suite` | document map → ownership → freshness | service-docs |
| `plan` | baseline → workstreams → dependencies → gates | delivery-plan, migration-plan, test-strategy |
| `assurance` | verdict → evidence → findings → residual risk | test-report, threat-model, readiness-review, risk-register |
| `brief` | current state → material change → action → next update | status-report, release-notes, workshop-summary, incident-update |

Use the type reference's default pattern and theme; a composed document uses
its declared pattern and the nearest type's theme. The full layout, module
registry, and acceptance contract is `core/document-patterns.md`. The invocation below uses
`field-notes` as a concrete example; pass the type's `default-theme` instead.

```bash
python3 "<skill-dir>/scripts/build_document.py" \
  "<skill-dir>/templates/longform.html" \
  --theme field-notes --out document.html
node "<skill-dir>/scripts/export_pdf.mjs" document.html --out document.pdf
```

`core/…`, `scripts/…` and `templates/…` are relative to this skill's directory — the
folder that contains this `SKILL.md` — not to your working directory. The skill carries
its own copy, so it works however it was installed.

## Leave alone

- Casual edits to existing Markdown (typos, one extra paragraph, a changelog bullet).
- Metric-led reports → `analytical-document-design`.
- Slides → `presentation-design`.
- Standalone charts or diagrams.
- Restyling Markdown into HTML, or applying a theme, unless asked.
- MSAs, NDAs, invoices, procurement, HR, or invented legal clauses. A
  statement of work uses only delivery-commercial terms the user supplied.
- Generating Mule XML or running MUnit. Mule markdown refresh when `mule-docs` is installed — prefer that skill.
- Rewriting a README that already has a shape the user did not ask to change.

## Before delivering

- [ ] Format matches the request (markdown unless they asked for designed output).
- [ ] The type's or composition's expected sections are present, or their absence is deliberate.
- [ ] A composed document declares `type: custom`, its pattern, nearest type, and only modules that pattern allows.
- [ ] Inferred claims are labelled; unresolved items are open questions.
- [ ] Every section leads with its conclusion.
- [ ] Terms are defined on first use and used consistently.
- [ ] Heading IDs are stable and text-derived; cross-references are by name.
- [ ] HTML path only: measure 62–72ch, prints without stranded headings or clipped code.

## Reference files

- `references/type-index.md` — reader's question → pattern, slug, aliases, path, shipped types.
- `references/composing.md` — compose from a pattern when no type fits; promotion rule.
- `references/type-design-doc.md`
- `references/type-adr.md`
- `references/type-spec.md`
- `references/type-api-contract.md`
- `references/type-architecture.md`
- `references/type-handoff.md`
- `references/type-design-handoff.md`
- `references/type-discovery.md`
- `references/type-test-report.md`
- `references/type-postmortem.md`
- `references/type-proposal.md`
- `references/type-runbook.md`
- `references/type-onboarding.md`
- `references/type-tutorial.md`
- `references/type-how-to.md`
- `references/type-reference.md`
- `references/type-explanation.md`
- `references/type-project-charter.md`
- `references/type-estimate.md`
- `references/type-change-request.md`
- `references/type-requirements.md`
- `references/type-statement-of-work.md`
- `references/type-support-model.md`
- `references/type-delivery-plan.md`
- `references/type-migration-plan.md`
- `references/type-test-strategy.md`
- `references/type-threat-model.md`
- `references/type-readiness-review.md`
- `references/type-risk-register.md`
- `references/type-status-report.md`
- `references/type-release-notes.md`
- `references/type-workshop-summary.md`
- `references/type-incident-update.md`
- `references/type-service-docs.md`
- `references/profile-mulesoft.md` — compatibility profile for the generic service suite.
- `references/consultancy-lifecycle.md` — minimum linked sets by engagement stage.
- `references/writing.md` — prose, headings, review mechanics.
- `references/evidence.md` — evidence states, privacy.
- `references/suites.md` — when to emit a linked set.
- `references/output.md` — format dial, HTML/PDF assembly.
