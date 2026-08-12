# Verifying a brand theme

In order. Each step catches something the previous one cannot.

## 1. Audit

```bash
python3 scripts/audit_theme.py path/to/theme.css
```

Checks token completeness against `core/tokens.md`, contrast on every pair that carries text, the one-accent rule, the accent's hue distance from the status colors and from the other themes, and the dark-theme print rule. Non-zero exit on error.

**Errors** must be fixed. **Warnings** must be shown to the user, not silently accepted — that is the difference between an audit and a rubber stamp.

Two warnings you will likely see and what they mean:

- *`--soft` below 4.5* — `--soft` carries eyebrows and metadata, which is small text, so 4.5 is the standard. Every shipped light theme sits near 3.8, so this is advisory rather than failing. If the brand can afford a darker tertiary, take it.
- *accent close to another theme's accent* — not a defect, but the two themes will be hard to tell apart in a thumbnail or a gallery.

## 2. Grayscale

Desaturate a rendered document — screenshot and remove color, or print without color.

The focal bar must still be the focal bar. If the accent was distinguished from the comparison fill only by hue, it disappears here, and so does every chart's point. `core/base.css` strokes focal marks as well as filling them for this reason; if you have overridden that, check it.

## 3. Print a real document

```bash
python3 scripts/build_document.py templates/document.html --theme <brand> --out /tmp/report.html
node scripts/export_pdf.mjs /tmp/report.html --out /tmp/report.pdf
```

Then **open the PDF and read it.** Page count proves nothing.

Check the title block survives, charts are not clipped, table headers repeat, and the methodology block is readable — that last one is where inverted panels go wrong.

**If the theme is dark, this step is mandatory rather than advisable.** `core/print.css` flattens surfaces to white but deliberately leaves the ink ramp alone, so a dark theme without its own `@media print` block prints near-white text on white paper with invisible hairlines. `core/themes/console-violet.css` is the worked example of the fix, and `audit_theme.py` fails a dark theme that omits it.

## 4. Preview beside the shipped themes

Add a panel to `templates/themes.html` and build it:

```bash
python3 scripts/build_document.py templates/themes.html --theme <brand> --out /tmp/themes.html
```

This answers a question no measurement can: does the theme look like a member of this system, or like a different system wearing its layout? Identical markup in every panel, so any difference you see is the theme.

Show the user. It is the fastest way for them to say "the accent is too loud" while that is still cheap to change.

## 5. Responsive and mobile

Check at desktop, tablet, and mobile widths. Brand themes with large radii or heavy borders degrade worst at narrow widths, where chrome takes proportionally more of the screen.

## 6. Repository checks, if the theme lives in this repo

```bash
python3 scripts/validate_repository.py .
python3 -m unittest discover -s tests
```

The validator adds the theme's colors to the known palette, so a hex from this theme appearing in a component file will now be reported as a token leak rather than an unknown color — which is the behavior you want.

## The checklist

The one at the bottom of `core/themes/brand-template.css`, with the mechanical items marked:

- [ ] Every TODO replaced.
- [x] `--ink` on `--surface` meets AA — *audit_theme.py*
- [x] `--muted` on `--surface` readable — *audit_theme.py*
- [x] `--accent-ink` on `--accent` meets AA — *audit_theme.py*
- [x] `--method-ink` and `--method-muted` readable on `--method-bg` — *audit_theme.py*
- [x] Exactly one accent, no brand secondaries wired in — *audit_theme.py*
- [ ] Every chart parses in grayscale — step 2, by eye
- [ ] Print produces a clean PDF — step 3, by eye
- [ ] Checked at desktop, mobile, and print widths — step 5
- [ ] Typography and border character differ, not just color
- [ ] Provenance recorded for every value
