# Prose and structure

Mechanics that make a long document navigable, reviewable, and durable.

## Contents

- [Heading hierarchy](#heading-hierarchy)
- [Anchors and cross-references](#anchors-and-cross-references)
- [Change logs](#change-logs)
- [Review mechanics](#review-mechanics)
- [Code in prose](#code-in-prose)
- [Tables and figures](#tables-and-figures)
- [Measure and rhythm](#measure-and-rhythm)

## Heading hierarchy

- One `<h1>`: the document title.
- `<h2>` for the main sections named by the document type.
- `<h3>` for subsections.
- `<h4>` sparingly.
- No `<h5>` or `<h6>`. Needing them means the structure should be reconsidered, or the document should be split.

Never skip levels — an `<h2>` followed by an `<h4>` breaks the outline for screen readers and for any tool that generates a TOC.

Headings are questions or claims, not labels. "How rollout is staged" beats "Rollout". "The queue has no failover" beats "Queue".

## Anchors and cross-references

Every heading gets a stable ID derived from its text:

```html
<h2 id="alternatives-considered">Alternatives considered</h2>
```

- Lowercase, hyphenated, derived from the text.
- **Never auto-numbered.** `#section-4-2` breaks every inbound link the moment a section is inserted above it — including links from tickets, chat, and other documents you cannot edit.
- If a heading must be renamed after the document has circulated, keep the old ID as an empty anchor so existing links still land.

Cross-reference by name:

```html
See <a href="#alternatives-considered">Alternatives considered</a>.
```

"See section 4.2" is wrong the moment anything moves, and nobody notices because it still looks like a valid reference.

## Change logs

Any document that circulates through review needs one, at the top, newest first.

```html
<table class="changelog">
  <caption>Change log</caption>
  <thead><tr><th>Date</th><th>Change</th><th>By</th></tr></thead>
  <tbody>
    <tr><td>2026-08-12</td><td>Added rollback plan after review</td><td>Author</td></tr>
    <tr><td>2026-08-08</td><td>Initial draft</td><td>Author</td></tr>
  </tbody>
</table>
```

Describe what changed substantively. "Updated section 3" tells a returning reviewer nothing; "narrowed scope to exclude the batch path" tells them whether they need to re-read.

## Review mechanics

Documents that are reviewed need affordances documents that are merely read do not:

- **Status banner** at the top: status, owner, decision date.
- **Reviewer list**, with what each is being asked to check. "Please review" to five people produces five overlapping partial reviews; "Sam: the storage tradeoff; Kim: the rollout risk" produces two useful ones.
- **Open questions** as a numbered list with owners, so they can be referenced in discussion.
- **Resolved questions kept, marked resolved.** Deleting them means the same question gets raised again by the next reviewer.
- **Stable numbering for requirements and questions** so comments elsewhere stay meaningful.

## Code in prose

- Blocks in `var(--mono)` at 0.875em, on `var(--surface-muted)`, with a 1px `var(--rule)` border.
- **Label the language.**
- Keep lines under about 80 characters. Long lines force horizontal scrolling on screen and clip in print.
- Show only what matters. A twelve-line excerpt with an ellipsis beats a two-hundred-line file.
- Inline code (`var(--mono)`, 0.9em) for identifiers, paths, flags, and commands — not for emphasis.
- In print, code blocks must not clip. Wrap long lines, or accept a scroll container that `core/print.css` neutralizes.

## Tables and figures

- Number and caption both: `Table 3: Storage options compared`, `Figure 2: Ingestion path`.
- Captions go below figures and above tables — the long-standing convention, and readers rely on it.
- Cross-reference by number *and* name: "Figure 2: Ingestion path". Numbers alone are fragile.
- A table needs a `<caption>` naming its population, and a `<th>` per column with real scope.
- Keep figures non-breaking in print so a caption never separates from what it captions.

## Measure and rhythm

- **62–72 characters per line.** The highest-impact typographic decision in a prose document. `core/base.css` sets `max-width: 68ch` on paragraphs.
- Line height 1.55–1.65 for body copy.
- Paragraphs separated by space, not indentation, on screen.
- Space above a heading roughly twice the space below it — a heading belongs to what follows.
- Lists get the same measure as body copy.
- Do not justify text. Without hyphenation, justification produces uneven word spacing that is measurably harder to read.

Full-width prose on a wide monitor is the most common readability failure in HTML technical documents, and it is entirely avoidable.
