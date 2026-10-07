#!/usr/bin/env python3
"""Build the GitHub Pages site into site/.

    python scripts/build_examples.py
    python scripts/build_site.py

Homepage is templates/site.html (the whole system). The thirty-four-type
gallery is types.html. Example documents are copied next to them.
Screenshot paths on the homepage use the @@SHOT marker.

    python scripts/build_site.py --check
writes to a temp dir and asserts the split, then deletes it.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
SHOTS = ROOT / "docs" / "screenshots"
ASSETS = ROOT / "assets"

sys.path.insert(0, str(ROOT / "scripts"))
import catalog  # noqa: E402
from build_document import build  # noqa: E402
from build_examples import assemble_docs_gallery  # noqa: E402

# Where each published copy's fixed back-link leads: (href, label, aria-label).
BACK_TO_TYPES = ("types.html", "← Patterns", "Back to document patterns")
BACK_TO_HOME = ("index.html", "← Home", "Back to the home page")

HTML_KEEP = {
    "inventory-report.html": BACK_TO_HOME,
    "capacity-deck.html": BACK_TO_HOME,
    "gallery-light.html": BACK_TO_HOME,
    "gallery-dark.html": BACK_TO_HOME,
    "themes-light.html": BACK_TO_HOME,
    "themes-dark.html": BACK_TO_HOME,
    "proposal-horizon.html": BACK_TO_TYPES,
    "proposal-coral.html": BACK_TO_TYPES,
    "brand.html": BACK_TO_HOME,
    "mulesoft.html": BACK_TO_TYPES,
}

# Local targets of src/href/srcset attributes; external, data: and mailto: URLs
# and in-page anchors are not site files.
LOCAL_REF = re.compile(r'(?:src|href|srcset)="(?!https?:|mailto:|data:|#)([^"\s]+)')

HOME_MUST_CONTAIN = (
    "src=\"assets/banner.svg\"",
    "/plugin marketplace add Avinava/document-design-system",
    "href=\"types.html\"",
    "href=\"capacity-deck.html\"",
    "href=\"inventory-report.html\"",
    "href=\"gallery-light.html\"",
    "href=\"themes-light.html\"",
    "analytical-document-design",
    "presentation-design",
    "writing-documents",
    "brand-theme-design",
    "diagram-design",
    "chart-design",
    "href=\"proposal-horizon.html\"",
    "href=\"proposal-coral.html\"",
    "href=\"brand.html\"",
    "horizon",
    'class="pattern-map"',
    'href="types.html#incident"',
    'href="types.html#plan"',
    'href="types.html#assurance"',
    'href="types.html#brief"',
    "Thirty-four types",
)


def write_page_copy(src: Path, dest: Path, back: tuple[str, str, str]) -> None:
    """Copy an assembled page and add Pages-only navigation affordances."""
    html = src.read_text(encoding="utf-8")
    html = html.replace(
        "</head>",
        '<link rel="icon" href="assets/banner.svg" type="image/svg+xml">\n</head>',
        1,
    )
    # Screenshots live in docs/screenshots/ in the repository and in
    # screenshots/ on Pages, so a repository-relative image path would break.
    html = html.replace("../docs/screenshots/", "screenshots/")
    back_href, back_label, back_aria = back
    control = (
        '<style>.site-back{position:fixed;z-index:20;top:12px;left:12px;'
        'padding:.45rem .7rem;border:1px solid var(--rule-strong);border-radius:999px;'
        'background:var(--paper);color:var(--ink);font:600 .72rem/1 var(--mono);'
        'text-decoration:none;box-shadow:0 2px 12px color-mix(in srgb,var(--ink) 10%,transparent)}'
        '.site-back:focus-visible{outline:3px solid var(--accent);outline-offset:2px}'
        # Narrow screens have no free gutter, so the control joins the flow
        # there instead of covering the page's first line.
        '@media(max-width:900px){.site-back{position:static;display:inline-block;margin:12px 0 0 16px}}'
        '@media print{.site-back{display:none}}</style>\n'
        f'<a class="site-back" href="{back_href}" aria-label="{back_aria}">{back_label}</a>\n'
    )
    html = html.replace("<body>", "<body>\n" + control, 1)
    dest.write_text(html, encoding="utf-8")


def assemble_home(shot_prefix: str, dest: Path) -> None:
    raw = (ROOT / "templates" / "site.html").read_text(encoding="utf-8")
    filled = raw.replace("@@SHOT", shot_prefix)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(filled)
        tmp_path = Path(tmp.name)
    try:
        assembled = build(tmp_path, "editorial-coral")
    finally:
        tmp_path.unlink(missing_ok=True)
    if "@@INLINE" in assembled or "@@SHOT" in assembled:
        sys.exit("unresolved marker in site homepage")
    dest.write_text(assembled, encoding="utf-8")
    try:
        shown = dest.relative_to(ROOT)
    except ValueError:
        shown = dest
    print(f"  {shown} ({len(assembled):,} bytes)")


def populate(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shots = dest / "screenshots"
    shots.mkdir(exist_ok=True)
    for png in sorted(SHOTS.glob("*.png")):
        shutil.copy2(png, shots / png.name)
    thumb_source = SHOTS / "thumbs"
    if thumb_source.is_dir():
        shutil.copytree(thumb_source, shots / "thumbs")

    assets = dest / "assets"
    assets.mkdir(exist_ok=True)
    banner = ASSETS / "banner.svg"
    if banner.is_file():
        shutil.copy2(banner, assets / "banner.svg")

    for slug in catalog.TYPES:
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        write_page_copy(src, dest / f"{slug}.html", BACK_TO_TYPES)

    for name, back in HTML_KEEP.items():
        src = EX / name
        if src.is_file():
            write_page_copy(src, dest / name, back)

    assemble_home("screenshots", dest / "index.html")
    assemble_docs_gallery(
        "screenshots/thumbs",
        dest / "types.html",
        include_skills=False,
        types_href="types.html",
    )
    (dest / ".nojekyll").write_text("", encoding="utf-8")


def check_built(dest: Path) -> None:
    index = dest / "index.html"
    types = dest / "types.html"
    if not index.is_file():
        sys.exit("site index failed to assemble")
    if not types.is_file():
        sys.exit("site types.html failed to assemble")
    home = index.read_text(encoding="utf-8")
    gallery = types.read_text(encoding="utf-8")
    if "@@INLINE" in home or "@@SHOT" in home:
        sys.exit("unresolved marker in site index")
    if "@@INLINE" in gallery:
        sys.exit("unresolved marker in types.html")
    if re.search(r'<img[^>]+src="\.\./docs/screenshots', home):
        sys.exit("homepage still points at ../docs/screenshots")
    if re.search(r'<img[^>]+src="\.\./docs/screenshots', gallery):
        sys.exit("types.html still points at ../docs/screenshots")
    for needle in HOME_MUST_CONTAIN:
        if needle not in home:
            sys.exit(f"homepage missing {needle!r}")
    for slug in catalog.TYPES:
        if f'href="{slug}.html"' not in gallery:
            sys.exit(f"types.html missing {slug}.html")
        doc = (dest / f"{slug}.html").read_text(encoding="utf-8")
        if 'class="site-back"' not in doc or 'href="assets/banner.svg"' not in doc:
            sys.exit(f"{slug}.html missing Pages navigation or favicon")
        if not (dest / "screenshots" / "thumbs" / f"{slug}.png").is_file():
            sys.exit(f"site missing thumbnail for {slug}")
    for pattern in catalog.PATTERNS:
        if f'id="{pattern}"' not in gallery:
            sys.exit(f"types.html missing {pattern} pattern")
    if 'loading="lazy"' not in gallery or "screenshots/thumbs" not in gallery:
        sys.exit("types.html must use lazy, lightweight thumbnails")
    for needle in ("Find by engagement stage", "Common names, canonical owners", "id=\"profiles\""):
        if needle not in gallery:
            sys.exit(f"types.html missing consultancy navigation {needle!r}")
    if '<section class="group">\n  <h2>The skills</h2>' in gallery:
        sys.exit("types.html should not repeat the six-skill strip")
    for name, (back_href, _, _) in HTML_KEEP.items():
        page = dest / name
        if not page.is_file():
            sys.exit(f"site missing {name}")
        if f'class="site-back" href="{back_href}"' not in page.read_text(encoding="utf-8"):
            sys.exit(f"{name} has no way back to {back_href}")
    for page in sorted(dest.glob("*.html")):
        for ref in LOCAL_REF.findall(page.read_text(encoding="utf-8")):
            target = ref.split("#")[0].split("?")[0]
            if target and not (dest / target).exists():
                sys.exit(f"{page.name} refers to {ref}, which is not in the published site")
    print(f"ok: {index.stat().st_size:,} bytes homepage, {types.stat().st_size:,} bytes types")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="assemble into a temp dir and exit (CI)",
    )
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            populate(dest)
            check_built(dest)
        return

    dest = ROOT / "site"
    if dest.exists():
        shutil.rmtree(dest)
    populate(dest)
    check_built(dest)
    print(f"wrote {dest.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
