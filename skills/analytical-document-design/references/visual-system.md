# Visual system

The token contract, themes, and component mapping live in `core/`. This file covers what is specific to analytical documents: typography roles, chart construction, and table design.

## Contents

- [Typography](#typography)
- [Font loading](#font-loading)
- [Charts](#charts)
- [Tables](#tables)
- [SVG and tokens](#svg-and-tokens)

## Typography

Use typography by role, not by novelty. The theme supplies the actual stacks; the table below describes the default `editorial-coral`.

| Role | Default | Treatment |
|---|---|---|
| Display / title | Manrope | 600 weight, tight tracking, high legibility |
| Body / names | Geist | 400–600 weight |
| Technical metadata | Geist Mono | Small, tracked, concise |

Rules:

- Display face for titles, section headings, and large metrics.
- Sans for paragraphs, categories, names, and tables.
- Mono only for dates, versions, identifiers, source names, and compact labels.
- Avoid narrow editorial serif faces for large operational metrics — they become fragile at a glance and in screenshots.
- Do not set all text in monospace to make a report appear technical. It reads as a terminal dump, not as rigor.
- Use tabular numerals (or mono) for aligned numeric columns.

## Font loading

Load only the fonts the selected theme needs when generating a single-theme document. A multi-theme preview may load all of them.

`editorial-coral` and `executive-navy`:

```html
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;500;600&family=Manrope:wght@400;500;600;700&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
```

`field-notes`:

```html
<link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;500;600&family=Source+Sans+3:wght@400;500;600;700&display=swap" rel="stylesheet">
```

Always retain system fallbacks. Font availability must never determine whether the document remains usable — and external fonts do fail, in offline environments, restricted networks, and email pipelines.

For a document that must be genuinely self-contained (archived, emailed, opened offline), inline subsetted base64 WOFF2 instead of linking. `scripts/inline_fonts.py` does the subsetting and encoding. Note that base64 adds roughly 33% overhead, so subsetting is required rather than optional.

## Charts

Choose a chart only when it reveals a relationship faster than a table would.

### Horizontal bars

For long category labels and concentration rankings.

- Sort descending unless chronology matters.
- Start bars at zero.
- One focal bar in accent; all others muted.
- Show both absolute value and percentage.
- Name the denominator near the chart.
- Cap the visible chart at eight categories; preserve all rows in supporting data.

### Cohort columns

For year or month composition.

- Chronology left to right.
- Stack only directly comparable populations, such as included versus excluded.
- Label what the stack means.
- Baseline at zero.
- Use current-size wording when historical deltas do not exist.

### Limit ledger

A single horizontal track for used versus available capacity.

- Keep component segments visually distinct.
- State the exact numerator and denominator.
- Show remaining capacity explicitly.
- Prefer a linear track over a gauge — a gauge communicates the same value less precisely and takes more space.

## Tables

Use tables for evidence, exact comparisons, and lists longer than eight items.

- Do not build behavior into a static report that requires JavaScript.
- Keep units in headings, or in values, consistently — not both.
- Align numbers right, with tabular figures.
- Include date and version columns when they inform review priority.
- Use horizontal overflow on small screens rather than crushing columns. `core/base.css` provides `.table-scroll`; `core/print.css` unsets it, because a scroll container clips in print.

## SVG and tokens

When the SVG is inline, CSS variables reach it through classes. Use the shared classes in `core/base.css` rather than presentation attributes:

```html
<rect class="bar-comparison" />
<rect class="bar-focal" />
```

```css
.bar-comparison { fill: color-mix(in srgb, var(--muted) 16%, transparent); stroke: var(--muted); }
.bar-focal      { fill: var(--accent-tint); stroke: var(--accent); }
```

If `color-mix()` compatibility is unacceptable in the target environment, the theme must define `--comparison-fill` and `--track-fill` explicitly. Never calculate colors in JavaScript — that puts theme knowledge back inside components, which is exactly what the token contract exists to prevent.

Every SVG needs a `viewBox`, a `<title>` as its first child, and a `<desc>`. See `core/a11y.md`.
