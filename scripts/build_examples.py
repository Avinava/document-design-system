#!/usr/bin/env python3
"""Rebuild everything in examples/ from templates, specs, and core/.

    python scripts/build_examples.py

Renders the charts and diagrams, assembles the four example documents, and
inlines each figure into its slot. Committed outputs double as CI fixtures and
as the screenshots in the README, so they need to be reproducible rather than
hand-maintained.

Node renderers are optional: if their dependencies are missing, the existing
committed SVGs are reused and the step is reported as skipped. That keeps the
document build working on a machine with only Python.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
TYPES = ROOT / "templates" / "types"

sys.path.insert(0, str(ROOT / "scripts"))
from build_document import build  # noqa: E402

# figure slug -> (renderer, spec, extra args)
CHARTS = {
    "footprint-by-function": "specs/footprint.json",
    "cohorts-by-year": "specs/cohorts.json",
    "latency-p99": "specs/latency.json",
    # Full-width variant for the deck. A doc-inline chart dropped into a
    # 1280px slide sits in the middle with its labels shrunk to nothing.
    "footprint-by-function-wide": "specs/footprint-wide.json",
}

DIAGRAMS = {
    "ingestion-path": (
        "specs/ingestion.mmd",
        "Ingestion path",
        "Client posts events to the gateway, which enqueues them; the queue acknowledges.",
    ),
}

# output -> (template, theme)
DOCUMENTS = {
    "inventory-report.html": ("document.html", "editorial-coral"),
    "capacity-deck.html": ("deck.html", "executive-navy"),
    # The two images the README swaps with the reader's GitHub theme are built
    # twice, once under a light root theme and once under the dark one. Only
    # these two carry the design argument; the rest render once.
    "gallery-light.html": ("gallery.html", "editorial-coral"),
    "gallery-dark.html": ("gallery.html", "console-violet"),
    "themes-light.html": ("themes.html", "editorial-coral"),
    "themes-dark.html": ("themes.html", "console-violet"),
}

# writing-documents examples: slug -> (theme, contract-layout)
# Bodies live in templates/types/<slug>.html; the shell is templates/longform.html.
LONGFORM = {
    "design-doc": ("field-notes", False),
    "adr": ("field-notes", False),
    "spec": ("field-notes", True),
    "api-contract": ("console-violet", True),
    "architecture": ("field-notes", False),
    "handoff": ("field-notes", False),
    "design-handoff": ("editorial-coral", False),
    "discovery": ("field-notes", False),
    "test-report": ("editorial-coral", True),
    "postmortem": ("console-violet", False),
    "proposal": ("executive-navy", False),
    "runbook": ("console-violet", False),
    "onboarding": ("field-notes", False),
    "tutorial": ("editorial-coral", False),
    "how-to": ("editorial-coral", False),
    "reference": ("console-violet", True),
    "explanation": ("field-notes", False),
    "mulesoft": ("field-notes", False),
}

FONTS = {
    "field-notes": (
        "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700"
        "&family=Source+Code+Pro:wght@400;500;600&display=swap"
    ),
    "editorial-coral": (
        "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700"
        "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
    ),
    "executive-navy": (
        "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700"
        "&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    ),
    "console-violet": (
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700"
        "&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    ),
}

# Figures inlined into the analytical report, in document order.
REPORT_SLOTS = [
    ("<!-- inline the SVG from scripts/render_chart.mjs here -->", "footprint-by-function"),
    ('<div class="chart-frame"></div>', "cohorts-by-year"),
]


def run(cmd: list[str]) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"  skipped: {result.stderr.strip().splitlines()[0] if result.stderr else 'failed'}")
        return False
    return True


def render_figures() -> None:
    print("rendering figures")
    ok = True
    for slug, spec in CHARTS.items():
        ok &= run(["node", "scripts/render_chart.mjs", str(EX / spec), "--out", str(EX / f"{slug}.svg")])
    for slug, (spec, title, desc) in DIAGRAMS.items():
        ok &= run([
            "node", "scripts/render_diagram.mjs", str(EX / spec),
            "--id", slug.split("-")[0], "--title", title, "--desc", desc,
            "--out", str(EX / f"{slug}.svg"),
        ])
    if not ok:
        print("  (reusing committed SVGs — run `npm install beautiful-mermaid "
              "@observablehq/plot jsdom` to re-render)")


def figure(slug: str) -> str:
    path = EX / f"{slug}.svg"
    if not path.is_file():
        sys.exit(f"missing figure: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8").strip()


def _title(body: str) -> str:
    m = re.search(r"<h1>(.*?)</h1>", body, re.S)
    if not m:
        return "Document"
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


def assemble_longform() -> None:
    print("assembling writing-documents examples")
    shell = (ROOT / "templates" / "longform.html").read_text(encoding="utf-8")
    stale = EX / "platform-rfc.html"
    if stale.is_file():
        stale.unlink()

    for slug, (theme, contract) in LONGFORM.items():
        body_path = TYPES / f"{slug}.html"
        if not body_path.is_file():
            sys.exit(f"missing type body: {body_path.relative_to(ROOT)}")
        body = body_path.read_text(encoding="utf-8")
        href = FONTS[theme]
        html = shell.replace("<!-- @@TITLE -->", _title(body), 1)
        html = html.replace(
            "<!-- @@FONTS -->",
            f'<link href="{href}" rel="stylesheet">',
            1,
        )
        html = html.replace("<!-- @@BODY -->", body, 1)
        if contract:
            html = html.replace(
                "<html lang=\"en\"",
                '<html lang="en" data-layout="contract"',
                1,
            )
        with tempfile.NamedTemporaryFile(
            "w", suffix=".html", encoding="utf-8", delete=False
        ) as tmp:
            tmp.write(html)
            tmp_path = Path(tmp.name)
        try:
            assembled = build(tmp_path, theme)
        finally:
            tmp_path.unlink(missing_ok=True)
        if "@@INLINE" in assembled or "@@BODY" in assembled or "@@TITLE" in assembled:
            sys.exit(f"unresolved marker in {slug}")
        (EX / f"{slug}.html").write_text(assembled, encoding="utf-8")
        print(f"  {slug}.html ({theme}, {len(assembled):,} bytes)")


def build_documents() -> None:
    print("assembling documents")
    assemble_longform()
    for out, (template, theme) in DOCUMENTS.items():
        target = EX / out
        if not run([
            sys.executable, "scripts/build_document.py",
            str(ROOT / "templates" / template), "--theme", theme, "--out", str(target),
        ]):
            sys.exit(f"failed to assemble {out}")

        html = target.read_text(encoding="utf-8")

        # gallery.html uses named slots; the report uses positional ones.
        if out.startswith("gallery"):
            gallery_figs = [f for f in CHARTS if not f.endswith("-wide")]
            for slug in gallery_figs + list(DIAGRAMS) + ["platform-architecture"]:
                html = html.replace(f"<!-- @FIG {slug} -->", figure(slug))
        elif out == "inventory-report.html":
            for marker, slug in REPORT_SLOTS:
                replacement = figure(slug)
                if marker.startswith("<div"):
                    replacement = f'<div class="chart-frame">{replacement}</div>'
                html = html.replace(marker, replacement, 1)
        elif out == "capacity-deck.html":
            html = html.replace(
                "<!-- inline the full-width SVG from scripts/render_chart.mjs here -->",
                figure("footprint-by-function-wide"), 1,
            )

        target.write_text(html, encoding="utf-8")
        print(f"  {out} ({theme}, {len(html):,} bytes)")


def main() -> None:
    render_figures()
    build_documents()
    print("\ndone. Screenshot with: python scripts/shoot_examples.py")


if __name__ == "__main__":
    main()
