#!/usr/bin/env python3
"""Build the GitHub Pages gallery into site/.

    python scripts/build_examples.py
    python scripts/build_site.py

Copies committed examples and screenshots, and writes an index that is the
document-type gallery with screenshot paths rewritten for the site root.

    python scripts/build_site.py --check
writes to a temp dir and asserts the index assembled, then deletes it.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
SHOTS = ROOT / "docs" / "screenshots"

sys.path.insert(0, str(ROOT / "scripts"))
from build_examples import assemble_docs_gallery  # noqa: E402

HTML_KEEP = {
    "inventory-report.html",
    "capacity-deck.html",
    "gallery-light.html",
    "gallery-dark.html",
    "themes-light.html",
    "themes-dark.html",
    "index.html",
}


def populate(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shots = dest / "screenshots"
    shots.mkdir(exist_ok=True)
    for png in sorted(SHOTS.glob("*.png")):
        shutil.copy2(png, shots / png.name)

    from build_examples import LONGFORM

    for slug in LONGFORM:
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        shutil.copy2(src, dest / f"{slug}.html")

    for name in HTML_KEEP:
        src = EX / name
        if src.is_file():
            shutil.copy2(src, dest / name)

    assemble_docs_gallery("screenshots", dest / "index.html")


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
            populate(Path(tmp))
            index = Path(tmp) / "index.html"
            if not index.is_file() or "@@INLINE" in index.read_text(encoding="utf-8"):
                sys.exit("site index failed to assemble")
            print(f"ok: {index.stat().st_size:,} bytes")
        return

    dest = ROOT / "site"
    if dest.exists():
        shutil.rmtree(dest)
    populate(dest)
    print(f"wrote {dest.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
