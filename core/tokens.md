# The token contract

Every skill in this repo consumes the same semantic tokens. Components name **roles**, never colors. That indirection is what lets one document swap themes, print correctly, and stay readable in grayscale without touching a single component rule.

A theme changes the visual voice. It must never change metric definitions, category order, chart scales, included records, or narrative conclusions.

## Required tokens

Every theme must define all of these. A theme that leaves one undefined is not a theme — it is a partial override, and `scripts/validate_repository.py` will fail it.

### Surfaces

| Token | Purpose |
|---|---|
| `--paper` | Page background |
| `--surface` | Primary card and table surface |
| `--surface-muted` | Chart frame, secondary region, alternate row |

### Ink

| Token | Purpose |
|---|---|
| `--ink` | Primary text and strong strokes |
| `--muted` | Body-secondary text and comparison strokes |
| `--soft` | Eyebrows, metadata, tertiary labels |

### Structure

| Token | Purpose |
|---|---|
| `--rule` | Hairline dividers and default borders |
| `--rule-strong` | Baselines and emphasized borders |

### Accent

| Token | Purpose |
|---|---|
| `--accent` | The single focal signal |
| `--accent-tint` | Low-emphasis accent surface |
| `--accent-ink` | Text readable on `--accent` |

One accent. It marks the focal signal — the measured value, the one bar that matters, the one risk treatment per region. Using it on every heading destroys the hierarchy it exists to create.

### Status

| Token | Purpose |
|---|---|
| `--positive` | Positive status when semantically required |
| `--warning` | Warning status when semantically required |
| `--critical` | Critical status when semantically required |

Status colors are a deliberate exception to the one-accent rule, permitted only when the data genuinely contains status states. They are not a decorative palette for categories.

### Methodology

| Token | Purpose |
|---|---|
| `--method-bg` | Methodology/provenance section background |
| `--method-ink` | Methodology/provenance primary text |
| `--method-muted` | Methodology/provenance secondary text |

The methodology block gets its own three tokens because it is typically inverted on screen and normalized to white in print. Giving it dedicated roles means print can retarget it without disturbing anything else.

### Typography

| Token | Purpose |
|---|---|
| `--display` | Title, section heading, and large-metric font stack |
| `--sans` | Body, category, table, and name font stack |
| `--mono` | Date, version, source, identifier, and compact-label font stack |

Three roles, not three fonts for their own sake. Mono is for technical metadata; setting body copy in mono to look technical makes a document harder to read, not more credible.

### Geometry

| Token | Purpose |
|---|---|
| `--radius-sm` | Tags and small controls |
| `--radius-md` | Cards, chart frames, and callouts |

Keep radii between 0 and 8px. Larger radii read as consumer-app chrome and undercut an analytical register.

### Derived (optional but recommended)

| Token | Purpose |
|---|---|
| `--comparison-fill` | Non-focal bar/area fill |
| `--track-fill` | Empty portion of a limit ledger or progress track |

`core/base.css` derives these with `color-mix()`. If a target environment cannot support `color-mix()`, a theme must define them explicitly instead. Never compute colors in JavaScript — that reintroduces the coupling the token contract exists to remove.

## Selecting a theme

Set it once, on the root element:

```html
<html lang="en" data-theme="editorial-coral">
```

If the user names a theme, use it. Otherwise:

- `editorial-coral` — general analytical reports, portfolio reviews. The default.
- `executive-navy` — board, finance, governance, conservative corporate contexts.
- `field-notes` — research, audit, workshop, operational-review documents.
- `brand-template` — a documented slot to fill with your own brand. See `themes/brand-template.css`.

Ask one short question only when brand fit materially affects the deliverable and context does not imply a choice.

Reject unknown theme IDs, or fall back explicitly to `editorial-coral`. Never silently emit a partially themed document — a half-themed report looks like a bug to the reader and hides which values were intentional.

## Adding a theme

A real theme is not a new `--accent`. It includes surfaces, typography, border character, methodology treatment, and print behavior.

1. Give it a lowercase hyphenated ID.
2. State its intended contexts and what differentiates it.
3. Define every token above.
4. Keep the same component structure and semantic roles.
5. Use one primary accent.
6. Verify body, muted, accent, and methodology text contrast.
7. Verify every chart in grayscale.
8. Define print overrides only when the base print treatment is insufficient.
9. Test at desktop, mobile, and print widths.

## The rule components must follow

Components consume semantic variables only. A theme's hex values never appear inside component CSS, chart generation, or diagram rendering.

```css
/* Correct */
.focal-bar { fill: var(--accent-tint); stroke: var(--accent); }

/* Wrong — the component now knows about a theme */
.focal-bar { fill: rgba(235, 108, 54, 0.10); stroke: #eb6c36; }
```

This is the one rule the whole system rests on. `scripts/validate_repository.py` greps for hex literals outside `core/themes/` and fails the build when it finds them.
