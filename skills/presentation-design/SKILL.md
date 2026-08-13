---
name: presentation-design
description: Design presentation decks as self-contained 16:9 HTML slides that export cleanly to PDF — board updates, project reviews, findings readouts, proposals, and conference talks. Use when building a deck, slides, a presentation, or a leadership readout; when converting a report or a set of findings into slides; or when an existing deck needs a coherent visual system and a clean PDF export. Do not use for documents meant to be read rather than presented (use analytical-document-design or longform-document-design), for a single standalone chart or diagram, or when the user specifically needs an editable .pptx file.
---

# Presentation Design

A slide is seen for as long as it takes to say one thing. That constraint drives every rule here.

A deck is not a document with page breaks. If the content only makes sense when read closely, it is a document — say so and use `analytical-document-design` or `longform-document-design` instead. Converting a document into slides by cutting it into pieces produces a deck that is bad to present and worse to read.

## One idea per slide

The title states the idea as a **claim**, not a topic. Everything else on the slide supports that claim.

- "Ingestion is our concentration risk" — a claim. The audience knows what to look for.
- "Ingestion metrics" — a topic. The audience has to work out what they are meant to conclude.

If a slide needs two titles, it is two slides. Slides are free; attention is not.

## Reading and presenting are different jobs

Decide which deck this is, because the answer changes the design and you cannot have both in one artifact:

**Presented** — you are speaking over it. Slides carry few words, large type, and one visual. The detail lives in what you say.

**Read** (sent, not presented) — nobody narrates it. Slides need enough text to stand alone, which means more words and smaller type, and the deck is longer.

When both are needed, build the presented deck and pair it with a document, or add a speaker-notes block that prints but does not project. Do not compromise into a deck that is too dense to present and too sparse to read alone — the common failure that produces a wall of bullets nobody can use for either purpose.

## Slide types

Use a small set. A deck where every slide has a different layout reads as a collection of unrelated files.

| Type | Use |
|---|---|
| Title | Deck title, presenter, date, context |
| Section divider | Marks a shift; a few words on an accent field |
| Statement | One sentence at large size. The argument's turning points |
| Metric | One to three numbers with labels and their denominators |
| Chart | One chart, one takeaway title |
| Diagram | One diagram, one takeaway title |
| Comparison | Two or three columns on a consistent set of criteria |
| Table | Small tables only — six rows and four columns is the practical ceiling |
| Agenda / summary | Structural orientation |
| Closing | The ask, the decision needed, or next steps |

Construction rules for each are in `references/slide-types.md`.

## The 16:9 frame

Slides are `1280 × 720` CSS pixels. That is the authoring unit; the deck scales to any display.

- **Safe margin: 64px on all sides.** Projectors crop, and video conferencing crops differently. Nothing meaningful goes outside it.
- **Baseline type size is 24px.** Body text below 20px is unreadable from the back of a room. If content does not fit at 20px, the slide has too much on it — cut, do not shrink.
- **Title: 40–48px. Statement slide: 56–72px.**
- **8px spacing grid** at this scale, since everything is twice document scale.
- One visual per slide. Two charts on one slide means the audience reads neither.

The token contract in `core/tokens.md` applies in full. `templates/deck.html` is the working skeleton.

## Contrast and the room

Decks fail in rooms in ways documents never do:

- **Assume a washed-out projector.** Subtle contrast that reads well on a laptop disappears under fluorescent light. Push contrast beyond the document minimum.
- **Never rely on thin hairlines.** The 1px rules that give documents their precision vanish when projected. Use 2px at slide scale.
- **Muted text is riskier here.** `var(--soft)` is often too light to project; prefer `var(--muted)`.
- **Dark backgrounds are a room decision, not a taste decision.** They work in a dark room and fail in a bright one, and they consume ink if the deck is printed. When in doubt, light.

## Output

One self-contained HTML file, one `<section class="slide">` per slide, no JavaScript required to read it.

Navigation may be added with CSS scroll-snap — never as a JS dependency the content needs in order to be visible. A deck that renders blank without JavaScript is not a deliverable.

```html
<section class="slide" aria-label="Slide 4: Ingestion is our concentration risk">
  <h2 class="slide-title">Ingestion is our concentration risk</h2>
  <figure class="slide-visual"><!-- one chart or diagram --></figure>
  <p class="slide-note">41% of footprint · 1.84M of 2.50M units · as of 2026-08-12</p>
</section>
```

Charts and diagrams come from `chart-design` and `diagram-design`, rendered at `full-width` and inlined as SVG. Everything scales with the slide because the SVG carries a `viewBox`.

## PDF export

A deck is usually delivered as a PDF, so the export is part of the deliverable, not an afterthought.

```css
@page { size: 1280px 720px landscape; margin: 0; }
.slide { break-after: page; break-inside: avoid; }
```

- One slide per page. Verify no slide splits across two.
- Backgrounds require "Background graphics" enabled in the print dialog. Say so when handing over the file, and make sure the deck still reads if it is disabled.
- `scripts/export_pdf.mjs` exports headlessly for inspection.
- Check the exported PDF, not the print preview. Page count equal to slide count is necessary but not sufficient — confirm nothing is clipped at the frame edges.

## Accessibility

`core/a11y.md` applies. Slide-specific:

- Each slide needs an `aria-label` carrying its number and title, since the visual reading order is not always the DOM order.
- Slide titles are real headings (`<h2>`), not styled `<div>`s.
- Every chart and diagram keeps its `<title>` and `<desc>`.
- Do not encode meaning by position alone — a slide read linearly by a screen reader loses the layout.

## Before delivering

- [ ] Every slide title states a claim, not a topic.
- [ ] One idea per slide; no slide needs two titles.
- [ ] The deck is clearly either presented or read, not a compromise.
- [ ] Nothing meaningful outside the 64px safe margin.
- [ ] No text below 20px.
- [ ] One visual per slide.
- [ ] Contrast holds up on a washed-out projector.
- [ ] Every metric names its denominator and as-of date.
- [ ] Exported PDF has one slide per page, nothing clipped.
- [ ] The deck reads correctly with JavaScript disabled.

## Reference files

- `references/slide-types.md` — per-type construction rules and failure modes.
- `references/deck-structure.md` — narrative arc, deck length, opening and closing.

## Paths in this skill

`core/…` and `scripts/…` are relative to the repo root. When this is installed as a
plugin your working directory is your own project, not the plugin, so prefix them:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/export_pdf.mjs" deck.html --out deck.pdf
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin's own
directory. Working inside the repo itself, the bare paths are correct as written.
