#!/usr/bin/env python3
"""Embed WOFF2 fonts into a document as base64 @font-face rules.

    python scripts/inline_fonts.py report.html \
           --font "Manrope:600:fonts/manrope-600.woff2" \
           --font "Geist:400:fonts/geist-400.woff2" \
           --out report-offline.html

Use this when a document must be genuinely self-contained — archived, emailed,
opened offline, or read inside a restricted network. A linked Google Fonts
stylesheet fails closed in all four cases, and the document falls back to system
metrics without saying so.

Base64 costs about 33% over the raw bytes, so **subset first**. A full Latin
variable font is ~30-60KB and encodes to ~40-80KB; unsubsetted CJK will make the
document unusable. Subset with fonttools before running this:

    pip install fonttools brotli
    pyftsubset font.ttf --flavor=woff2 --layout-features='*' \
      --unicodes='U+0000-00FF,U+2018-201D,U+2013-2014,U+00A0' \
      --output-file=font-subset.woff2

Source properly-licensed subsets from Fontsource, but inline the bytes rather
than importing its stylesheet.

Standard library only.
"""

import argparse
import base64
import re
import sys
from pathlib import Path

# Removing the network stylesheet is the point — leaving it means the document
# still reaches out, and the inlining bought nothing.
GOOGLE_LINK_RE = re.compile(
    r'[ \t]*<link[^>]*fonts\.(?:googleapis|gstatic)\.com[^>]*>[ \t]*\n?', re.IGNORECASE
)
PRECONNECT_RE = re.compile(
    r'[ \t]*<link[^>]*rel="preconnect"[^>]*fonts\.[^>]*>[ \t]*\n?', re.IGNORECASE
)

WARN_BYTES = 120_000


def face(family: str, weight: str, path: Path) -> str:
    raw = path.read_bytes()
    if len(raw) > WARN_BYTES:
        print(
            f"warning: {path.name} is {len(raw):,} bytes — subset it before "
            f"embedding, or the document will carry ~{int(len(raw) * 1.33):,} "
            "bytes of base64 for this face alone",
            file=sys.stderr,
        )
    b64 = base64.b64encode(raw).decode("ascii")
    return (
        f"@font-face {{\n"
        f"  font-family: '{family}';\n"
        f"  font-weight: {weight};\n"
        f"  font-style: normal;\n"
        f"  font-display: swap;\n"
        f"  src: url(data:font/woff2;base64,{b64}) format('woff2');\n"
        f"}}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    parser.add_argument(
        "--font",
        action="append",
        default=[],
        metavar="FAMILY:WEIGHT:PATH",
        help="repeatable, e.g. 'Manrope:600:fonts/manrope-600.woff2'",
    )
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--keep-links",
        action="store_true",
        help="do not strip the Google Fonts <link> tags (rarely what you want)",
    )
    args = parser.parse_args()

    if not args.html.is_file():
        sys.exit(f"not found: {args.html}")
    if not args.font:
        sys.exit("no --font given; nothing to inline")

    faces = []
    for spec in args.font:
        parts = spec.split(":")
        if len(parts) != 3:
            sys.exit(f'bad --font "{spec}", expected FAMILY:WEIGHT:PATH')
        family, weight, raw_path = parts
        path = Path(raw_path)
        if not path.is_file():
            sys.exit(f"font file not found: {path}")
        faces.append(face(family, weight, path))

    html = args.html.read_text(encoding="utf-8")

    if not args.keep_links:
        html, n_link = GOOGLE_LINK_RE.subn("", html)
        html, n_pre = PRECONNECT_RE.subn("", html)
        if n_link or n_pre:
            print(f"removed {n_link + n_pre} external font link(s)", file=sys.stderr)

    block = "<style>\n" + "\n".join(faces) + "\n</style>\n"

    # Ahead of the first <style> so the token stacks can already name these
    # families; falling back to </head> if the document has none.
    if "<style>" in html:
        html = html.replace("<style>", block + "<style>", 1)
    elif "</head>" in html:
        html = html.replace("</head>", block + "</head>", 1)
    else:
        sys.exit("could not find a <style> block or </head> to insert into")

    if args.out:
        args.out.write_text(html, encoding="utf-8")
        print(
            f"wrote {args.out} ({len(html):,} bytes, {len(faces)} face(s) embedded)",
            file=sys.stderr,
        )
    else:
        sys.stdout.write(html)


if __name__ == "__main__":
    main()
