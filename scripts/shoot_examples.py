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
    "longform-rfc": ("platform-rfc.html", (1280, 980), False),
    "deck": ("capacity-deck.html", (1280, 760), False),
    "gallery": ("gallery.html", (1280, 1430), True),
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
                page = browser.new_page(viewport={"width": w, "height": h},
                                        device_scale_factor=2)
                page.goto(f"http://127.0.0.1:{PORT}/{page_file}", wait_until="networkidle")
                # Web fonts render as fallbacks if the shot is taken before they
                # load, and the result looks subtly wrong in a way that is easy
                # to miss in a thumbnail.
                page.evaluate("document.fonts.ready")
                target = OUT / f"{name}.png"
                page.screenshot(path=str(target), full_page=full)
                print(f"  {target.relative_to(ROOT)}")
                page.close()
            browser.close()
    finally:
        httpd.shutdown()

    print(f"\nwrote {len(SHOTS)} screenshots to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
