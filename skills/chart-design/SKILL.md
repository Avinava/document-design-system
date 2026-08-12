---
name: chart-design
description: Design honest, accessible charts of quantitative data as inline SVG — bar and column charts, line and time series, limit ledgers, distributions, scatter plots, and small multiples. Use when visualizing measured values, choosing a chart type, picking or fixing chart colors, building a categorical palette from design tokens, setting axes and scales, labelling series, or making an existing chart readable in grayscale and in print. Do not use for diagrams of structure or process such as architecture or flows (use diagram-design), for the surrounding report narrative and metric semantics (use analytical-document-design), or for interactive dashboards that require a client-side charting library.
---

# Chart Design

A chart is an argument about numbers. Its job is to make one comparison faster than a table would — and to make the wrong reading hard.

Choose a chart only when it reveals a relationship faster than a table. A chart of four values is slower to read than four labelled numbers, because the reader has to decode the encoding before they get the data.

## The honesty rules

These are not stylistic. Breaking them changes what the reader concludes.

- **Bar and column charts start at zero.** A truncated bar axis multiplies apparent differences by an arbitrary factor. If small differences matter, use a line chart, a dot plot, or state the values.
- **Line charts may use a non-zero axis** — they encode position, not length — but the axis must be labelled and the truncation visible.
- **Area encodes one quantity, not two.** Doubling both width and height quadruples the area for a doubled value.
- **Percentages name their denominator**, near the chart, not buried in a footnote.
- **Equal visual weight means equal comparability.** Do not put two different units on one axis.
- **Time on an axis is continuous.** Missing months appear as zero or as a marked gap, never by silently closing up.
- **State when a scale is logarithmic**, in the axis label, not the caption.
- **Categories are categories, even when they look like numbers.** Years, quarters, ports, and version numbers are labels, not measurements. Put them on a categorical (band) scale. Left on a continuous scale, `2020…2025` gets positioned by arithmetic distance, and a missing year silently becomes a gap the data never had.

If the data does not support the chart's implicit claim, change the chart, not the axis.

## Choosing a form

| The reader needs | Form |
|---|---|
| Rank and compare categories | Horizontal bars, sorted descending |
| Compare a value across time periods | Columns, chronological |
| A trend, or many series over time | Line |
| Used versus available against a limit | Limit ledger (single track) |
| Composition of a whole, 2–3 parts | Stacked bar, labelled |
| Composition of a whole, many parts | Ranked bars — not a pie |
| Relationship between two measures | Scatter |
| The same comparison across groups | Small multiples |
| Distribution shape | Histogram or box plot |

Never a pie chart with more than three slices. Angle is the hardest encoding to judge, and a ranked bar chart answers the same question in less space.

Never a dual-axis chart. The crossover point is set by the axis scaling, which means it is set by the author, which means it proves nothing.

Per-form construction rules are in `references/chart-forms.md`.

## Color

The token contract in `core/tokens.md` applies. Charts add one constraint that matters more here than anywhere else in this system:

**Color is the last encoding to reach for, and never the only one.**

- **Default to one accent plus muted ink.** One focal bar in `var(--accent)`, everything else in `var(--comparison-fill)`. This handles most analytical charts and is the strongest hierarchy available.
- **Categorical palettes are a last resort.** If the chart needs more than one hue, it usually needs to be small multiples instead.
- **Never encode a category by hue alone.** Direct-label the series, or vary line style and marker shape as well.
- **Status colors are for status.** `var(--positive)`, `var(--warning)`, `var(--critical)` mean something. Using them as a three-category palette destroys that meaning everywhere else in the document.
- **Verify in grayscale.** If two series become indistinguishable, they were only ever distinguished by hue.

For deriving a genuine categorical palette from the theme when one is unavoidable, see `references/palette.md`.

## Labels

Most chart failures are labelling failures.

- **Direct-label series** at the end of a line or beside a bar. A legend is a lookup table the reader holds in memory.
- **Show the value** when there are fewer than about twelve bars. The chart shows the shape; the number shows the fact.
- **Never put labels inside bars.** They collide with short bars and get clipped.
- **Axis labels carry units.** `Units (thousands)`, not `Units`.
- **The title states the finding**, not the variables. "Ingestion holds 41% of the footprint" beats "Size by function".
- **Name the as-of date and the denominator** in or beside the figure.

## Output

Inline SVG. No client-side charting library, unless interactivity is an explicit requirement — and it usually is not, because a static chart is what survives being printed, emailed, and screenshotted.

```html
<figure class="chart">
  <svg role="img" aria-labelledby="ch-fn-title ch-fn-desc" viewBox="0 0 720 320" width="100%">
    <title id="ch-fn-title">Current footprint by function</title>
    <desc id="ch-fn-desc">Nine functions ranked by size. Ingestion holds 41 percent of the 1.8 million unit total, more than the next three combined.</desc>
    ...
  </svg>
  <figcaption>Source: normalized inventory export, as of 2026-08-12. Denominator: 1,842,110 included units.</figcaption>
</figure>
```

`<title>` first, unique IDs prefixed per figure, `viewBox` always. The `<desc>` states the comparison and its result — that sentence is what a screen-reader user gets instead of the chart, and writing it is the fastest test of whether the chart has a point.

Use the shared SVG classes in `core/base.css` (`.bar-focal`, `.bar-comparison`, `.axis-line`, `.grid-line`, `.chart-label`, `.chart-value`) rather than presentation attributes, so a theme change reaches every chart.

To generate charts from data rather than hand-authoring them, `scripts/render_chart.mjs` renders Observable Plot to a static SVG at authoring time. See `references/rendering.md`.

## Density

- No more than eight visible categories. Combine the tail into a labelled "Other" and keep every row in the supporting data.
- No more than about five lines on one chart. Beyond that, use small multiples.
- Gridlines are hairlines in `var(--rule)`, or absent. They orient; they are not part of the data.
- No chartjunk: no 3D, no shadows, no gradients, no textured fills, no background images.
- Remove the axis line where the gridlines already imply it.

## Before delivering

- [ ] The chart is faster to read than the equivalent table.
- [ ] Bars start at zero; any truncated axis is labelled and visible.
- [ ] Every percentage names its denominator.
- [ ] Series are direct-labelled, not legend-only.
- [ ] No meaning is carried by hue alone.
- [ ] Legible in grayscale.
- [ ] The title states the finding.
- [ ] `viewBox`, `<title>` first, `<desc>`, unique IDs.
- [ ] Eight categories or fewer visible; the tail is accounted for.
- [ ] Readable at print width, not just at authoring width.

## Paths in this skill

`core/…` and `scripts/…` are relative to the repo root. When this is installed as a
plugin your working directory is your own project, not the plugin, so prefix them:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit_theme.py" theme.css
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin's own
directory. Working inside the repo itself, the bare paths are correct as written.

## Reference files

- `references/chart-forms.md` — per-form construction rules and failure modes.
- `references/palette.md` — deriving a categorical palette from theme tokens, and when not to.
- `references/rendering.md` — generating charts from data with Observable Plot.
