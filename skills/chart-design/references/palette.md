# Categorical palettes

Read this only after concluding that one accent plus muted ink genuinely will not work. That conclusion is usually wrong.

## First, don't

A categorical palette assigns meaning to hue. That is the weakest encoding available: it fails in grayscale, fails for the ~8% of men with a color vision deficiency, fails when the chart is printed with background graphics disabled, and requires the reader to consult a legend for every single mark.

Before reaching for one, try in this order:

1. **One focal series in `var(--accent)`, everything else in `var(--comparison-fill)`.** This is the strongest hierarchy available and answers most analytical questions, because most charts are making one point.
2. **Direct labels instead of a legend.** If each series is labelled at its end, hue is decoration rather than encoding, and you can use a single color.
3. **Small multiples.** One panel per category, one color throughout. Removes the need for a palette entirely.
4. **Line style and marker shape.** Solid/dashed/dotted plus circle/square/triangle distinguishes four series with no color at all, and survives grayscale and photocopying.

If two or more of these work, use them. A palette is a fallback, not a default.

## When a palette is genuinely required

Legitimate cases: a stacked composition with three named parts, a set of series that recur across many figures in one document, or a categorical map.

The rules:

- **Six colors maximum.** Beyond six, readers cannot reliably match a mark to a legend entry. If there are more than six categories, group the tail.
- **Always pair hue with a second encoding** — direct label, shape, or line style.
- **Never reuse the status colors.** `var(--positive)`, `var(--warning)`, and `var(--critical)` mean something specific throughout the document. Borrowing them for categories A, B, and C makes every genuine status indicator ambiguous.
- **Keep assignments stable across every figure in a document.** If "Ingestion" is the second color in one chart and the fourth in another, the reader has to re-learn the mapping each time.

## Deriving one from the theme

The palette must come from the theme, so it changes when the theme changes. Define it once, in the document's token block, never inline in a chart.

The construction: anchor on `--accent`, then vary **lightness and chroma** rather than scattering hues. A palette built by rotating hue produces a rainbow — the pattern `core/tokens.md` exists to prevent, and one that carries an implicit ordering the data does not have.

```css
:root {
  /* Sequential-by-emphasis. Anchored on the theme accent, stepping down in
     emphasis rather than around the hue wheel. Position in the sequence
     carries the ordering, so it degrades gracefully into grayscale. */
  --cat-1: var(--accent);
  --cat-2: color-mix(in srgb, var(--accent) 55%, var(--muted));
  --cat-3: var(--muted);
  --cat-4: color-mix(in srgb, var(--muted) 55%, var(--surface-muted));
  --cat-5: color-mix(in srgb, var(--soft) 70%, var(--surface-muted));
  --cat-6: var(--surface-muted);
}
```

This is deliberately monochromatic. It gives an unambiguous visual ordering, it works in grayscale by construction, and it cannot clash with the document.

When categories are genuinely unordered and a monochromatic ramp would imply a ranking that does not exist, add **one** contrasting hue drawn from the theme — not five:

```css
:root {
  --cat-alt: var(--positive); /* only where no status semantics are in play */
}
```

If a document truly needs six unordered, distinguishable hues, it needs small multiples instead. That is not a workaround; it is the better chart.

## Sequential and diverging scales

Different problem, different rules. These encode a *quantity* by color, so ordering is the point.

**Sequential** — one hue, varying lightness, low to high. Anchor light at `--surface-muted` and dark at `--accent`. Never rainbow: the perceptual jumps in a rainbow ramp create boundaries in the data that are not there.

**Diverging** — only when there is a meaningful midpoint (zero, a target, a baseline). Two hues meeting at a neutral center. State what the midpoint is, in the legend. If there is no natural midpoint, use a sequential scale.

Both need a legend with labelled endpoints and the midpoint, because a continuous encoding cannot be direct-labelled.

## Verification

Before shipping any chart that uses more than one color:

1. **Grayscale it.** Screenshot, desaturate. If two categories become the same, the palette is failing.
2. **Check a deuteranopia simulation.** Red/green pairs are the common failure.
3. **Print it with background graphics off.** Fills may vanish entirely; make sure strokes and labels still carry the chart.
4. **Confirm every color-encoded category also has a text label somewhere in the figure.**

If a chart only works in color, it only works on a screen, and most analytical documents are eventually printed.
