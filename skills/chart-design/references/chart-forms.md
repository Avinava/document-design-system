# Chart forms

Per-form construction rules. Each entry covers what the form is for, how to build it, and the failure mode it invites.

## Contents

- [Horizontal bars](#horizontal-bars)
- [Columns](#columns)
- [Line and time series](#line-and-time-series)
- [Limit ledger](#limit-ledger)
- [Stacked bar](#stacked-bar)
- [Waterfall bridge](#waterfall-bridge)
- [Scatter](#scatter)
- [Small multiples](#small-multiples)
- [Histogram and box plot](#histogram-and-box-plot)
- [Forms to avoid](#forms-to-avoid)

---

## Horizontal bars

**For:** ranking and comparing categories, especially with long labels.

- Sort descending unless chronology matters. An unsorted categorical bar chart wastes the reader's most useful comparison.
- Start at zero. Always.
- Labels sit to the left of the axis, left-aligned, in `var(--sans)`. Values sit to the right of each bar's end, in tabular figures.
- One focal bar in `var(--accent)`; all others `var(--comparison-fill)` with a `var(--muted)` stroke.
- Show both the absolute value and the share, and name the denominator near the chart.
- Cap at eight visible categories. Combine the tail into "Other (n categories)" and keep every row in the supporting CSV.

**Failure mode:** labels inside bars. They clip on short bars and collide on long ones.

---

## Columns

**For:** comparing a value across time periods.

- Chronological, left to right. Never sorted by value — that destroys the axis.
- Start at zero.
- Keep the gap between columns narrower than the columns themselves, or the eye groups them wrongly.
- Missing periods appear as zero-height columns with their label, not by closing up the axis.
- When showing cohorts, label what the cohort means. "Current size by creation year" and "amount added per year" are different facts and look identical.

**Failure mode:** more than about fifteen columns. Switch to a line chart.

---

## Line and time series

**For:** trends, and comparing several series over time.

- A non-zero y-axis is legitimate here, because a line encodes position rather than length. Label the axis and make the truncation visible.
- Time on x, evenly scaled. Irregular intervals must be positioned by their real values, not spaced evenly.
- Direct-label each line at its right end. No legend.
- At most about five lines. Beyond that, use small multiples, or draw one series in `var(--accent)` and the rest in `var(--rule)` as context.
- Distinguish series by line style and end marker as well as color, so grayscale survives.
- Break the line across genuine data gaps. Interpolating across missing data invents values.

**Failure mode:** a smoothed spline through sparse points. Curve fitting implies measurements between the points that were never taken. Use straight segments.

---

## Limit ledger

**For:** used versus available against a known limit.

A single horizontal track — the clearest way to show consumption against a ceiling.

- One track, full width. Used segment in `var(--accent)`, remaining in `var(--track-fill)`.
- State the exact numerator and denominator as text: `1.84M of 2.50M units (74%)`.
- Show remaining capacity explicitly. A reader looking at a capacity chart is asking "how much is left," so answer it in words.
- If the used portion has components, segment it — but keep segments visually distinct and directly labelled.
- Needs an `aria-label` carrying the exact values; the shape alone conveys nothing to a screen reader.

**Failure mode:** a gauge or donut. Both take more space to communicate the same value less precisely.

---

## Stacked bar

**For:** composition of a whole, when there are two or three parts.

- Only stack directly comparable populations — included versus excluded, used versus free. Stacking unrelated categories produces segments whose lengths cannot be compared because they do not share a baseline.
- Label what the stack means, in the axis title.
- Order segments consistently across every bar.
- Only the bottom segment is easy to compare across bars; put the segment that matters most there.
- Three segments is the practical limit.

**Failure mode:** the 100% stacked bar used to compare many categories. Every bar is the same length, so the only readable comparison is the bottom segment.

---

## Waterfall bridge

**For:** how a total is built from its parts, or how one total moves to another — an estimate from its work packages, a forecast from last month's.

- One row per step, read top to bottom. Each bar floats from the running total before it to the running total after it; a total starts at zero.
- **The parts must sum to the totals.** `scripts/render_chart.mjs` refuses a spec whose declared total disagrees with its steps, because the chart would print one number and draw another.
- Direction is carried three ways, never by hue alone: a signed label (`+9`, `−2`), the side the bar grows toward, and the label sitting at the bar's leading end.
- Totals take the focal accent; steps are `var(--comparison-fill)`. Thin dotted connectors carry the running total from one bar to the next so the arithmetic can be audited by eye.
- A pending or excluded change — a change request not yet approved — is drawn as a dashed outline after the total with its reason in words ("+3 · not approved"). It is never added to a total.
- An estimate range belongs on the total as a whisker, labelled with its bounds.

**Failure mode:** a bridge whose bars do not reconcile — rounded steps that sum to 23 beside a total of 24. Fix the numbers or name the rounding; never let the reader find it.

---

## Scatter

**For:** the relationship between two measures.

- Both axes labelled with units. Neither needs to start at zero, but say so if truncated.
- Direct-label the outliers and the points under discussion; leave the rest unlabelled.
- Do not draw a trend line unless the fit is stated and the relationship is real. A trend line asserts a model.
- Overlapping points need transparency or jitter, and the caption should say which was used.
- `var(--accent)` marks the points the argument is about.

**Failure mode:** implying causation through arrangement. A scatter shows association. The caption must not upgrade it.

---

## Small multiples

**For:** the same comparison repeated across groups.

Often the right answer when a single chart has too many series.

- Identical scales across every panel. Different scales make the panels non-comparable, which defeats the entire form.
- Identical axes, drawn once at the edges rather than repeated in every panel.
- Panel titles in `var(--sans)`, consistent position.
- Order panels meaningfully — by magnitude, chronology, or a grouping that the caption names.
- Three to twelve panels. Fewer belongs on one chart; more is a table.

**Failure mode:** per-panel auto-scaling. It makes every panel look similar and hides the differences the chart exists to show.

---

## Histogram and box plot

**For:** the shape of a distribution.

- State the bin width for a histogram; the shape is a function of it.
- Do not choose a bin width that manufactures or hides a mode. Try several and say which was used.
- Box plots need their convention stated — whiskers at 1.5 IQR, at min/max, or at percentiles, all of which look identical.
- Show n. A distribution of twelve observations and one of twelve thousand look the same and mean very different things.

**Failure mode:** a box plot for a small or bimodal sample. Show the points instead.

---

## Forms to avoid

| Form | Why | Instead |
|---|---|---|
| Pie with more than three slices | Angle is the hardest encoding to judge | Ranked horizontal bars |
| Donut with a number in the middle | The ring adds nothing to the number | The number, or a limit ledger |
| Dual-axis chart | The crossover point is set by the author's scaling, so it proves nothing | Two aligned charts, or index both to a base period |
| 3D anything | Perspective distorts the encoding | The 2D form |
| Radar / spider | Area depends on axis order, which is arbitrary | Grouped bars or small multiples |
| Word cloud | Encodes frequency by area and position by nothing | A ranked table |
| Truncated bar axis | Multiplies apparent differences arbitrarily | Zero baseline, or a dot plot |
