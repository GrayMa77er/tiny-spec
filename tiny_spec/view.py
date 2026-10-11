"""``tiny-spec view`` — a local, read-only page over :mod:`tiny_spec.state`.

Serves one self-contained HTML page and a ``/state.json`` endpoint that re-derives the
state from git on every request. Nothing is cached or written: close the tab and there
is nothing to clean up. Binds to 127.0.0.1 only.
"""

from __future__ import annotations

import json
import webbrowser
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.resources import files
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from tiny_spec.state import derive


class _Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, root: Path, page: bytes, **kwargs):
        self.root = root
        self.page = page
        super().__init__(*args, **kwargs)

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 — http.server's naming
        url = urlparse(self.path)
        if url.path == "/":
            self._send(200, self.page, "text/html; charset=utf-8")
        elif url.path == "/state.json":
            remote = parse_qs(url.query).get("remote", ["0"])[0] == "1"
            body = json.dumps(derive(self.root, remote=remote)).encode()
            self._send(200, body, "application/json")
        else:
            self._send(404, b"not found", "text/plain")

    def log_message(self, *_args) -> None:  # keep the terminal quiet
        pass


def serve(root: Path, port: int, open_browser: bool) -> int:
    page = files("tiny_spec").joinpath("view.html").read_bytes()
    handler = partial(_Handler, root=root.resolve(), page=page)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"tiny-spec view — {root.resolve()}\n  {url}\n  Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0
