# Writing

Applies to Markdown and HTML. HTML measure, theme, and print live in `output.md`.

Do not invent a house style guide. Follow an existing technical one when a local choice is not specified: [Google developer documentation style guide](https://developers.google.com/style/highlights), [Microsoft Writing Style Guide](https://learn.microsoft.com/style-guide/), [Write the Docs principles](https://www.writethedocs.org/guide/writing/docs-principles/).

## Voice

- Second person, active voice.
- Sentence-case headings.
- Avoid *should* — use *must* / *can* / *might*, or an imperative.
- Conditions before instructions.
- Lead each section with its conclusion. A reader who stops after the first sentence still gets the point.
- One idea per paragraph. A paragraph that needs a "furthermore" is two paragraphs.
- Prefer prose to bullets for reasoning. Bullets are for enumerable things — options, steps, requirements.
- Define terms on first use; use the same term throughout.
- Put numbers in the sentence when numbers exist.
- Name the actors. "It was decided" hides who can revisit it.

Minimum viable documentation: a small accurate set beats a generated suite. Some repetition across types is fine (ARID); do not factor type files into an abstract framework.

Docs live next to the code they describe. That is why Markdown in the repo is the default.

## Heading hierarchy

- One title (`#` / `<h1>`).
- Type sections as `##` / `<h2>`.
- Subsections as `###` / `<h3>`.
- `####` sparingly. No fifth level — split the document instead.
- Never skip levels.
- Headings are questions or claims, not labels. "How rollout is staged" beats "Rollout".

## Anchors and cross-references

Every heading gets a stable ID derived from its text: lowercase, hyphenated, never auto-numbered. `#section-4-2` breaks the moment a section is inserted above it.

If a heading must be renamed after the document has circulated, keep the old ID as an empty anchor.

Cross-reference by name: "See Alternatives considered". "See section 4.2" is wrong the moment anything moves.

## Change logs

Documents that circulate through review need one, at the top, newest first. Describe what changed substantively. "Updated section 3" tells a returning reviewer nothing; "narrowed scope to exclude the batch path" tells them whether they need to re-read.

## Review mechanics

- **Status** at the top: status, owner, decision date.
- **Reviewer list**, with what each is being asked to check.
- **Open questions** numbered, with owners.
- **Resolved questions kept, marked resolved.**
- Stable identifiers for requirements and questions (`REQ-014`, `Q-3`).

Status values: `Draft`, `Proposed`, `Accepted`, `Superseded by <link>`, `Deprecated`. A superseded document keeps its content and gains a pointer.

## Code, tables, figures

- Label the language on fenced blocks. Keep lines under about 80 characters.
- Show only what matters. A twelve-line excerpt beats a two-hundred-line file.
- Inline code for identifiers, paths, flags, commands — not for emphasis.
- Number and caption tables and figures. Captions below figures, above tables.
- Cross-reference by number and name: "Figure 2: Ingestion path".

HTML-specific treatment (mono, surfaces, print clipping) is in `output.md`.
