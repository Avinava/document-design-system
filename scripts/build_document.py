#!/usr/bin/env python3
"""Assemble a self-contained HTML document from a template plus core/ CSS.

    python scripts/build_document.py templates/document.html \
           --theme editorial-coral --out report.html

The template carries build markers instead of copied CSS:

    /* @@INLINE core/base.css @@ */
    /* @@INLINE core/themes/${THEME}.css @@ */

so there is exactly one copy of the design system and nothing to keep in sync.
${THEME} resolves to --theme.

Standard library only — no build step, no dependencies.
"""

import argparse
import re
import sys
from pathlib import Path

MARKER = re.compile(r"[ \t]*/\* *@@INLINE +(?P<path>[^ ]+) +@@ *\*/[^\n]*")

REPO_ROOT = Path(__file__).resolve().parent.parent


def resolve(raw: str, theme: str) -> Path:
    return REPO_ROOT / raw.replace("${THEME}", theme)


def build(template: Path, theme: str) -> str:
    html = template.read_text(encoding="utf-8")
    missing: list[str] = []

    def replace(match: re.Match) -> str:
        target = resolve(match.group("path"), theme)
        if not target.is_file():
            missing.append(str(target.relative_to(REPO_ROOT)))
            return match.group(0)
        body = target.read_text(encoding="utf-8").rstrip()
        rel = target.relative_to(REPO_ROOT)
        return f"/* ---- inlined from {rel} ---- */\n{body}"

    out = MARKER.sub(replace, html)

    if missing:
        sys.exit("missing files referenced by @@INLINE markers:\n  " + "\n  ".join(missing))

    # The theme is selected once, on the root element. A document whose
    # data-theme disagrees with its inlined tokens is the confusing kind of
    # broken — it renders, just with the wrong palette.
    out = re.sub(r'(<html[^>]*\sdata-theme=")[^"]*(")', rf"\g<1>{theme}\g<2>", out, count=1)

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("template", type=Path)
    parser.add_argument("--theme", default="editorial-coral")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    themes = {p.stem for p in (REPO_ROOT / "core" / "themes").glob("*.css")}
    if args.theme not in themes:
        sys.exit(
            f'unknown theme "{args.theme}". Available: {", ".join(sorted(themes))}.\n'
            "Never emit a partially themed document — add the theme to core/themes/ first."
        )

    if not args.template.is_file():
        sys.exit(f"template not found: {args.template}")

    result = build(args.template, args.theme)

    if args.out:
        args.out.write_text(result, encoding="utf-8")
        print(f"wrote {args.out} ({len(result):,} bytes, theme: {args.theme})", file=sys.stderr)
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
