---
name: brand-theme-design
description: Turn a brand into a working theme for this design system — from a screenshot, a website, a PDF brand guide, a style guide, or a handful of hex values. Use when asked to match a company's brand, apply brand colors or brand guidelines to documents, make reports look like an existing site or product, build a theme from a logo or screenshot, or fill in the brand-template slot; and when an existing theme needs its contrast, accent, or print behavior audited. Do not use for choosing between the themes that already ship (that is a one-line answer in core/tokens.md), for restyling a single document rather than creating a reusable theme, or for general visual design of a report, diagram, chart, or deck — those belong to the skill for that artifact.
---

# Brand Theme Design

Turn a brand into a theme that satisfies the token contract — and say plainly when the brand cannot do what is being asked of it.

The job is not filling in blanks. A brand guide is a **superset with different intent**: five to eight colors chosen to work on a logo, a billboard, and a product UI. The contract needs a value-structured neutral ramp and exactly **one** accent. Most of the work is deciding what to leave out.

The other half of the job is arithmetic nobody does by eye. Brand colors routinely fail contrast for body text, because body text is not what they were picked for. Finding that out *before* shipping is most of this skill's value.

## Workflow

### 1. Ask what exists

Do not guess the input. Ask which of these they have, and take the best one available:

| Input | How to read it |
|---|---|
| PDF brand guide, style guide | **Best.** Read the pages directly. Brand guides state their hex values as text, which beats sampling any rendering |
| Website | `scripts/extract_site_theme.py <url>` — reads *computed styles* off real elements, not pixels |
| Screenshot, logo, product shot | Look at it directly. Vision judges which color is the brand's "look here" color better than pixel-frequency counting, which just returns the most-used color |
| A few hex values | Go straight to mapping |

`references/extraction.md` covers each path, including what to pull beyond color.

### 2. Extract with provenance

Record where every value came from — "primary `#0B5FFF` ← brand guide p.4", "body ink `#1A1A1A` ← computed `color` on `body`". The user needs to correct your reading, and they cannot correct what they cannot trace.

Capture typography and border character too. A theme that changes only color is not a theme.

### 3. Map to roles — the judgment step

This is where the skill earns its keep, and it is mostly subtraction. The rules, in full, are in `references/mapping.md`. The four that decide most outcomes:

- **The brand's primary is usually not `--accent`.** It is more often the ink, or a heading color. `--accent` marks the one or two things a reader should look at first; a color that appears on every surface cannot do that job.
- **Neutrals must stay close in value.** `--paper`, `--surface`, `--surface-muted` sit within a narrow luminance band. That value structure is what makes a document read as a document rather than as a UI.
- **The leftover brand colors become nothing.** Not a categorical chart palette — `chart-design` rejects exactly that.
- **Brand success/error map to the status tokens, but re-tuned.** Values chosen against a white app background usually fail on this system's surfaces.

### 4. Audit — do not skip and do not eyeball

```bash
python3 scripts/audit_theme.py path/to/theme.css
```

It checks token completeness, every contrast pair at its correct threshold, the one-accent rule, the accent's hue distance from the status colors and from the other themes, and the dark-theme print rule. Non-zero exit on failure.

**When contrast fails, do not quietly darken the brand color and move on.** Say what failed and offer the choice — `references/mapping.md` has the three honest remedies in preference order. A brand color that cannot carry body text is a fact about the brand, and the user is entitled to know it.

### 5. Preview it beside the others

Add the theme as a panel in `templates/themes.html`, build, and show them the result:

```bash
python3 scripts/build_document.py templates/themes.html --theme <brand> --out /tmp/themes.html
```

Seeing it next to `editorial-coral`, `executive-navy`, `field-notes`, and `console-violet` answers "does this look like a member of the system" faster than any description.

Then print one real document with it, per `references/verification.md`. If the theme is dark, the print step is not optional — see below.

### 6. Ship it

**Where the file goes depends on where you are:**

- **Working inside the `document-design-system` repo** → `core/themes/<brand>.css`, then run `scripts/validate_repository.py` and the test suite.
- **The plugin is installed and you are in someone else's project** → write it into *their* project. The plugin directory is read-only and is replaced on update, so a theme written there is silently lost.

Check which situation you are in before writing. If unsure, ask.

## Non-negotiables

Everything in `core/tokens.md` applies. The ones a brand most often pushes against:

- **One accent.** A brand with six colors still gets one. This is the rule most likely to be argued with, and the one that most determines whether documents read clearly.
- **All 22 tokens defined.** A partially themed document looks like a bug.
- **Status colors are semantic**, not a palette to fill with brand secondaries.
- **A dark brand needs its own `@media print` block.** `core/print.css` flattens surfaces to white but deliberately leaves the ink ramp alone, so a dark theme without this prints near-white on white. `console-violet` is the worked example.
- **Font fallbacks are mandatory.** Brand fonts are frequently licensed for web use, unavailable, or both.

## When the brand does not fit

Sometimes the honest answer is that the brand cannot be applied as-is. Say so, and name the specific conflict:

- *"Your brand blue is 3.1:1 on white. It can be the accent and carry headings at 24px and up, but it cannot be body text. Three options…"*
- *"The guide specifies six colors of equal weight. This system gives one of them the accent role and treats the rest as neutrals — which one should lead?"*
- *"Your brand font is not licensed for web embedding. The nearest metric-compatible fallback is X, which will shift line lengths by about 2%."*

That is more useful than a theme that technically renders and quietly fails its readers.

## Before delivering

- [ ] Every value traceable to a source the user can check.
- [ ] `audit_theme.py` passes with no errors.
- [ ] Any warnings shown to the user, not silently accepted.
- [ ] One accent; leftover brand colors are not wired in anywhere.
- [ ] Typography and border character differ, not just color.
- [ ] Previewed beside the shipped themes.
- [ ] Printed a real document; dark themes have a print block.
- [ ] Written to the right place for the context.

## Paths in this skill

`core/…` and `scripts/…` are relative to the repo root. When this is installed as a
plugin your working directory is your own project, not the plugin, so prefix them:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit_theme.py" theme.css
```

`${CLAUDE_PLUGIN_ROOT}` is Claude Code's portable reference to the plugin's own
directory. Working inside the repo itself, the bare paths are correct as written.

## Reference files

- `references/extraction.md` — per-input extraction, and what to capture beyond color.
- `references/mapping.md` — brand palette to semantic roles, the contrast remedies, and a worked example.
- `references/verification.md` — the audit, grayscale, print, and preview steps in order.
