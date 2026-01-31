"""Shim entrypoint for running the Stellody FastAPI site.

Run:

    python site.py

This starts a local Uvicorn server for the FastAPI app defined in
`fastapi_stellody/app.py`.
"""

from __future__ import annotations

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Stellody FastAPI site.")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Bind host (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8004,
        help="Bind port (default: 8004)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development (default: off)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        import uvicorn
    except Exception as exc:  # pragma: no cover
        print(
            "Missing dependency: uvicorn. Install dependencies first, e.g.\n"
            "  python -m pip install -r fastapi_stellody/requirements.txt",
            file=sys.stderr,
        )
        print(f"\nOriginal error: {exc}", file=sys.stderr)
        return 1

    # Use an import string so Uvicorn can manage reloading correctly.
    uvicorn.run(
        "fastapi_stellody.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
