"""Allow running the test suite via `python tests ...`.

Example:

    python tests -v --cov
"""

from __future__ import annotations

import sys

import pytest


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(main())
