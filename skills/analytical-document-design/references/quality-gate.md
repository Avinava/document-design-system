# Quality gate

Run before delivering. Most of these are cheap to check and expensive to discover after the report has been circulated.

## Evidence

- [ ] Included and excluded populations are explicit.
- [ ] Displayed totals reconcile to detailed records.
- [ ] Every percentage has the intended denominator, named near the figure.
- [ ] Snapshot cohorts are not described as historical growth.
- [ ] Creator / modifier / owner semantics are accurate.
- [ ] Inferred classifications carry confidence or a caveat.
- [ ] Review candidates are not presented as guaranteed savings.

## Narrative

- [ ] The title states the reader's question, not the implementation.
- [ ] The first screen shows current state and material implications.
- [ ] Each chart answers a different question.
- [ ] Findings are written as facts before interpretations.
- [ ] Methodology explains source, as-of date, and limitations.

## Design

- [ ] One accent color carries the focal signal.
- [ ] No shadows or decorative gradients.
- [ ] Display metrics use a legible professional font.
- [ ] Mono is limited to technical metadata.
- [ ] No chart shows more than eight visible categories.
- [ ] Tables remain usable on mobile.

## Theme

- [ ] A documented theme ID is set once on the root element.
- [ ] Every required semantic token is defined.
- [ ] Components contain no theme-specific hex values.
- [ ] One primary focal accent.
- [ ] Status colors appear only for real semantic states.
- [ ] Body, muted, accent, and methodology contrast meet accessibility requirements.
- [ ] Typography uses display, body, and technical roles consistently.
- [ ] Charts remain understandable in grayscale.
- [ ] Theme identity survives print normalization.
- [ ] Desktop, mobile, and print renderings were checked.

## Print and PDF

- [ ] `@page` declares the intended size and margins.
- [ ] Screen-only controls and navigation are removed.
- [ ] Title, source, as-of date, and methodology remain visible.
- [ ] Headings avoid breaks immediately after them.
- [ ] Small cards, figures, and callouts avoid internal page breaks.
- [ ] Long sections and tables flow naturally.
- [ ] Table headers repeat across pages where supported.
- [ ] Wide tables do not clip or shrink below readable sizes.
- [ ] SVG charts have a `viewBox`, fit page width, and stay legible.
- [ ] Color meaning survives grayscale and disabled background graphics.
- [ ] External URLs are appended only where useful.
- [ ] Print preview or exported PDF was visually inspected — **or** the lack of visual verification is disclosed.

## Accessibility

- [ ] SVGs have unique title/description IDs, `<title>` first, and a `viewBox`.
- [ ] Text labels accompany every color encoding.
- [ ] Contrast is sufficient for body, muted, accent, and methodology text.
- [ ] Navigation and non-SVG visualizations have accessible labels.
- [ ] Focus is visible on links and controls.

## Delivery

- [ ] HTML opens without a build step.
- [ ] Supporting data files contain the expected row counts.
- [ ] Generator syntax or build checks pass.
- [ ] Regeneration produces stable totals and classifications.
- [ ] The intended page format and print-dialog requirements are documented.
