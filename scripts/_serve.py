"""Serve a directory over localhost for the browser-driven scripts.

    from _serve import serve
    httpd, base = serve(ROOT)            # any free port
    ...
    httpd.shutdown()

A file:// page cannot load the Google Fonts stylesheet consistently, so a
screenshot or a measurement taken from one shows fallback metrics rather than
what a reader sees. Serving the directory also lets pages resolve relative
links such as ../docs/screenshots/thumbs/.

Standard library only.
"""

from __future__ import annotations

import functools
import http.server
import socketserver
import threading
from pathlib import Path


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler logs every request to stderr; that noise buries
    the one line per page that the caller actually wants to see."""

    def log_message(self, *args) -> None:  # noqa: D102
        pass


def serve(directory: Path, port: int = 0) -> tuple[socketserver.TCPServer, str]:
    """Serve `directory` on 127.0.0.1 in a daemon thread.

    Port 0 asks the OS for a free port. Returns the server (call `shutdown()`
    when done) and its base URL without a trailing slash.
    """
    handler = functools.partial(QuietHandler, directory=str(directory))
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"
