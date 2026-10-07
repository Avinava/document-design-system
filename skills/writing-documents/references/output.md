# Output

Format is a dial. Writing quality does not depend on it.

## The rule

`format = markdown`, unless the user asked for `html`, `pdf`, `print`, `designed`, `themed`, or "use the design system".

Casual edits to an existing file keep that file's format. Do not create a parallel HTML.

## What to load

| Format | Load | Do not load |
|---|---|---|
| `markdown` | `SKILL.md`, `type-<slug>.md` (or `composing.md` plus the nearest type's file), `writing.md`, `evidence.md` | `core/`, themes, `templates/longform.html`, `print.css`, `build_document.py`, `brand-theme-design` |
| `html` / `pdf` | the above plus this file and `core/` | — |
| `both` | Markdown first, then HTML from that source | letting the two drift |

Markdown stays canonical in a git repo. HTML is a generated, shareable rendering.

## Conventional paths

If the user did not name a path, use the type file's `path:` value; a composed document uses the nearest type's path unless a sibling folder fits better (`docs/primers/`). Stay in an existing file when they are already editing one.

On Markdown: ATX headings (`#`, `##`), fenced code with a language, repo-relative links. Mermaid stays a fenced `mermaid` block.

On HTML: prerender Mermaid through `diagram-design` / `scripts/render_diagram.mjs` to SVG whose colours are `var(--…)`. Do not rewrite the Markdown source to strip fences.

## HTML assembly

`templates/longform.html` is the shell: the root `data-theme` and `data-pattern`, the inlined theme, `core/base.css`, `core/document-patterns.css`, and `core/print.css` last. It carries no content of its own. The body — an `<article class="doc">` — owns section order and every module, from the type file's shape or the composition's declared modules. Do not force the RFC outline onto every type.

Pattern and theme on the root:

```html
<html lang="en" data-theme="field-notes" data-pattern="decision">
```

The type reference declares its default `pattern` and `default-theme`. Pattern
controls reading structure; theme controls visual voice. The eleven-pattern
contract is in `core/document-patterns.md`. A proposal can change from
`executive-navy` to a client theme without ceasing to be a `decision` document.
Pass `--theme` from that type's `default-theme` unless the user or a client
brand named a different one.

A composed document assembles the same way. Its front matter supplies the
pattern (`pattern:`) and the theme comes from `nearest-type`'s
`default-theme`. Build the body from the modules listed in `modules:` — each
must be allowed for the pattern in the module registry in
`core/document-patterns.md` — and set `data-pattern` on the root from the front
matter, not from the nearest type.

```bash
python3 "<skill-dir>/scripts/build_document.py" \
  "<skill-dir>/templates/longform.html" \
  --theme field-notes --out document.html
node "<skill-dir>/scripts/export_pdf.mjs" document.html --out document.pdf
```

`<skill-dir>` is the folder that contains this skill's `SKILL.md`.

## HTML layout

- Measure prose at 62–72 characters. `core/base.css` caps paragraphs; pattern
  modules may use the wider document shell.
- Line height 1.55–1.65. Preserve semantic reading order when multi-column
  comparisons, maps, or registers collapse on small screens.
- Headings four levels deep at most.
- Generous space above headings, tight below.
- Code in `var(--mono)` at 0.875em on `var(--surface-muted)`, language labelled.
- Tables and figures numbered and captioned.
- No JavaScript required to read the file.

Print: `core/print.css` last. Body 10–11pt. Headings do not strand. Code must not clip. Read `references/print-production.md` from the `analytical-document-design` skill before claiming a document prints. Inspect the PDF.

Diagrams from `diagram-design`; charts from `chart-design`. A design doc usually needs one or two diagrams and no charts.

Web previews and GitHub Pages may link to the selected fonts. For offline,
email, archival, or PDF delivery, embed or package them explicitly and verify
the rendered output. Do not describe a linked-font HTML file as offline-safe.
