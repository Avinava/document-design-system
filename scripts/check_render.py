#!/usr/bin/env python3
"""Render pages in a real browser and check that every figure stays in bounds.

    uv venv && uv pip install -r requirements-authoring.txt
    uv run playwright install chromium
    uv run python scripts/check_render.py                       # every examples/*.html
    uv run python scripts/check_render.py examples/estimate.html
    uv run python scripts/check_render.py --root site site      # a built directory

check_diagrams.py reads coordinates and estimates text width. This script
measures what a browser actually lays out, with the theme's real fonts, so it
catches what estimation cannot: a label that fits at 0.6em per character but
not in the theme's typeface, or a page whose figure pushes the layout sideways
on a phone.

Each page is loaded once, then checked at three widths — desktop (1280),
phone (390) and print (the printable width of the page's own @page rule,
under print media) — under every theme in
core/themes/ except the brand template, swapped in place by setting
data-theme on the root. Dark is a theme here, not a mode, so the swap covers
it. For each combination:

    page-scroll     the page does not scroll horizontally
    figure-box      every figure <svg> has a non-zero box
    text-bounds     every SVG <text> bounding box stays inside its viewBox
    table-clip      a .table-scroll whose table is wider than it can scroll

Exit status 1 when any check fails, 2 when Chromium is not installed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from _serve import serve  # noqa: E402
from pins import REPO_PYTHON_HINT  # noqa: E402

THEMES_DIR = ROOT / "core" / "themes"
SKIP_THEMES = {"brand-template"}

# name -> (viewport width, viewport height, media). A width of None means
# "the printable width of the page's own @page rule": A4 portrait with the
# core/print.css margins is 688px; a deck's 1280px page has no margin.
MODES = {
    "1280": (1280, 900, "screen"),
    "390": (390, 844, "screen"),
    "print": (None, 1123, "print"),
}

PAGE_WIDTH = r"""
() => {
  const px = (v) => {
    const m = /^(-?[\d.]+)(px|mm|cm|in)?$/.exec(String(v).trim());
    if (!m) return null;
    return ({px: 1, mm: 96 / 25.4, cm: 96 / 2.54, in: 96})[m[2] || 'px'] * parseFloat(m[1]);
  };
  const named = {a4: [210, 297], a3: [297, 420], letter: [215.9, 279.4]};
  let rule = null;
  const walk = (rules) => {
    for (const r of rules) {
      if (r.type === CSSRule.PAGE_RULE) rule = r;
      else if (r.cssRules) walk(r.cssRules);
    }
  };
  for (const sheet of document.styleSheets) {
    try { walk(sheet.cssRules); } catch (e) { /* cross-origin font sheet */ }
  }
  let width = 210 * 96 / 25.4, left = 0, right = 0;
  if (rule) {
    const size = (rule.style.getPropertyValue('size') || '').toLowerCase().split(/\s+/).filter(Boolean);
    const landscape = size.includes('landscape');
    const name = size.find((t) => named[t]);
    const dims = size.map(px).filter((v) => v !== null);
    if (name) {
      const [w, h] = named[name];
      width = (landscape ? h : w) * 96 / 25.4;
    } else if (dims.length) {
      width = dims.length > 1 && landscape ? Math.max(dims[0], dims[1]) : dims[0];
    }
    left = px(rule.style.getPropertyValue('margin-left') || '0') || 0;
    right = px(rule.style.getPropertyValue('margin-right') || '0') || 0;
  }
  return Math.round(width - left - right);
}
"""

TOLERANCE = 1.0  # CSS px / user units; sub-pixel rounding is not a defect

MEASURE = """
(tol) => {
  const out = [];
  const doc = document.documentElement;
  if (doc.scrollWidth > doc.clientWidth + tol) {
    out.push(['page-scroll', `page is ${doc.scrollWidth}px wide in a ${doc.clientWidth}px viewport`]);
  }
  const label = (svg) => {
    const t = svg.querySelector('title');
    return t ? `"${t.textContent.trim().slice(0, 48)}"` : (svg.getAttribute('aria-label') || '<svg>').slice(0, 48);
  };
  const visible = (el) => el.checkVisibility ? el.checkVisibility() : el.getClientRects().length > 0;
  for (const svg of document.querySelectorAll('svg')) {
    if (svg.parentElement && svg.parentElement.closest('svg')) continue;   // nested
    if (!visible(svg)) continue;
    const r = svg.getBoundingClientRect();
    const isFigure = svg.closest('figure, .system-map, .diagram-scroll, .chart-frame, .frame');
    if (isFigure && (r.width < 1 || r.height < 1)) {
      out.push(['figure-box', `${label(svg)} renders at ${r.width.toFixed(1)}×${r.height.toFixed(1)}`]);
      continue;
    }
    const vb = svg.viewBox && svg.viewBox.baseVal;
    if (!vb || !vb.width || !vb.height) continue;
    const rootInv = svg.getScreenCTM() && svg.getScreenCTM().inverse();
    if (!rootInv) continue;
    for (const text of svg.querySelectorAll('text')) {
      if (text.closest('defs, marker, clipPath, mask, pattern, symbol')) continue;
      if (!text.textContent.trim()) continue;
      let box;
      try { box = text.getBBox(); } catch (e) { continue; }
      if (!box.width && !box.height) continue;
      const m = rootInv.multiply(text.getScreenCTM());
      const pts = [[box.x, box.y], [box.x + box.width, box.y],
                   [box.x, box.y + box.height], [box.x + box.width, box.y + box.height]]
        .map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
      const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
      const x0 = Math.min(...xs), x1 = Math.max(...xs), y0 = Math.min(...ys), y1 = Math.max(...ys);
      if (x0 < vb.x - tol || y0 < vb.y - tol || x1 > vb.x + vb.width + tol || y1 > vb.y + vb.height + tol) {
        out.push(['text-bounds', `${label(svg)}: text "${text.textContent.trim().slice(0, 40)}" spans ` +
          `(${x0.toFixed(1)},${y0.toFixed(1)})–(${x1.toFixed(1)},${y1.toFixed(1)}) outside viewBox ` +
          `${vb.x} ${vb.y} ${vb.width} ${vb.height}`]);
      }
    }
  }
  for (const wrap of document.querySelectorAll('.table-scroll')) {
    if (!visible(wrap)) continue;
    const overflow = getComputedStyle(wrap).overflowX;
    const scrolls = overflow === 'auto' || overflow === 'scroll';
    const wrapBox = wrap.getBoundingClientRect();
    for (const child of wrap.children) {
      const box = child.getBoundingClientRect();
      if (box.right > wrapBox.right + tol && !scrolls) {
        out.push(['table-clip', `table ${box.width.toFixed(0)}px wide spills from a ` +
          `${wrapBox.width.toFixed(0)}px .table-scroll that cannot scroll (overflow-x: ${overflow})`]);
      }
    }
  }
  return out;
}
"""


class BrowserMissing(RuntimeError):
    """Chromium is not installed for this Playwright; exit 2, not a check failure."""


def themes() -> dict[str, str]:
    return {
        p.stem: p.read_text(encoding="utf-8")
        for p in sorted(THEMES_DIR.glob("*.css"))
        if p.stem not in SKIP_THEMES
    }


def theme_fonts() -> list[str]:
    """Each theme's web-font stylesheet, so a swapped theme measures in its own type."""
    try:
        from build_examples import FONTS
    except ImportError:
        return []
    return sorted(set(FONTS.values()))


def collect(args: list[str], root: Path) -> list[Path]:
    if not args:
        return sorted((ROOT / "examples").glob("*.html"))
    pages: list[Path] = []
    for raw in args:
        p = Path(raw)
        if not p.is_absolute():
            p = (Path.cwd() / p).resolve()
        if p.is_dir():
            pages.extend(sorted(p.glob("*.html")))
        elif p.is_file():
            pages.append(p)
        else:
            sys.exit(f"check_render: no such page or directory: {raw}")
    for p in pages:
        try:
            p.relative_to(root)
        except ValueError:
            sys.exit(f"check_render: {p} is outside the served root {root}; pass --root")
    return pages


def check(pages: list[Path], root: Path, only_themes: list[str] | None) -> list[str]:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright

    css = themes()
    if only_themes:
        unknown = sorted(set(only_themes) - set(css))
        if unknown:
            sys.exit(f"check_render: unknown theme(s): {', '.join(unknown)}")
        css = {k: v for k, v in css.items() if k in only_themes}
    fonts = theme_fonts()
    failures: list[str] = []
    httpd, base = serve(root)
    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch()
            except PlaywrightError as exc:
                first = str(exc).strip().splitlines()[0]
                raise BrowserMissing(f"{first}\n  run: playwright install chromium") from None
            context = browser.new_context()
            for page_path in pages:
                rel = page_path.relative_to(root).as_posix()
                page = context.new_page()
                page.goto(f"{base}/{rel}", wait_until="networkidle")
                # Every theme's tokens and fonts, so swapping data-theme
                # restyles the page exactly as a build under that theme would.
                for href in fonts:
                    page.add_style_tag(url=href)
                page.add_style_tag(content="\n".join(css.values()))
                page.evaluate("document.fonts.ready")
                original = page.evaluate("document.documentElement.getAttribute('data-theme')")
                seen: set[str] = set()
                for theme in css:
                    page.evaluate("(t) => document.documentElement.setAttribute('data-theme', t)", theme)
                    page.evaluate("document.fonts.ready")
                    for mode, (w, h, media) in MODES.items():
                        if w is None:
                            w = page.evaluate(PAGE_WIDTH)
                        page.set_viewport_size({"width": w, "height": h})
                        page.emulate_media(media=media)
                        for rule, message in page.evaluate(MEASURE, TOLERANCE):
                            key = f"{rel} [{mode}] {rule}: {message}"
                            if key in seen:
                                continue
                            seen.add(key)
                            failures.append(f"{rel} [{theme} @ {mode}] {rule}: {message}")
                if original is not None:
                    page.evaluate("(t) => document.documentElement.setAttribute('data-theme', t)", original)
                page.close()
                print(f"  {rel}", file=sys.stderr)
            browser.close()
    finally:
        httpd.shutdown()
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Render pages and check figures stay in bounds.")
    parser.add_argument("pages", nargs="*", help="HTML files or directories (default: examples/*.html)")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="directory to serve; pages must sit inside it (default: the repository)")
    parser.add_argument("--theme", action="append", help="limit to one theme (repeatable)")
    args = parser.parse_args()

    try:
        import playwright  # noqa: F401
    except ImportError:
        sys.exit(
            "playwright is required.\n"
            f"  {REPO_PYTHON_HINT}\n"
            "It is an authoring-time dependency only."
        )

    root = args.root.resolve()
    pages = collect(args.pages, root)
    if not pages:
        sys.exit("check_render: no pages to check")
    try:
        failures = check(pages, root, args.theme)
    except BrowserMissing as exc:
        print(f"check_render: {exc}", file=sys.stderr)
        return 2
    for line in failures:
        print(line)
    combos = len(pages) * len(MODES) * (len(args.theme) if args.theme else len(themes()))
    if failures:
        print(f"\n{len(failures)} failure(s) across {combos} page renders", file=sys.stderr)
        return 1
    print(f"{combos} page renders clean ({len(pages)} pages × {len(MODES)} widths × themes)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
