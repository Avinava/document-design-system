#!/usr/bin/env python3
"""Read a site's palette and typography off its computed styles.

    pip install playwright && playwright install chromium
    python3 scripts/extract_site_theme.py https://example.com
    python3 scripts/extract_site_theme.py https://example.com /docs --out brand.json

Computed styles rather than pixel sampling, for two reasons: the values are
exact rather than antialiased averages, and each one arrives with the role it
plays. Knowing a color is *the link color* is most of the mapping decision —
a quantizer would just tell you which color covers the most area, which is
always the background.

Output is a JSON report with provenance for every value, meant to be shown to
the user for correction before anything is mapped. See
skills/brand-theme-design/references/extraction.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter

# Each probe: label -> (selector, css properties to read).
# Chosen to cover the roles the token contract needs, not to be exhaustive.
PROBES = {
    "body": ("body", ["color", "background-color", "font-family", "font-size"]),
    "heading": ("h1, h2", ["color", "font-family", "font-weight"]),
    "link": ("a[href]", ["color"]),
    "button": ("button, .btn, a.button, [role=button]", ["background-color", "color", "border-radius"]),
    "surface": ("main section, article, .card, [class*=card]", ["background-color", "border-color", "border-radius"]),
    "code": ("code, pre", ["font-family"]),
    "muted": ("p small, .text-muted, [class*=muted], footer p", ["color"]),
}

SCRIPT = """
([probes]) => {
  const out = {};
  const seen = {};
  for (const [label, [sel, props]] of probes) {
    const els = [...document.querySelectorAll(sel)].filter(e => {
      const r = e.getBoundingClientRect();
      return r.width > 0 && r.height > 0;
    }).slice(0, 12);
    if (!els.length) continue;
    const vals = {};
    for (const el of els) {
      const cs = getComputedStyle(el);
      for (const p of props) {
        const v = cs.getPropertyValue(p).trim();
        if (!v || v === 'none' || v === 'rgba(0, 0, 0, 0)') continue;
        (vals[p] = vals[p] || []).push(v);
      }
    }
    out[label] = vals;
  }
  return out;
}
"""


def to_hex(css_color: str) -> str:
    """rgb()/rgba() -> #rrggbb. Anything else is returned unchanged."""
    if css_color.startswith("#"):
        return css_color.lower()
    if not css_color.startswith("rgb"):
        return css_color
    nums = [n.strip() for n in css_color[css_color.find("(") + 1 : css_color.find(")")].split(",")]
    try:
        r, g, b = (int(float(n)) for n in nums[:3])
    except ValueError:
        return css_color
    return f"#{r:02x}{g:02x}{b:02x}"


def most_common(values: list[str]) -> tuple[str, int]:
    counts = Counter(values)
    value, n = counts.most_common(1)[0]
    return value, n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("paths", nargs="*", default=[], help="extra paths, e.g. /docs /pricing")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "playwright is not installed.\n"
            "  pip install playwright && playwright install chromium\n"
            "It is an authoring-time dependency only.\n"
            "Alternative: read a screenshot or the brand guide PDF directly — see\n"
            "skills/brand-theme-design/references/extraction.md",
            file=sys.stderr,
        )
        return 1

    base = args.url.rstrip("/")
    urls = [base] + [base + p if p.startswith("/") else f"{base}/{p}" for p in args.paths]
    report: dict[str, dict] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in urls:
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            try:
                page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception as exc:  # noqa: BLE001 — one bad page must not kill the run
                print(f"  skipped {url}: {str(exc).splitlines()[0]}", file=sys.stderr)
                page.close()
                continue
            page.evaluate("document.fonts.ready")
            found = page.evaluate(SCRIPT, [list(PROBES.items())])
            for label, props in found.items():
                for prop, values in props.items():
                    value, n = most_common(values)
                    key = f"{label}.{prop}"
                    # First page wins; later pages only fill gaps, so the home
                    # page's identity is not overwritten by a docs subsite.
                    if key in report:
                        continue
                    report[key] = {
                        "value": to_hex(value) if "color" in prop else value,
                        "raw": value,
                        "seen_on": n,
                        "source": url,
                    }
            page.close()
        browser.close()

    if not report:
        print("nothing extracted — the pages may have failed to load", file=sys.stderr)
        return 1

    out = {
        "urls": urls,
        "note": (
            "Computed styles, not pixel samples. Confirm these with the user before "
            "mapping — only they know which blue is the brand blue and which is a "
            "button state. See skills/brand-theme-design/references/mapping.md"
        ),
        "observations": report,
    }
    text = json.dumps(out, indent=2)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"wrote {args.out} ({len(report)} observations)", file=sys.stderr)
    else:
        print(text)

    print("\n  candidates:", file=sys.stderr)
    for key in ("body.color", "body.background-color", "link.color", "button.background-color"):
        if key in report:
            print(f"    {key:<28} {report[key]['value']}", file=sys.stderr)
    print(
        "\n  The link/button color is usually the accent candidate; body.color is "
        "usually --ink.\n  Neither is automatic — see references/mapping.md.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
