# Output

Format is a dial. Writing quality does not depend on it.

## The rule

`format = markdown`, unless the user asked for `html`, `pdf`, `print`, `designed`, `themed`, or "use the design system".

Casual edits to an existing file keep that file's format. Do not create a parallel HTML.

## What to load

| Format | Load | Do not load |
|---|---|---|
| `markdown` | `SKILL.md`, `type-<slug>.md`, `writing.md`, `evidence.md` | `core/`, themes, `templates/longform.html`, `print.css`, `build_document.py`, `brand-theme-design` |
| `html` / `pdf` | the above plus this file and `core/` | — |
| `both` | Markdown first, then HTML from that source | letting the two drift |

Markdown stays canonical in a git repo. HTML is a generated, shareable rendering.

## Conventional paths

If the user did not name a path, use the type file's `path:` value. Stay in an existing file when they are already editing one.

On Markdown: ATX headings (`#`, `##`), fenced code with a language, repo-relative links. Mermaid stays a fenced `mermaid` block.

On HTML: prerender Mermaid through `diagram-design` / `scripts/render_diagram.mjs` to SVG whose colours are `var(--…)`. Do not rewrite the Markdown source to strip fences.

## HTML assembly

`templates/longform.html` is the shell — measure, status banner, TOC, optional non-goals box, changelog. Type files own section order. Do not force the RFC outline onto every type.

Theme on the root:

```html
<html lang="en" data-theme="field-notes">
```

`field-notes` is the writing-documents default. `console-violet` for incident and ops voices. `executive-navy` for proposals to leadership. `editorial-coral` when the document sits next to an analytical report. Contract- and table-heavy types (`spec`, `api-contract`, `test-report`, `reference`) set `data-layout="contract"` for a slightly wider shell.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/build_document.py" \
  "${CLAUDE_PLUGIN_ROOT}/templates/longform.html" \
  --theme field-notes --out document.html
node "${CLAUDE_PLUGIN_ROOT}/scripts/export_pdf.mjs" document.html --out document.pdf
```

Inside this repo, drop the `${CLAUDE_PLUGIN_ROOT}/` prefix.

## HTML layout

- Measure 62–72 characters. `core/base.css` sets `max-width: 68ch` on paragraphs.
- Line height 1.55–1.65. One column.
- Headings four levels deep at most.
- Generous space above headings, tight below.
- Code in `var(--mono)` at 0.875em on `var(--surface-muted)`, language labelled.
- Tables and figures numbered and captioned.
- No JavaScript required to read the file.

Print: `core/print.css` last. Body 10–11pt. Headings do not strand. Code must not clip. Read `skills/analytical-document-design/references/print-production.md` before claiming a document prints. Inspect the PDF.

Diagrams from `diagram-design`; charts from `chart-design`. A design doc usually needs one or two diagrams and no charts.
