---
name: writing-documents
description: Write structured technical documents — design-doc, adr, spec, postmortem, proposal, runbook — as Markdown in the repo by default. Use when asked to write or restructure a design doc, RFC, ADR, spec, postmortem, proposal, runbook, or longform technical documentation. Produce designed HTML or PDF only when asked. Do not use for casual edits to existing markdown, metric-led reports (analytical-document-design), slides (presentation-design), standalone charts or diagrams, or restyling a file into HTML unprompted.
---

# Writing Documents

A technical document exists to get a reader to a decision, or to a working understanding, without them having to reconstruct the author's thinking.

The failure mode is not ugliness. It is a document that is complete, accurate, and unreadable — where the reader cannot find the decision, cannot tell what is settled versus proposed, and cannot see what changed since they last read it.

This skill is two layers. Do not glue them together.

1. **Writing** (default) — pick the type, load its shape, write from evidence. Output is Markdown in the user's tree.
2. **Design system** (opt-in) — tokens, themes, print, self-contained HTML. Load `core/` only when the user asked for HTML, PDF, print, a designed page, or "use the design system".

## Format first

`format = markdown`, unless the user asked for `html`, `pdf`, `print`, `designed`, `themed`, or "use the design system".

| Format | Load | Do not load |
|---|---|---|
| `markdown` | this file, the type file, `references/writing.md`, `references/evidence.md` | `core/`, themes, `templates/longform.html`, print.css, `build_document.py` |
| `html` / `pdf` | the above plus `references/output.md` and `core/` | — |
| `both` | Markdown first (canonical in-repo), then HTML from that source | — |

Full dial, conventional paths, and HTML assembly: `references/output.md`.

On the Markdown path, leave Mermaid as fenced blocks. Prerender to themed SVG only on the HTML path.

State the assumption in one line. Do not quiz.

> Writing `docs/adr/adr-014.md` as type `adr` (markdown). Designed HTML on request.

Ask only when the slug is actually ambiguous, the request conflicts with another skill, or they asked for HTML and no theme is set (`field-notes` is the longform default).

Never offer a designed HTML version unprompted.

## Pick the type

Load `references/type-index.md` if the slug is unclear. Then load **one** `references/type-<slug>.md` before writing.

| Slug | Reader's question | Shape |
|---|---|---|
| `design-doc` | Should we do this, and is the approach sound? | Context → Problem → Goals / non-goals → Design → Alternatives → Cross-cutting → Risks → Rollout → Open questions |
| `adr` | Why is it like this? | Status → Context → Decision → Consequences. One decision, immutable once accepted |
| `spec` | What exactly must I build, and how do I know I am done? | Scope → Definitions → Normative requirements → Examples → Compliance |
| `postmortem` | What happened, why, and what stops it recurring? | Summary → Impact → Timeline → Root cause → Contributing factors → Action items. Blameless |
| `proposal` | Should I approve this? | The ask → Rationale → Cost → Alternatives → Decision needed |
| `runbook` | What do I do right now? | Preconditions → Steps → Verification → Rollback → Escalation |

Aliases (`rfc` → `design-doc`, `playbook` → `runbook`) live in `references/type-index.md`. Do not invent a second filename.

If several types apply, split. Two clear documents beat one that mixes a decision with a 3am checklist. A linked set is `references/suites.md`.

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

- Assemble from `templates/longform.html`. Theme on `data-theme` (`field-notes` unless the type file or the user says otherwise).
- Measure 62–72 characters. One column.
- Diagrams from `diagram-design`; charts from `chart-design`.
- Print via `core/print.css`. Inspect the PDF; do not claim print support from `@media print` alone.
- No JavaScript required to read the file.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_document.py" \
  "${CLAUDE_PLUGIN_ROOT}/templates/longform.html" \
  --theme field-notes --out document.html
node "${CLAUDE_PLUGIN_ROOT}/scripts/export_pdf.mjs" document.html --out document.pdf
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin directory. Working inside this repo, the bare `scripts/` and `templates/` paths are correct.

## Leave alone

- Casual edits to existing Markdown (typos, one extra paragraph, a changelog bullet).
- Metric-led reports → `analytical-document-design`.
- Slides → `presentation-design`.
- Standalone charts or diagrams.
- Restyling Markdown into HTML, or applying a theme, unless asked.
- Rewriting a README that already has a shape the user did not ask to change.

## Before delivering

- [ ] Format matches the request (markdown unless they asked for designed output).
- [ ] The type's expected sections are present, or their absence is deliberate.
- [ ] Inferred claims are labelled; unresolved items are open questions.
- [ ] Every section leads with its conclusion.
- [ ] Terms are defined on first use and used consistently.
- [ ] Heading IDs are stable and text-derived; cross-references are by name.
- [ ] HTML path only: measure 62–72ch, prints without stranded headings or clipped code.

## Reference files

- `references/type-index.md` — slug, aliases, path, shipped types.
- `references/type-design-doc.md`
- `references/type-adr.md`
- `references/type-spec.md`
- `references/type-postmortem.md`
- `references/type-proposal.md`
- `references/type-runbook.md`
- `references/writing.md` — prose, headings, review mechanics.
- `references/evidence.md` — evidence states, privacy.
- `references/suites.md` — when to emit a linked set.
- `references/output.md` — format dial, HTML/PDF assembly.
