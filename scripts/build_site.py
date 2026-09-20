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
from build_document import build  # noqa: E402
from build_examples import LONGFORM, assemble_docs_gallery  # noqa: E402

HTML_KEEP = {
    "inventory-report.html",
    "capacity-deck.html",
    "gallery-light.html",
    "gallery-dark.html",
    "themes-light.html",
    "themes-dark.html",
    "proposal-horizon.html",
    "proposal-coral.html",
    "brand.html",
    "mulesoft.html",
}

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


def write_page_copy(src: Path, dest: Path, back_href: str | None = None) -> None:
    """Copy an assembled page and add Pages-only navigation affordances."""
    html = src.read_text(encoding="utf-8")
    html = html.replace(
        "</head>",
        '<link rel="icon" href="assets/banner.svg" type="image/svg+xml">\n</head>',
        1,
    )
    if back_href:
        control = (
            '<style>.site-back{position:fixed;z-index:20;top:12px;left:12px;'
            'padding:.45rem .7rem;border:1px solid var(--rule-strong);border-radius:999px;'
            'background:var(--paper);color:var(--ink);font:600 .72rem/1 var(--mono);'
            'text-decoration:none;box-shadow:0 2px 12px color-mix(in srgb,var(--ink) 10%,transparent)}'
            '.site-back:focus-visible{outline:3px solid var(--accent);outline-offset:2px}'
            '@media print{.site-back{display:none}}</style>\n'
            f'<a class="site-back" href="{back_href}" aria-label="Back to document patterns">← Patterns</a>\n'
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

    for slug in LONGFORM:
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        write_page_copy(src, dest / f"{slug}.html", "types.html")

    for name in HTML_KEEP:
        src = EX / name
        if src.is_file():
            write_page_copy(
                src,
                dest / name,
                "types.html" if name.startswith("proposal-") or name == "mulesoft.html" else None,
            )

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
    for slug in LONGFORM:
        if f'href="{slug}.html"' not in gallery:
            sys.exit(f"types.html missing {slug}.html")
        doc = (dest / f"{slug}.html").read_text(encoding="utf-8")
        if 'class="site-back"' not in doc or 'href="assets/banner.svg"' not in doc:
            sys.exit(f"{slug}.html missing Pages navigation or favicon")
        if not (dest / "screenshots" / "thumbs" / f"{slug}.png").is_file():
            sys.exit(f"site missing thumbnail for {slug}")
    for pattern in (
        "decision", "record", "contract", "procedure", "learning", "system",
        "incident", "suite", "plan", "assurance", "brief",
    ):
        if f'id="{pattern}"' not in gallery:
            sys.exit(f"types.html missing {pattern} pattern")
    if 'loading="lazy"' not in gallery or "screenshots/thumbs" not in gallery:
        sys.exit("types.html must use lazy, lightweight thumbnails")
    for needle in ("Find by engagement stage", "Common names, canonical owners", "id=\"profiles\""):
        if needle not in gallery:
            sys.exit(f"types.html missing consultancy navigation {needle!r}")
    if '<section class="group">\n  <h2>The skills</h2>' in gallery:
        sys.exit("types.html should not repeat the six-skill strip")
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
