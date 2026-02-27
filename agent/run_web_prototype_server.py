"""Serve Stage 8 static prototype locally."""

from __future__ import annotations

import argparse
import http.server
import socketserver
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local server for Stage 8 static prototype")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind (default: 8765).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    web_root = Path("web_prototype") / "static"
    if not web_root.exists():
        raise SystemExit(f"missing prototype static directory: {web_root}")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *handler_args, **handler_kwargs):
            super().__init__(*handler_args, directory=str(web_root), **handler_kwargs)

    with socketserver.TCPServer((args.host, args.port), Handler) as httpd:
        print(f"web_prototype_url=http://{args.host}:{args.port}/index.html")
        httpd.serve_forever()


if __name__ == "__main__":
    raise SystemExit(main())

