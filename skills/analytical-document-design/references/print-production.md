# Print and PDF production

Treat print as a distinct output mode, not as the browser page with navigation hidden. A report that will be reviewed, archived, emailed, or presented to leadership must produce a deliberate PDF when printed from a modern browser.

`core/print.css` is the baseline. This file explains what it is doing, what it cannot do, and how to verify the result.

## Contents

- [The print contract](#the-print-contract)
- [Page setup](#page-setup)
- [Print-only identity](#print-only-identity)
- [Typography in print](#typography-in-print)
- [Color and grayscale](#color-and-grayscale)
- [Charts in print](#charts-in-print)
- [Tables in print](#tables-in-print)
- [Fragmentation strategy](#fragmentation-strategy)
- [URLs and interactive elements](#urls-and-interactive-elements)
- [Verification](#verification)
- [Validated failure patterns](#validated-failure-patterns)

## The print contract

The printed report must:

- Preserve the report title, as-of date, source, control total, and methodology.
- Remove interactive navigation and controls that have no paper meaning.
- Keep text at a readable physical size.
- Fit charts within the printable page width without clipping.
- Repeat table headers across pages where supported.
- Avoid splitting a heading from the content it introduces.
- Avoid splitting small metric cards, charts, callouts, and methodology boxes.
- Permit long evidence tables to flow across pages rather than forcing them onto one.
- Preserve meaningful accent colors while remaining understandable in grayscale.
- Expose useful external URLs when the destination matters on paper.
- Avoid blank pages caused by over-aggressive break rules.

## Page setup

Default to portrait A4 unless the content has genuinely wide evidence tables. Use US Letter when the target organization requires it.

```css
@page { size: A4 portrait; margin: 14mm 14mm 16mm; }
```

```css
@page { size: Letter portrait; margin: 0.55in 0.55in 0.65in; }
```

Do not switch the whole document to landscape because one table is wide. Create a landscape appendix, or simplify the visible columns first.

Browser-generated headers and footers are controlled by the print dialog, not reliably by page CSS. Do not claim that CSS alone suppresses browser-added URL and date headers. Tell the user to disable browser headers and footers when a clean PDF is required.

### Load order

Place print rules after the responsive screen media queries, or give print selectors enough specificity to override them.

Print rendering can match a narrow-viewport media query. Without explicit overrides, a desktop grid silently collapses to one column in the PDF — and because the PDF still looks tidy, this survives casual review.

### Shorthand hazards

Be careful with shorthand declarations on structural classes. `.section { padding: 24px 0; }` also removes horizontal padding from `<section class="section methodology">`.

Restore component-owned spacing with a later, more specific selector:

```css
section.methodology { padding: 18px 20px; }
```

Or avoid the conflict by setting only the block-axis properties on the structural class.

## Print-only identity

Navigation disappears in print, but provenance must not. Provide a compact `.print-only` block when the screen header does not print cleanly:

```html
<div class="print-only report-provenance">
  <strong>Report title</strong><br>
  As of 2026-08-12 · Source: normalized inventory export
</div>
```

`.print-only` defaults to `display: none` outside `@media print` in `core/base.css`.

## Typography in print

- Set physical sizes in `pt` where predictable output matters.
- Body copy around 9.5–11pt.
- Evidence tables around 8–9pt. Do not shrink below 7.5pt to force a fit — pick fewer columns instead.
- Line height at least 1.35 for body copy.
- Avoid very light font weights, especially for PDFs that may be printed in grayscale.
- External web fonts fail in offline or restricted environments. Define robust system fallbacks.
- Confirm the browser has finished loading fonts before exporting a PDF.

## Color and grayscale

`print-color-adjust: exact` is a request, not a guarantee. Browser settings can still suppress backgrounds.

Therefore:

- Never rely on background color alone to convey meaning.
- Keep borders, labels, or patterns around focal and comparison elements.
- Ensure charts remain legible in grayscale.
- Avoid large dark background areas that consume ink.
- Invert dark methodology sections to white when ink economy matters, or retain a strong border and heading hierarchy. `core/print.css` inverts them by default.
- Test both with and without "Background graphics" enabled in the print dialog.

## Charts in print

- Prefer inline SVG; it stays sharp at any print scale.
- Give every SVG a stable `viewBox`.
- Avoid CSS `min-width` in print; it clips wide charts.
- Keep SVG text large enough after fitting to page width.
- Place legends within the figure's printable bounds.
- Keep the chart title and its explanatory note with the chart, inside a non-breaking figure wrapper.
- Never split one chart across two pages.
- If a chart is too dense at portrait width, build a separate print variant or a landscape appendix rather than scaling it into illegibility.

## Tables in print

- Allow long tables to span pages.
- Repeat `<thead>` with `display: table-header-group`.
- Do not apply `break-inside: avoid` to a whole table — it creates blank space or overflow.
- Apply non-breaking behavior to individual rows only when rows are short.
- Replace sticky headers and columns with ordinary cells.
- Remove horizontal scroll containers, and reset their `min-width`.
- Select the columns the printed decision actually needs. Move exhaustive fields to CSV rather than printing 20 compressed columns.
- When a table still does not fit at a readable size, hide low-priority columns in print with explicit selectors and keep exact records in the CSV. Never hide the key identifier, primary grouping, measured value, or review-driving field.

For a deliberately wide appendix:

```css
@page wide { size: A4 landscape; margin: 12mm; }
.wide-appendix { page: wide; break-before: page; }
```

Named pages and orientation changes have inconsistent browser support. When the appendix is critical, a separate landscape HTML/PDF deliverable is more reliable.

## Fragmentation strategy

Use break controls selectively:

- Avoid breaking metric cards, small figures, and short callouts.
- Let large sections and long tables break naturally.
- Keep a section heading with at least its first paragraph or chart.
- Use explicit page breaks before major appendices, not before every section.
- Do not set `break-inside: avoid` on all sections — a section taller than a page overflows or leaves large whitespace.
- A deliberate page break after a self-contained executive summary is usually cleaner than letting the next heading strand at the bottom of page one.
- `break-after: avoid` on a heading container does not always keep a following chart with it. If the chart is a separate sibling and the remaining page area is marginal, use a section-specific page break, or wrap heading and chart in a non-breaking figure when the combined height fits one page.

## URLs and interactive elements

- Hide controls, filters, tooltips, hover instructions, and interactive-only legends.
- Convert essential state into visible static labels before print.
- Append URLs only to meaningful external links, not every navigation anchor.
- Do not print `javascript:`, fragment-only, mail-action, or long generated URLs.
- Add QR codes only when requested, and always with a written URL fallback.

## Verification

Do not declare print support based on the presence of `@media print`.

Verify in Chromium print preview or a PDF export:

- Page one contains the title, as-of date, and primary metric.
- No chart or table is clipped horizontally.
- No blank pages are introduced.
- Section headings are not stranded at page bottoms.
- Table headers repeat where expected.
- Methodology and source survive print.
- Text is readable at 100% PDF zoom and on physical paper.
- Accent meaning survives grayscale.
- Browser header/footer and background-graphics settings are documented if they affect output.

Check more than page count. A large reduction in pages can mean improved layout — or clipped overflow. Confirm the first and last categories, first and last table columns, and expected row totals are present in the rendered pages or extracted PDF text.

`scripts/export_pdf.mjs` exports a PDF headlessly for inspection. When browser automation is not available, state plainly that print CSS was implemented but visual PDF verification was not performed.

## Validated failure patterns

These recur, and each survives a casual review:

| Pattern | Remedy |
|---|---|
| Responsive mobile rules collapsing print grids, because both media conditions match | Override the responsive grid explicitly inside the print block |
| Screen `min-width` clipping the right side of SVG charts and tables | Reset `min-width` and remove scroll overflow in print |
| Whole-section `break-inside: avoid` producing half-empty pages | Protect cards and charts only; let sections and tables fragment |
| A footer or short trailing block creating its own mostly blank page | Hide nonessential screen footers when provenance already appears in the header or methodology |
| A section heading on one page with its chart on the next | Section-specific page break, or wrap heading and chart in a non-breaking figure |
| Dark methodology panels consuming ink or reproducing poorly in grayscale | Normalize to white with a strong border (the `core/print.css` default) |
| Generic structural padding shorthands overriding compound-class card and panel spacing | Reassert component padding with a compound selector, then inspect all four edge insets in the PDF |
| A `.print-only` provenance block printing on top of a title block that already printed fine, so page one carries the title twice | Add the block only when the screen header genuinely does not survive print. Check page one of the export before keeping it |
| A chart sized for a document dropped into a wider surface — it centers with its labels shrunk rather than filling the space | Render at the size of the surface it lands on, not the size of the document it came from |
