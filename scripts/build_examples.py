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

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"

# figure slug -> (renderer, spec, extra args)
CHARTS = {
    "footprint-by-function": "specs/footprint.json",
    "cohorts-by-year": "specs/cohorts.json",
    "latency-p99": "specs/latency.json",
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
    "platform-rfc.html": ("longform.html", "field-notes"),
    "capacity-deck.html": ("deck.html", "executive-navy"),
    "gallery.html": ("gallery.html", "editorial-coral"),
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


def build_documents() -> None:
    print("assembling documents")
    for out, (template, theme) in DOCUMENTS.items():
        target = EX / out
        if not run([
            sys.executable, "scripts/build_document.py",
            str(ROOT / "templates" / template), "--theme", theme, "--out", str(target),
        ]):
            sys.exit(f"failed to assemble {out}")

        html = target.read_text(encoding="utf-8")

        # gallery.html uses named slots; the report uses positional ones.
        if out == "gallery.html":
            for slug in list(CHARTS) + list(DIAGRAMS) + ["platform-architecture"]:
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
                figure("footprint-by-function"), 1,
            )

        target.write_text(html, encoding="utf-8")
        print(f"  {out} ({theme}, {len(html):,} bytes)")


def main() -> None:
    render_figures()
    build_documents()
    print("\ndone. Screenshot with: python scripts/shoot_examples.py")


if __name__ == "__main__":
    main()
