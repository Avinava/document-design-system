# Slide types

Construction rules per type. All measurements are at 16:9 authoring scale (1280 × 720), with a 64px safe margin.

## Title

Deck title, presenter, date, and enough context that the file makes sense six months later when someone opens it out of a shared drive.

- Deck title 56–64px, left-aligned in the safe area.
- One line of context beneath, in `var(--muted)`, 24px.
- Presenter and date in `var(--mono)`, 18px.
- No stock imagery. No logo wall.

**Failure mode:** a title that names the project rather than the argument. "Q3 Platform Review" tells the audience nothing; "Where our platform capacity goes" tells them what they are about to learn.

## Section divider

Marks a shift in the argument. Should be rare — one every five to eight slides at most.

- Two to five words, 48px, on `var(--accent)` with `var(--accent-ink)`, or on `var(--surface-muted)`.
- Optionally a section number in `var(--mono)`.
- Nothing else.

**Failure mode:** using dividers to pad a short deck. If sections are three slides long, they are not sections.

## Statement

One sentence at large size. Reserve these for the argument's turning points — the two or three moments the audience should remember.

- 56–72px, `var(--display)`, generous line height, no more than three lines.
- Centered vertically, left-aligned horizontally.
- Optional small attribution or source beneath in `var(--mono)`.
- No visual. The words are the visual.

**Failure mode:** using them for section headers, which dilutes them until they carry no weight.

## Metric

One to three numbers, each with a label and a denominator.

- Value 72–96px in `var(--display)`, tabular figures.
- Label directly beneath in `var(--muted)`, 22px.
- Denominator or as-of date in `var(--mono)`, 18px.
- At most one number in `var(--accent)`.
- Three is the ceiling. Four numbers on a slide means none of them is the point.

**Failure mode:** a KPI wall — six equal-sized numbers with no hierarchy. If they are genuinely all equal, they belong in a table in a document.

## Chart

One chart, one takeaway title.

- Title states the finding: "Ingestion holds 41% of the footprint."
- Chart rendered at `full-width` from `chart-design`, inlined as SVG.
- Source and as-of date in `var(--mono)`, 16px, beneath.
- Simplify relative to the document version: fewer categories, larger labels, fewer gridlines. A chart that works on paper at reading distance is usually too dense to project.
- Chart text at slide scale needs to be at least 18px equivalent.

**Failure mode:** reusing a document chart unchanged. Two things go wrong at once, and the result looks merely underwhelming rather than broken, so it survives review.

A chart rendered at `doc-inline` (720px) carries a `max-width` of 720px. Dropped into a 1280px slide it does not stretch — it centers, leaving wide empty margins, and its internal label gutter eats more of what remains. Meanwhile every label inside it was sized for reading distance, not for a room.

Re-render at `full-width` from the same spec. Changing the slide's CSS cannot fix it, because the constraint is baked into the SVG.

## Diagram

One diagram, one takeaway title.

- Rendered at `full-width` from `diagram-design`.
- Simplify hard. A diagram at 4/10 density in a document is closer to 6/10 on a projector, because the audience has seconds rather than minutes.
- If the diagram needs building up, split it across consecutive slides — each adding one layer, with the same geometry so the parts stay in place.

**Failure mode:** a full architecture diagram from a document. Split it, or show only the part the claim is about.

## Comparison

Two or three columns, compared on a consistent set of criteria.

- Columns get equal width, and the criteria stay in the same order in each.
- Header row names each option; the leftmost column names the criteria.
- Accent one column only when the deck is making a recommendation. If it is presenting options neutrally, do not accent any — accenting one is an argument whether or not it is meant as one.
- Three columns maximum.

**Failure mode:** columns compared on different criteria, which makes them non-comparable while looking rigorous.

## Table

Small tables only. Six rows and four columns is the practical ceiling.

- 20px minimum, tabular figures, numbers right-aligned.
- Header in `var(--muted)` with a 2px `var(--rule-strong)` bottom border — hairlines vanish when projected.
- Highlight at most one row or one cell.
- Anything larger belongs in a document that accompanies the deck. Say so on the slide.

**Failure mode:** a twenty-row spreadsheet screenshot. Nobody in the room can read it, and it signals that the presenter did not decide what mattered.

## Agenda / summary

Structural orientation. One at the front, optionally one at the back.

- Three to six items, 28px.
- Number them. Match the wording to the section dividers exactly, or the audience cannot map one to the other.
- No sub-bullets.

**Failure mode:** an agenda listing topics rather than the questions each section answers.

## Closing

The ask, the decision needed, or next steps. Never "Thank you" or "Questions?" — those waste the slide that stays on screen longest, through the entire discussion.

- State what you want: the decision, the approval, the owner, the date.
- Three items maximum.
- Contact details in `var(--mono)` if the deck will be forwarded.

**Failure mode:** ending on a summary of what was said instead of what happens next.
