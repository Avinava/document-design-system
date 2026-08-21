#!/usr/bin/env python3
"""Screenshot the built examples into docs/screenshots/ for the README.

    pip install playwright && playwright install chromium
    python scripts/build_examples.py
    python scripts/shoot_examples.py

Serves examples/ over localhost rather than using file:// URLs — a file:// page
cannot load the Google Fonts stylesheet consistently, and the screenshots would
show fallback metrics rather than what a reader sees.
"""

from __future__ import annotations

import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
OUT = ROOT / "docs" / "screenshots"
PORT = 8931

# name -> (page, viewport, full_page)
#
# Prefer a framed viewport over full_page for the prose documents. A full-page
# capture of a real report is ~2500 CSS px tall, which renders in a README as an
# unreadable sliver — the point of these is to show what the system looks like,
# not to reproduce the whole document.
SHOTS = {
    "analytical-report": ("inventory-report.html", (1280, 980), False),
    "analytical-report-detail": ("inventory-report.html", (1280, 980), False),
    "design-doc": ("design-doc.html", (1280, 980), False),
    "adr": ("adr.html", (1280, 720), False),
    "spec": ("spec.html", (1280, 980), False),
    "api-contract": ("api-contract.html", (1280, 980), False),
    "architecture": ("architecture.html", (1280, 980), False),
    "handoff": ("handoff.html", (1280, 980), False),
    "design-handoff": ("design-handoff.html", (1280, 980), False),
    "discovery": ("discovery.html", (1280, 980), False),
    "test-report": ("test-report.html", (1280, 980), False),
    "postmortem": ("postmortem.html", (1280, 980), False),
    "proposal": ("proposal.html", (1280, 800), False),
    "runbook": ("runbook.html", (1280, 980), False),
    "onboarding": ("onboarding.html", (1280, 900), False),
    "tutorial": ("tutorial.html", (1280, 900), False),
    "how-to": ("how-to.html", (1280, 800), False),
    "reference": ("reference.html", (1280, 800), False),
    "explanation": ("explanation.html", (1280, 800), False),
    "mulesoft": ("mulesoft.html", (1280, 900), False),
    # Light/dark pairs, for the README <picture> elements that follow the
    # reader's GitHub theme.
    "gallery-light": ("gallery-light.html", (1280, 1430), True),
    "gallery-dark": ("gallery-dark.html", (1280, 1430), True),
    "themes-light": ("themes-light.html", (1280, 760), False),
    "themes-dark": ("themes-dark.html", (1280, 760), False),
}

# Scroll offset in CSS pixels, for shots that should show a section further
# down the page than the header.
SCROLL = {"analytical-report-detail": 1128}

# name -> (page, zero-based slide index)
#
# Slides are captured as elements rather than viewports. A deck's title slide is
# deliberately sparse — one idea per slide — so a viewport shot of page one is
# mostly empty paper and tells a reader nothing about the system.
SLIDE_SHOTS = {
    "deck-title": ("capacity-deck.html", 0),
    "deck-statement": ("capacity-deck.html", 2),
    "deck-divider": ("capacity-deck.html", 3),
    "deck-table": ("capacity-deck.html", 4),
    "deck-metric": ("capacity-deck.html", 5),
    "deck-chart": ("capacity-deck.html", 6),
    "deck-diagram": ("capacity-deck.html", 7),
    "deck-compare": ("capacity-deck.html", 10),
    "deck-close": ("capacity-deck.html", 13),
}


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler logs every request to stderr; that noise buries
    the one line per screenshot that the caller actually wants to see."""

    def log_message(self, *args) -> None:  # noqa: D102
        pass


def serve() -> socketserver.TCPServer:
    handler = functools.partial(QuietHandler, directory=str(EX))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main() -> None:
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit(
            "playwright is not installed.\n"
            "  pip install playwright && playwright install chromium\n"
            "It is an authoring-time dependency only."
        )

    OUT.mkdir(parents=True, exist_ok=True)
    httpd = serve()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()

            for name, (page_file, (w, h), full) in SHOTS.items():
                if only and name not in only:
                    continue
                page = browser.new_page(viewport={"width": w, "height": h},
                                        device_scale_factor=2)
                page.goto(f"http://127.0.0.1:{PORT}/{page_file}", wait_until="networkidle")
                # Web fonts render as fallbacks if the shot is taken before they
                # load, and the result looks subtly wrong in a way that is easy
                # to miss in a thumbnail.
                page.evaluate("document.fonts.ready")
                if name in SCROLL:
                    page.evaluate(f"window.scrollTo(0, {SCROLL[name]})")
                    page.wait_for_timeout(200)
                target = OUT / f"{name}.png"
                page.screenshot(path=str(target), full_page=full)
                print(f"  {target.relative_to(ROOT)}")
                page.close()

            for name, (page_file, index) in SLIDE_SHOTS.items():
                if only and name not in only:
                    continue
                page = browser.new_page(viewport={"width": 1280, "height": 760},
                                        device_scale_factor=2)
                page.goto(f"http://127.0.0.1:{PORT}/{page_file}", wait_until="networkidle")
                page.evaluate("document.fonts.ready")
                slide = page.locator("section.slide").nth(index)
                slide.scroll_into_view_if_needed()
                page.wait_for_timeout(200)
                target = OUT / f"{name}.png"
                slide.screenshot(path=str(target))
                print(f"  {target.relative_to(ROOT)}")
                page.close()

            browser.close()
    finally:
        httpd.shutdown()

    print(f"\nwrote {len(SHOTS) + len(SLIDE_SHOTS)} screenshots to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
