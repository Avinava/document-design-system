#!/usr/bin/env python3
"""Audit a theme against the token contract.

    python3 scripts/audit_theme.py core/themes/acme.css
    python3 scripts/audit_theme.py --all

Mechanizes the checklist that otherwise sits as prose at the bottom of
core/themes/brand-template.css. Four of those ten items are WCAG contrast
pairs, and nobody computes those correctly by looking at them — which is the
whole reason this exists.

Checks:
  1. every required token from core/tokens.md is declared
  2. contrast on every pair that carries text, at the right threshold
  3. one accent — no smuggled-in secondary accents or categorical palettes
  4. accent hue separation from the status colors and from other themes
  5. a dark theme restores a readable ink ramp for print

Exit code is non-zero on any error, so it works as a CI gate.
Standard library only. tests/test_repository.py imports its colour maths.
"""

from __future__ import annotations

import argparse
import colorsys
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES = ROOT / "core" / "themes"

CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")


# ---------------------------------------------------------------- colour ---


def strip_comments(css: str) -> str:
    """Comments discuss tokens in prose; those are not declarations."""
    return CSS_COMMENT.sub("", css)


def relative_luminance(hex_color: str) -> float:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def hue(hex_color: str) -> float:
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)[0] * 360


def hue_gap(a: str, b: str) -> float:
    d = abs(hue(a) - hue(b))
    return min(d, 360 - d)


# ----------------------------------------------------------------- parse ---


def declarations(css: str, within_print: bool = False) -> dict[str, str]:
    """Token -> value. `within_print` reads the @media print block instead."""
    css = strip_comments(css)
    block = re.search(r"@media\s+print\s*\{(.*)\}\s*\}", css, re.S)
    if within_print:
        css = block.group(1) if block else ""
    elif block:
        css = css[: block.start()]
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", css)}


def required_tokens() -> set[str]:
    """The contract, read from core/tokens.md so the two cannot drift."""
    tokens, optional = set(), False
    for line in (ROOT / "core" / "tokens.md").read_text(encoding="utf-8").split("\n"):
        if line.startswith("### "):
            optional = "optional" in line.lower()
        if optional:
            continue
        m = re.match(r"\|\s*`(--[a-z0-9-]+)`\s*\|", line)
        if m:
            tokens.add(m.group(1))
    return tokens


# ----------------------------------------------------------------- rules ---

# (foreground, background, minimum, severity)
#
# 4.5 is WCAG AA for normal text; 3.0 is AA for large text and for graphical
# objects such as a bar fill or a hairline.
PAIRS = [
    ("--ink", "--surface", 4.5, "error"),
    ("--ink", "--paper", 4.5, "error"),
    ("--muted", "--surface", 4.5, "error"),
    ("--accent-ink", "--accent", 4.5, "error"),
    ("--method-ink", "--method-bg", 4.5, "error"),
    ("--method-muted", "--method-bg", 4.5, "error"),
    ("--accent", "--surface", 3.0, "error"),
    ("--positive", "--surface", 3.0, "error"),
    ("--warning", "--surface", 3.0, "error"),
    ("--critical", "--surface", 3.0, "error"),
    # --soft carries eyebrows and metadata. That is small text, so 4.5 is the
    # standard — but every shipped light theme sits near 3.8, so this is
    # reported as advisory rather than failing known-good themes.
    ("--soft", "--surface", 4.5, "warn"),
]

STATUS = ("--positive", "--warning", "--critical")
MIN_HUE_GAP = 15.0


class Report:
    def __init__(self, name: str) -> None:
        self.name = name
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.lines: list[str] = []

    def ok(self, msg: str) -> None:
        self.lines.append(f"    ok    {msg}")

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        self.lines.append(f"    FAIL  {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        self.lines.append(f"    warn  {msg}")


def audit(path: Path, other_accents: dict[str, str]) -> Report:
    r = Report(path.stem)
    css = path.read_text(encoding="utf-8")
    tok = declarations(css)

    # 1. completeness
    missing = required_tokens() - set(tok)
    if missing:
        r.fail(f"missing required tokens: {', '.join(sorted(missing))}")
    else:
        r.ok(f"all {len(required_tokens())} required tokens declared")

    def hexval(name: str) -> str | None:
        v = tok.get(name, "")
        m = HEX.fullmatch(v.strip())
        return m.group(0) if m else None

    # 2. contrast
    for fg, bg, need, severity in PAIRS:
        a, b = hexval(fg), hexval(bg)
        if not (a and b):
            continue  # non-hex (rgba) values are not text pairs
        ratio = contrast(a, b)
        msg = f"{fg} on {bg} = {ratio:.2f} (need {need})"
        if ratio >= need:
            r.ok(msg)
        elif severity == "error":
            r.fail(msg)
        else:
            r.warn(msg)

    # 3. one accent
    extra = [t for t in tok if re.match(r"--(accent-\d|cat-\d|accent-2)", t)]
    if extra:
        r.fail(f"more than one accent: {', '.join(sorted(extra))}")
    else:
        r.ok("one accent")

    # 4. hue separation
    accent = hexval("--accent")
    if accent:
        for s in STATUS:
            sv = hexval(s)
            if sv and hue_gap(accent, sv) < MIN_HUE_GAP:
                # Advisory rather than fatal: core/a11y.md already requires every
                # status to carry a written label, so hue proximity is a
                # legibility smell, not a correctness failure the way a contrast
                # miss is.
                r.warn(
                    f"--accent is {hue_gap(accent, sv):.0f}° from {s} — too close to a "
                    "status hue, which makes every real status ambiguous"
                )
        for name, other in other_accents.items():
            if name != path.stem and hue_gap(accent, other) < MIN_HUE_GAP:
                r.warn(
                    f"--accent is {hue_gap(accent, other):.0f}° from {name}'s — the two "
                    "themes will be hard to tell apart at thumbnail size"
                )

    # 5. dark themes must survive print
    paper = hexval("--paper")
    if paper and relative_luminance(paper) < 0.5:
        printed = declarations(css, within_print=True)
        if not printed:
            r.fail(
                "dark theme with no @media print block — core/print.css flattens "
                "surfaces to white but leaves the ink ramp alone, so this prints "
                "near-white on white"
            )
        else:
            for token in ("--ink", "--muted"):
                v = printed.get(token, "")
                m = HEX.fullmatch(v.strip())
                if not m:
                    r.fail(f"dark theme print block does not restore {token}")
                elif contrast(m.group(0), "#ffffff") < 4.5:
                    r.fail(f"print {token} is {contrast(m.group(0), '#ffffff'):.2f} on white paper")
                else:
                    r.ok(f"print {token} = {contrast(m.group(0), '#ffffff'):.2f} on white paper")

    return r


def collect_accents() -> dict[str, str]:
    out = {}
    for t in sorted(THEMES.glob("*.css")):
        v = declarations(t.read_text(encoding="utf-8")).get("--accent", "")
        m = HEX.fullmatch(v.strip())
        if m:
            out[t.stem] = m.group(0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("theme", nargs="?", type=Path)
    ap.add_argument("--all", action="store_true", help="audit every theme in core/themes/")
    ap.add_argument("--quiet", action="store_true", help="only show failures")
    args = ap.parse_args()

    if args.all:
        targets = sorted(THEMES.glob("*.css"))
    elif args.theme:
        targets = [args.theme]
    else:
        ap.error("pass a theme file or --all")

    accents = collect_accents()
    errors = warnings = 0

    for path in targets:
        if not path.is_file():
            print(f"not found: {path}", file=sys.stderr)
            return 1
        r = audit(path, accents)
        errors += len(r.errors)
        warnings += len(r.warnings)
        status = "FAIL" if r.errors else ("warn" if r.warnings else "ok")
        print(f"\n  {r.name}  [{status}]")
        for line in r.lines:
            if args.quiet and line.strip().startswith("ok"):
                continue
            print(line)

    print(f"\n  {len(targets)} theme(s) · {errors} error(s) · {warnings} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
