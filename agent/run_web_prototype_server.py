"""Serve Stage 8 static prototype locally."""

from __future__ import annotations

import argparse
import http.server
import socketserver
from pathlib import Path

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
STATIC_ROOT = Path("web_prototype") / "static"


def parse_args() -> argparse.Namespace:
    """Parse CLI options for local static server launch."""

    parser = argparse.ArgumentParser(description="Run local server for Stage 8 static prototype")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Host to bind (default: {DEFAULT_HOST}).")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port to bind (default: {DEFAULT_PORT}).")
    return parser.parse_args()


def build_handler(web_root: Path) -> type[http.server.SimpleHTTPRequestHandler]:
    """Return a static-file handler pinned to the provided web root."""

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **handler_kwargs):
            super().__init__(*handler_args, directory=str(web_root), **handler_kwargs)

    return Handler


def main() -> int:
    """Serve static Stage 8 prototype files over HTTP."""

    args = parse_args()
    if not STATIC_ROOT.exists():
        raise SystemExit(f"missing prototype static directory: {STATIC_ROOT}")

    handler_cls = build_handler(STATIC_ROOT)
    with socketserver.TCPServer((args.host, args.port), handler_cls) as httpd:
        print(f"web_prototype_url=http://{args.host}:{args.port}/index.html")
        httpd.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())

