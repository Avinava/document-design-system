---
name: longform-document-design
description: Design prose-first technical documents — RFCs, design docs, architecture decision records, specifications, postmortems, runbooks, and technical proposals — as self-contained HTML with clear structure, cross-references, footnotes, and clean print output. Use when writing or restructuring a design doc, RFC, ADR, spec, postmortem, or proposal; when a long technical document is hard to navigate or review; or when prose needs a consistent hierarchy, citation, and print treatment. Do not use for metric-led or data-driven reports (use analytical-document-design), for slides (use presentation-design), for standalone charts or diagrams, or for end-user product documentation and tutorials.
---

# Long-form Document Design

A long-form technical document exists to get a reader to a decision, or to a working understanding, without them having to reconstruct the author's thinking.

The failure mode is not ugliness. It is a document that is complete, accurate, and unreadable — where the reader cannot find the decision, cannot tell what is settled versus proposed, and cannot see what changed since they last read it.

## Structure carries the argument

Pick the type first. Each has a shape readers already know, and matching it means the reader spends their attention on the content rather than on the document.

| Type | Shape |
|---|---|
| **Design doc / RFC** | Context → Problem → Goals and non-goals → Proposal → Alternatives → Risks → Open questions |
| **ADR** | Status → Context → Decision → Consequences. One decision per record, immutable once accepted |
| **Spec** | Scope → Definitions → Normative requirements → Examples → Compliance |
| **Postmortem** | Summary → Impact → Timeline → Root cause → Contributing factors → Action items. Blameless |
| **Proposal** | The ask → Rationale → Cost → Alternatives → Decision needed |
| **Runbook** | Preconditions → Steps → Verification → Rollback → Escalation |

Full section-by-section guidance is in `references/document-types.md`.

## Non-goals are the highest-value section

The section most often omitted and most often needed. Explicitly stating what a document is *not* proposing prevents the review from sprawling into adjacent problems, and it is where reviewers with a different mental model discover the mismatch early rather than after the work is done.

Similarly:

- **Alternatives considered** — with why each was rejected. An alternatives section listing only strawmen tells the reader the decision was made before the document was written, and they will treat the whole document accordingly.
- **Open questions** — with an owner and a date. A document with no open questions is either finished or not being honest.

## Say what is settled

A reader must be able to tell, per section, whether they are reading a decision, a proposal, or a sketch. Mark it explicitly rather than leaving it to tone:

```html
<p class="status-banner">
  <strong>Status:</strong> Proposed ·
  <strong>Decision needed by:</strong> 2026-09-01 ·
  <strong>Owner:</strong> Platform
</p>
```

Status values worth distinguishing: `Draft`, `Proposed`, `Accepted`, `Superseded by <link>`, `Deprecated`. A `Superseded` document keeps its content and gains a pointer — deleting it destroys the record of why the decision was made.

## Prose

The design system cannot rescue unclear writing, and clear writing survives bad formatting.

- **Lead each section with its conclusion.** A reader who stops after the first sentence should still get the point.
- **One idea per paragraph.** A paragraph that needs a "furthermore" is two paragraphs.
- **Prefer prose to bullets for reasoning.** Bullets are good for enumerable things — options, steps, requirements. They are bad for argument, because they let the author omit the connective logic and hide that it is missing.
- **Define terms on first use**, and then use the same term throughout. Synonyms make a reader wonder whether a distinction is intended.
- **Put the numbers in the sentence.** "Latency roughly tripled (140ms → 410ms at p99)" is checkable; "latency degraded significantly" is not.
- **Name the actors.** "It was decided" hides who decided and whether they can revisit it.

## Navigation

Long documents are read non-linearly, and re-read. Build for that.

- **Table of contents** for anything over about 1,500 words, with anchor links.
- **Stable heading IDs**, derived from the heading text, so external links do not rot. Never auto-number IDs — inserting a section renumbers every link to it.
- **Cross-references by name, not position.** "See Rollout" survives an edit; "see section 4.2" does not.
- **Section summaries** for sections over roughly 800 words.
- **A change log** at the top for documents that circulate through review. Reviewers returning to a document need to see what moved.

## Layout

The token contract in `core/tokens.md` applies. Long-form-specific:

- **Measure: 62–72 characters.** This is the single highest-impact typographic decision in a prose document. Full-width text on a wide monitor is genuinely hard to read, because the eye loses the line on the return sweep.
- **Line height 1.55–1.65** for body copy.
- **One column.** Multi-column prose requires a fixed page height, which HTML does not have.
- **Headings four levels deep at most.** A fifth level means the structure needs rethinking.
- **Generous space above headings, tight below** — a heading belongs to what follows it, and the spacing should say so.
- **Code blocks in `var(--mono)`** at 0.875em, in a `var(--surface-muted)` frame, with the language labelled.
- **Tables and figures numbered and captioned**, so cross-references have something to point at.

## Footnotes and citations

Footnotes for asides that would break the sentence but are worth keeping. Citations for claims a reader may want to verify.

- Numbered, superscript, linked both ways — reference to note, note back to reference.
- Collect them at the end of the document, not per section.
- In print, they must remain reachable: `core/print.css` appends URLs to external links, which serves the same purpose on paper.
- If a footnote is essential to the argument, it is not a footnote. Put it in the text.

## Output

One self-contained HTML file: embedded CSS, no JavaScript required, inline SVG for any diagrams, responsive, printable. `templates/document.html` is the starting skeleton.

Diagrams come from `diagram-design`; charts from `chart-design`. A design doc usually needs one or two diagrams and no charts — if it needs many charts, the analysis probably belongs in a separate report.

Also generate when useful: a Markdown version for repository storage and diffing, since design docs and ADRs are usually version-controlled alongside code.

## Print

`core/print.css` handles the baseline. Long-form specifics:

- Body copy 10–11pt; anything smaller is unpleasant across many pages.
- Headings do not strand at page bottoms.
- Code blocks should not split mid-block where avoidable, and must not clip horizontally — long lines wrap or the block scrolls in a print-safe way.
- Table of contents links become useless on paper; either drop the TOC in print or convert it to a plain outline.
- Read `skills/analytical-document-design/references/print-production.md` for the full print contract; it applies here in full.

## Before delivering

- [ ] The document type's expected sections are present, or their absence is deliberate.
- [ ] Goals **and non-goals** are both stated.
- [ ] Alternatives are real, with real reasons for rejection.
- [ ] Status is explicit, with an owner and a date.
- [ ] Open questions have owners.
- [ ] Every section leads with its conclusion.
- [ ] Terms are defined on first use and used consistently.
- [ ] Measure is 62–72 characters.
- [ ] Heading IDs are stable and text-derived.
- [ ] Cross-references are by name, not number.
- [ ] Claims carry numbers where numbers exist.
- [ ] Prints cleanly, with no stranded headings or clipped code.

## Reference files

- `references/document-types.md` — section-by-section guidance per document type.
- `references/prose-and-structure.md` — heading hierarchy, cross-references, change logs, review mechanics.

## Paths in this skill

`core/…` and `scripts/…` are relative to the repo root. When this is installed as a
plugin your working directory is your own project, not the plugin, so prefix them:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/export_pdf.mjs" document.html --out document.pdf
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin's own
directory. Working inside the repo itself, the bare paths are correct as written.
