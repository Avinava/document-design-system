# Mapping a brand onto the token contract

The extraction step gives you a pile of colors. This step decides what each one becomes — and, mostly, what to discard.

## Contents

- [Why this is subtraction](#why-this-is-subtraction)
- [Role by role](#role-by-role)
- [When the brand color fails contrast](#when-the-brand-color-fails-contrast)
- [Typography](#typography)
- [Border character and geometry](#border-character-and-geometry)
- [A worked example](#a-worked-example)

## Why this is subtraction

A brand guide is built for a different job. It has to survive a logo at 16px, a billboard, a product UI with buttons and states, and a merchandise print run. So it ships a *palette* — five to eight colors of roughly equal standing, plus neutrals.

A document theme needs almost the opposite: a tight neutral ramp carrying nearly everything, and one color that means **look here**. A palette of equals cannot produce a focal point, because if everything is emphasized nothing is.

So the first question is not "where does each brand color go" but "which single brand color earns the accent, and can the rest go away".

## Role by role

### `--accent`

**The brand's primary is usually the wrong choice.** A primary is, by design, the color used most — on the logo, the nav, the buttons. A color the reader sees constantly cannot also mean "this specific thing matters."

Better candidates, in order:

1. A brand color reserved for emphasis, calls to action, or highlights.
2. The primary, *if* the brand is otherwise neutral and the primary is used sparingly.
3. A brand secondary with enough saturation to read as deliberate.

Then check it against `core/tokens.md`'s two measurements — distance from the status hues, and distance from the other themes' accents. `scripts/audit_theme.py` reports both.

### `--paper`, `--surface`, `--surface-muted`

From the brand's neutrals, not its colors. Three rules:

- Keep them **close in value**. A big jump between paper and surface reads as stacked UI panels rather than a document.
- If the brand's neutral is pure white, warm or cool it very slightly toward the brand's temperature. Pure white makes the design feel sterile, and a hint of the brand's cast ties the theme together.
- `--surface-muted` is a recess, not a second surface. It sits between paper and surface in emphasis.

### `--ink`, `--muted`, `--soft`

Usually the brand's darkest neutral, then two steps up.

**A brand's dark color often is the ink** — many brands' "primary dark" is exactly a body text color. Take it. But it must clear 4.5:1 on `--surface`; if it does not, the brand does not have a body text color and you need to darken one.

Tint the ramp toward the brand rather than using pure greys. Coloured neutrals are most of what makes a theme feel like a brand, and they cost nothing in contrast.

### `--rule`, `--rule-strong`

The ink at low opacity, matching the convention in the shipped themes. Do not use a brand color for hairlines — structure is not signal.

### `--positive`, `--warning`, `--critical`

If the brand defines semantic colors, start there — but **re-tune them**. Brand status colors are chosen against a white app background and often fail on this system's surfaces, and a dark theme always needs them restated.

If the brand defines none, keep the shipped values. Status colors are not a place for brand expression, and inventing them adds risk for no gain.

### `--method-bg`, `--method-ink`, `--method-muted`

The methodology block inverts on light themes and recesses on dark. On light, `--method-bg` is usually the brand's darkest neutral. Check both text tokens against it.

### `--accent-tint`, `--accent-ink`

`--accent-tint` is the accent at about 10–14% — used as a fill behind an accent border.

`--accent-ink` is the text that sits **on** the accent, and it is the pair most often gotten wrong. White is the reflex and it is frequently wrong: white on a mid-tone orange or yellow fails AA badly. The system's own default shipped at 3.12:1 until the auditor caught it. Test both white and a dark ink, and take whichever clears 4.5.

### The leftovers

Nothing. Not a chart palette — `chart-design/references/palette.md` explains why hue-based categorical palettes are the wrong encoding regardless of where the hues came from. Not a second accent. If the user insists their brand needs all six colors present, explain that the system spends its color budget on one signal, and that adding more removes the reader's ability to know where to look.

## When the brand color fails contrast

This is common and it is not a failure of the mapping. Brand colors are chosen for logos.

Say what failed with the number, then offer these in order:

1. **Split the role.** Keep the brand color exactly as-is for `--accent` — accents mark and fill, they rarely carry small text — and derive a darkened variant for anything textual. The brand stays visually intact where it is seen most.
2. **Adjust lightness, hold hue.** Darken or lighten until it clears, keeping hue and saturation. Often a 10–15% lightness move is enough and stays recognisably the brand color.
3. **State the limit.** Some colors cannot carry body text at any size that matters. Say so and use the color structurally — accent, rules, fills — with a compliant ink for text.

What not to do: pass it silently, or use the brand color for text anyway and note the failure in a comment nobody reads.

## Typography

Capture three roles, not three fonts for their own sake: display, sans, mono.

- **Brand fonts are often unavailable** — licensed for print only, self-hosted behind auth, or paid. Ask before assuming you can load one.
- Always end the stack with a system fallback. `core/tokens.md` is explicit that font availability must not determine whether the document is usable.
- Prefer a **metric-compatible** fallback where one exists, so line lengths do not shift when the web font fails.
- If the brand is all-sans, keeping a distinct display face is still legitimate — the contrast between display and body is load-bearing in this system.

## Border character and geometry

`--radius-sm` and `--radius-md` carry more brand character than their size suggests. A brand with sharp corners and one with soft corners produce visibly different documents from identical markup. Read the radius off the brand's real UI and keep it in the 0–8px band.

## A worked example

**Input** — a fictional brand guide states: Primary `#0B5FFF`, Ink `#101828`, Slate `#475467`, Cloud `#F2F4F7`, Success `#12B76A`, Warning `#F79009`, Error `#F04438`. Fonts: Söhne (display + body), no mono specified.

**Mapping and the reasoning:**

| Token | Value | Why |
|---|---|---|
| `--ink` | `#101828` | The brand's ink is already a body text color. 16.1:1 on white |
| `--muted` | `#475467` | Brand slate. 7.5:1 — clears AA |
| `--soft` | `#667085` | Derived one step up; the guide has no tertiary |
| `--paper` | `#F9FAFB` | Cloud, lightened slightly so surface can sit above it |
| `--surface` | `#FFFFFF` | |
| `--surface-muted` | `#F2F4F7` | Cloud proper, as the recess |
| `--accent` | `#0B5FFF` | The primary — this brand is otherwise neutral, so it qualifies |
| `--accent-ink` | `#FFFFFF` | 4.9:1 on that blue. Passes; would not have on a lighter blue |
| `--positive/warning/critical` | brand values | Present and semantic; re-checked against `--surface` |

**The failure it hits:** the primary at `#0B5FFF` is 4.9:1 on white — fine for `--accent-ink` in reverse, and fine as an accent. But the user asks for links in brand blue on `--surface-muted` (`#F2F4F7`), where it measures 4.6:1. That passes for normal text but only just, and fails if anyone lightens the surface.

**The remedy taken:** remedy 1. Keep `#0B5FFF` as `--accent`; use `#0A54DB` for linked text, which measures 6.1:1 and is indistinguishable from the brand blue at text sizes.

**The typography answer:** Söhne is a licensed webfont the user may not have rights to redistribute. The stack becomes `'Söhne', 'Inter', system-ui, sans-serif` — Inter is close in metrics, so a missing Söhne shifts the layout very little. No brand mono, so the shipped mono stack stays.
