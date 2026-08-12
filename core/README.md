# core — the shared design system

Every skill in this repo consumes `core/`. It is the single source of truth for tokens, themes, component mapping, print behavior, and accessibility rules.

Skills describe **judgment** — what to measure, when a chart earns its place, how to structure an argument. `core/` describes **mechanics** — what `--accent` means and how a card maps to it. Keeping them apart is what stops five skills from drifting into five incompatible design systems.

## Files

| File | What it is |
|---|---|
| `tokens.md` | The token contract. Every required semantic token, what it means, and the rules for adding a theme. |
| `themes/editorial-coral.css` | Default theme. Warm, precise, broadly shareable analytical reports. |
| `themes/executive-navy.css` | Board, finance, governance. Lower expression, higher contrast. |
| `themes/field-notes.css` | Research, audit, workshop. Tactile warm paper. |
| `themes/brand-template.css` | Documented slot for your own brand. Copy, fill every TODO, rename. |
| `base.css` | Component-to-token mapping. Contains no color literals. |
| `print.css` | Print and PDF as a distinct output mode. Load last. |
| `a11y.md` | Accessibility contract: SVG labelling, contrast, grayscale, focus. |

## Using it in a document

Load order is not cosmetic. Print rules must come last so they beat responsive rules — print rendering can match a narrow-viewport media query, and without that ordering a desktop grid silently collapses to one column in the PDF.

```html
<html lang="en" data-theme="editorial-coral">
<head>
  <style>
    /* 1. theme  2. base  3. print — inlined, in this order */
  </style>
</head>
```

Documents ship as **one self-contained HTML file**, so in practice these files are inlined into a `<style>` block rather than linked. `templates/document.html` shows the assembled result.

## The one rule

Components consume semantic variables only. A theme's hex values never appear in component CSS, chart generation, or diagram rendering.

`scripts/validate_repository.py` enforces this by failing on any hex literal found outside `core/themes/`.

## Changing core

A change here reaches all five skills, so:

1. Adding a token means adding it to **every** theme, including `brand-template.css`, and documenting it in `tokens.md`.
2. Renaming a token means updating every skill that names it.
3. Never add a second decorative accent. The one-accent rule is load-bearing — it is what makes the focal signal legible.
4. Run `python scripts/validate_repository.py .` before committing.
