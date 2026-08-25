# Document patterns

Themes and patterns are independent axes.

- A **theme** sets visual voice through semantic tokens: paper, ink, accent,
  typography, borders, and status colour.
- A **pattern** sets reading behaviour through structure: where the answer
  appears, which relationships are visible, and which modules repeat.

The root element declares both:

```html
<html lang="en" data-theme="field-notes" data-pattern="decision">
```

Changing `data-theme` must not change the information architecture. Changing
`data-pattern` must not invent facts or alter the document's evidence state.
Pattern CSS lives in `core/document-patterns.css` and contains no colour
literals; every component consumes the active theme's semantic tokens.

## The eight families

| Pattern | Reader movement | Characteristic modules | Types |
|---|---|---|---|
| `decision` | Orient to the ask, compare choices, record what is needed next | ask band, comparison grid, decision rail, risks | `design-doc`, `discovery`, `proposal` |
| `record` | Confirm status, read the decision, trace consequences | compact record header, status stamp, consequence register | `adr` |
| `contract` | Find an exact rule, example, or compliance condition | wide requirement tables, specimens, definition blocks, verdict | `spec`, `api-contract`, `test-report`, `reference` |
| `procedure` | Establish safety, execute in order, verify or recover | preconditions, numbered steps, checkpoints, danger and rollback | `handoff`, `how-to`, `runbook` |
| `learning` | Build context, complete a path, consolidate understanding | learning goal, staged lesson, checkpoints, takeaways | `explanation`, `onboarding`, `tutorial` |
| `system` | Build a spatial model, then inspect boundaries and states | system map, boundary cards, state grid, interface ledger | `architecture`, `design-handoff` |
| `incident` | See severity first, reconstruct time, connect cause to action | impact strip, timeline, cause chain, action register | `postmortem` |
| `suite` | Orient across a linked documentation set | document map, ownership matrix, freshness state | `mulesoft` |

The family is a constraint, not a page template. Two documents in the same
family may omit or reorder modules when their reader's question requires it.
The invariant is that they support the same reading movement.

## Selection

Select the document type first. Its reference file declares the default
pattern and theme. Override the theme freely when the audience needs a
different voice. Override the pattern only when the document's reading task
has genuinely changed; in most cases that means the type is wrong.

Do not collapse every page back to a centred stack of headings and cards.
Prose remains readable at 62–72 characters, while tables, maps, timelines,
comparisons, and action registers may use the wider document shell.

## Fonts and portability

Web previews and GitHub Pages link to the declared Google Fonts so the intended
voice is visible without inflating every HTML file. Offline, email, archival,
and PDF deliverables must embed or package fonts explicitly, or use a verified
system-font fallback. A linked font is not an offline promise.

## Acceptance checks

- The root has a known `data-pattern` and `data-theme`.
- The type reference, generated HTML, and gallery agree on both defaults.
- The pattern exposes its characteristic modules before decoration is judged.
- At 390px, reading order is unchanged and no page-level horizontal scroll is
  introduced. Wide tables may scroll inside `.table-scroll`.
- In print, grids and tables remain intentional, headings do not strand, and
  code does not clip.
- `core/document-patterns.css` contains no colour literals.
