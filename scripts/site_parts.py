#!/usr/bin/env python3
"""Pieces every GitHub Pages page shares: navigation, meta tags, dark mode.

Imported by scripts/build_site.py (index, modules, figures, themes) and
scripts/build_examples.py (the Patterns page, which is also built locally as
examples/index.html). Standard library only. Repository-only.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

SITE_URL = "https://avinava.github.io/document-design-system/"
REPO_URL = "https://github.com/Avinava/document-design-system"
SOCIAL_IMAGE = "screenshots/social-preview.png"
# The mark as a standalone file (literal colours, its own dark mode) for the
# favicon; the navigation draws the same geometry inline on the page's tokens.
FAVICON = "assets/mark.svg"
FAVICON_LINK = f'<link rel="icon" href="{FAVICON}" type="image/svg+xml">'

# The mark (assets/mark.svg): a page whose lines are its reading order, the
# first line in the one accent because the answer leads. On tokens, so it
# inverts with the page's dark palette.
MARK_SVG = (
    '<svg class="mark" viewBox="0 0 32 32" width="22" height="22" aria-hidden="true" focusable="false">'
    '<rect x="0" y="0" width="32" height="32" rx="8" fill="var(--ink)"/>'
    '<rect x="8" y="7" width="12" height="3" rx="1.5" fill="var(--accent)"/>'
    '<rect x="8" y="12.5" width="16" height="3" rx="1.5" fill="var(--paper)"/>'
    '<rect x="8" y="18" width="16" height="3" rx="1.5" fill="var(--paper)"/>'
    '<rect x="8" y="23.5" width="10" height="3" rx="1.5" fill="var(--paper)"/>'
    "</svg>"
)
WORDMARK_TEXT = 'document<span class="hyphen">-</span>design<span class="hyphen">-</span>system'

# Every site page wears one theme so the front door reads as one voice.
# Readers whose system asks for dark get the dark theme's palette, keeping the
# light theme's type so the page does not change family under them.
SITE_THEME = "executive-navy"
DARK_THEME = "console-violet"
DARK_KEEP = re.compile(r"^--(?:display|sans|mono|radius-[a-z]+)$")

# (label, href). The order is the site's reading order.
NAV = (
    ("Story", "index.html"),
    ("Patterns", "types.html"),
    ("Modules", "modules.html"),
    ("Figures", "figures.html"),
    ("Themes", "themes.html"),
    ("GitHub", REPO_URL),
)

# The local Patterns page (examples/index.html) has no homepage or modules
# page beside it, so its navigation names only what exists in examples/.
LOCAL_NAV = (
    ("Patterns", "index.html"),
    ("Figures", "gallery-light.html"),
    ("Themes", "themes-light.html"),
    ("GitHub", REPO_URL),
)

NAV_CSS = """
.site-nav { display: flex; flex-wrap: wrap; align-items: baseline; justify-content: space-between;
  gap: .5rem 1.5rem; padding: 18px 0 14px; border-bottom: 1px solid var(--rule); }
.wordmark { display: inline-flex; align-items: center; gap: .55rem; align-self: center; color: var(--ink);
  font: 600 1rem/1.2 var(--display); letter-spacing: -.015em; text-decoration: none; }
.wordmark .mark { flex: none; display: block; }
.wordmark .hyphen { color: var(--soft); }
.site-nav ul { display: flex; flex-wrap: wrap; gap: .25rem 1.25rem; list-style: none; margin: 0; padding: 0; font-size: .9375rem; }
.site-nav a { color: var(--muted); text-decoration: none; padding: .25rem 0; }
.site-nav a:hover { color: var(--ink); }
.site-nav a[aria-current="page"] { color: var(--ink); box-shadow: inset 0 -2px 0 var(--accent); }
.site-nav a:focus-visible, .site-nav .wordmark:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
@media (max-width: 560px) { .site-nav ul { gap: .15rem 1rem; font-size: .875rem; } }
"""


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def site_nav(current: str | None, links: tuple[tuple[str, str], ...] = NAV) -> str:
    """The site navigation; `current` is the href of the page it sits on."""
    items = []
    for label, href in links:
        here = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{esc(href)}"{here}>{esc(label)}</a></li>')
    home = "index.html" if links is NAV else REPO_URL
    return (
        '<nav class="site-nav" aria-label="Site">\n'
        f'  <a class="wordmark" href="{home}" aria-label="document-design-system">{MARK_SVG}<span>{WORDMARK_TEXT}</span></a>\n'
        f'  <ul>{"".join(items)}</ul>\n'
        "</nav>"
    )


def head_meta(title: str, description: str, page: str) -> str:
    """Description, canonical URL, Open Graph and Twitter tags for one page."""
    url = SITE_URL if page == "index.html" else SITE_URL + page
    image = SITE_URL + SOCIAL_IMAGE
    t, d = esc(title), esc(description)
    return "\n".join((
        f'<meta name="description" content="{d}">',
        '<meta name="color-scheme" content="light dark">',
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="document-design-system">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{d}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{t}">',
        f'<meta name="twitter:description" content="{d}">',
        f'<meta name="twitter:image" content="{image}">',
    ))


def dark_css(root: Path = ROOT) -> str:
    """The dark theme's colour tokens, applied when the reader's system asks for dark.

    Read from the theme file at build time, so the site templates carry no
    colour of their own and the dark palette cannot drift from the theme.
    """
    css = (root / "core" / "themes" / f"{DARK_THEME}.css").read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    block = re.search(r"\{(.*?)\}", css, re.S)
    if not block:
        raise ValueError(f"{DARK_THEME}.css has no rule block")
    decls = []
    for name, value in re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", block.group(1)):
        if not DARK_KEEP.match(name):
            decls.append(f"    {name}: {value.strip()};")
    return (
        f"/* dark palette from core/themes/{DARK_THEME}.css, for prefers-color-scheme: dark */\n"
        "@media screen and (prefers-color-scheme: dark) {\n"
        "  :root[data-theme] {\n    color-scheme: dark;\n"
        + "\n".join(decls)
        + "\n  }\n}"
    )


_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
         "fourteen fifteen sixteen seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def words(n: int) -> str:
    """0–99 as English words: 34 -> 'thirty-four'."""
    if not 0 <= n < 100:
        return str(n)
    if n < 20:
        return _ONES[n]
    tens, ones = divmod(n, 10)
    return _TENS[tens] + (f"-{_ONES[ones]}" if ones else "")


# Layout every site page shares. Tokens only: the validator rejects colour
# literals outside core/themes/.
SHARED_CSS = NAV_CSS + """
.shell { max-width: 1180px; margin: 0 auto; padding: 0 32px 72px; }
.skip-link { position: absolute; left: -9999px; }
.skip-link:focus { left: 1rem; top: 1rem; z-index: 10; padding: .6rem .8rem; background: var(--surface); color: var(--ink); }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
.site-title { font-family: var(--display); font-weight: 600; font-size: clamp(2.35rem, 5.4vw, 4.1rem);
  line-height: 1.03; letter-spacing: -.035em; margin: 0 0 1.25rem; max-width: 17ch; text-wrap: balance; }
.site-lead { font-size: 1.1875rem; line-height: 1.55; color: var(--muted); max-width: 58ch; margin: 0 0 1.25rem; }
.site-section { padding-top: 88px; scroll-margin-top: 8px; }
.site-section > h2 { font-size: clamp(1.65rem, 3.2vw, 2.4rem); line-height: 1.1; letter-spacing: -.025em;
  margin: 0 0 .75rem; max-width: 24ch; text-wrap: balance; }
.site-section > .site-lead { margin-bottom: 2rem; }
.chooser { width: 100%; border-collapse: collapse; font-size: 1rem; }
.chooser thead th { font: 500 .8125rem/1.3 var(--sans); color: var(--soft); border-bottom: 1px solid var(--rule-strong); padding: 0 1rem .6rem 0; }
.chooser tbody tr:nth-child(even) { background: none; }
.chooser tbody th, .chooser td { border-bottom: 1px solid var(--rule); padding: .85rem 1rem .85rem 0; vertical-align: baseline; }
.chooser tbody th { font: 500 1.0625rem/1.4 var(--display); color: var(--ink); letter-spacing: -.005em; width: 44%; }
.chooser td:nth-child(2) { width: 9rem; white-space: nowrap; }
.chooser td:last-child { color: var(--muted); font-size: .9375rem; }
.chooser td:last-child a { color: var(--muted); text-decoration-color: var(--rule-strong); }
.chooser td:last-child a:hover { color: var(--ink); }
.pattern-chip { display: inline-block; padding: .2rem .6rem; border-radius: 999px; background: var(--accent-tint);
  color: var(--ink); font: 600 .875rem/1.3 var(--sans); text-decoration: none; }
.pattern-chip:hover { background: var(--accent); color: var(--accent-ink); }
.site-foot { margin-top: 96px; padding-top: 18px; border-top: 1px solid var(--rule); color: var(--muted); font-size: .875rem; }
.site-foot p { max-width: 80ch; margin: 0 0 .4rem; }
@media (max-width: 760px) {
  .shell { padding: 0 16px 48px; }
  .site-section { padding-top: 64px; }
  .site-lead { font-size: 1.0625rem; }
  .chooser thead { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
  .chooser, .chooser tbody, .chooser tr, .chooser th, .chooser td { display: block; width: auto; }
  .chooser tr { padding: .9rem 0; border-bottom: 1px solid var(--rule); }
  .chooser tbody th, .chooser td { border: 0; padding: 0; width: auto; }
  .chooser td:nth-child(2) { margin: .45rem 0 .3rem; }
}
"""


def chooser(pattern_href, preset_href, caption: str) -> str:
    """The reader-question router (type-index.md) as a table.

    `pattern_href(name)` and `preset_href(slug)` give each link's target, so
    the homepage and the Patterns page can point at different anchors.
    """
    rows = []
    for q in catalog.QUESTIONS:
        presets = ", ".join(
            f'<a href="{esc(preset_href(slug))}">{esc(catalog.TYPES[slug].title)}</a>' for slug in q.presets
        )
        rows.append(
            f'<tr><th scope="row">{esc(q.question)}</th>'
            f'<td><a class="pattern-chip" href="{esc(pattern_href(q.pattern))}">{esc(q.pattern.capitalize())}</a></td>'
            f"<td>{presets}</td></tr>"
        )
    return (
        f'<table class="chooser">\n<caption class="sr-only">{esc(caption)}</caption>\n'
        '<thead><tr><th scope="col">The reader asks</th><th scope="col">Pattern</th>'
        '<th scope="col">Presets in that pattern</th></tr></thead>\n<tbody>\n'
        + "\n".join(rows)
        + "\n</tbody>\n</table>"
    )
