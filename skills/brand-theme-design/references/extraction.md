# Extraction, per input

Get the palette and the typography out of whatever the user has, and record where each value came from.

Provenance is not bookkeeping. The user is the only one who knows whether the blue you found on their pricing page is the brand blue or a button state, and they can only correct what they can trace.

## Contents

- [PDF brand guide](#pdf-brand-guide)
- [Website](#website)
- [Screenshot or logo](#screenshot-or-logo)
- [Hex values](#hex-values)
- [What to capture beyond color](#what-to-capture-beyond-color)
- [The report to show the user](#the-report-to-show-the-user)

## PDF brand guide

The best input, and the easiest. Read the pages directly with the Read tool's `pages` parameter.

Brand guides **state their hex values as text**. Read them; do not sample the rendering. A PDF's color swatches go through the document's color profile, so a sampled pixel can be several points off the stated value, and the stated value is the one the brand actually uses.

What to look for, in order:

1. The color section — usually names, hex, and often intended use ("primary", "for CTAs only", "never on body text").
2. **The usage rules.** Guides frequently say which color leads and which are secondary. That answers the accent question outright, and it is the answer the user's brand team already agreed on.
3. Typography — families, weights, and any stated hierarchy.
4. Any accessibility section. Some guides already state which pairings are approved, which saves you the argument.

Read the usage prose, not just the swatches. "Coral is reserved for emphasis" is worth more than the hex.

## Website

```bash
python3 scripts/extract_site_theme.py https://example.com --out /tmp/brand.json
```

Uses Playwright to read **computed styles** off real elements — body color and background, heading colors, link color, button background and text, card and surface backgrounds, and the font families actually resolved.

Computed styles beat pixel sampling for two reasons: they give exact declared values rather than antialiased averages, and they carry the element's role with them. Knowing a color is *the link color* is most of the mapping decision.

Notes:

- Pass two or three pages if the site has them — a marketing home page and a docs or app page reveal different parts of the palette.
- Sites in a dark mode by default will yield a dark ramp. Confirm which mode the user wants themed.
- The script degrades with a clear message if Playwright is not installed, exactly like the other renderer scripts.

## Screenshot or logo

**Look at the image directly.** Vision needs no dependency and is better than pixel-frequency quantization at the question that actually matters — which color means "look here" versus which color merely covers the most area. A quantizer returns the background.

Read out:

- The dominant surface and its temperature (is that white warm or cool?).
- The text colors, and whether headings differ from body.
- The one color used for emphasis, links, or calls to action. This is your accent candidate.
- Border and divider treatment — hairline, heavy, or none.
- Corner radius.

State your readings as hex values and say they are read from an image, so the user knows to correct them. A screenshot has been through compression and a display profile; treat every value as approximate until confirmed. If exactness matters, ask for the brand guide or the site.

## Hex values

If the user simply says "our blue is `#0B5FFF`", go straight to mapping. Ask only for what mapping actually needs and the brand has not supplied: a dark neutral for ink, a light neutral for paper, and whether the brand defines status colors.

## What to capture beyond color

A theme that changes only color is not a theme — `core/tokens.md` is explicit. Capture:

- **Typography** — display, body, and mono families, with real fallbacks. Ask about licensing before planning to load a font.
- **Corner radius** — read it off real UI, keep it in the 0–8px band.
- **Border character** — hairline versus solid, and how strong dividers are.
- **Temperature** — whether the neutrals lean warm or cool. This carries a surprising amount of brand identity and costs nothing.

## The report to show the user

Before mapping, show what you found and let them correct it:

```
From brand-guide.pdf:
  primary    #0B5FFF   p.4 "Primary — use for calls to action"
  ink        #101828   p.4 "Text"
  slate      #475467   p.4 "Secondary text"
  cloud      #F2F4F7   p.5 "Backgrounds"
  success    #12B76A   p.6
  warning    #F79009   p.6
  error      #F04438   p.6
  display    Söhne     p.9 — licensing not stated, please confirm
  radius     8px       p.12 (buttons)

Not found: mono family, tertiary text color. I will derive both.
```

Then say which one you intend to make the accent and why, before you write anything. That is the decision most worth checking, and the cheapest to change before the file exists.
