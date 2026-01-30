from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path
import types

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SITE_PY = PROJECT_ROOT / "site.py"


def _load_site_entrypoint() -> types.ModuleType:
    """Load the project's `site.py` (not Python's stdlib `site` module)."""

    spec = importlib.util.spec_from_file_location("stellody_site", SITE_PY)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UvicornStub(types.SimpleNamespace):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[tuple[object, ...], dict[str, object]]] = []

    def run(self, *args: object, **kwargs: object) -> None:
        self.calls.append((args, kwargs))


def test_build_parser_has_expected_defaults() -> None:
    site_entry = _load_site_entrypoint()
    parser = site_entry._build_parser()
    args = parser.parse_args([])

    assert args.host == "127.0.0.1"
    assert args.port == 8000
    assert args.reload is False


def test_main_invokes_uvicorn_with_import_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    site_entry = _load_site_entrypoint()
    uvicorn = UvicornStub()
    monkeypatch.setitem(sys.modules, "uvicorn", uvicorn)

    rc = site_entry.main(["--host", "0.0.0.0", "--port", "1234", "--reload"])

    assert rc == 0
    assert len(uvicorn.calls) == 1

    args, kwargs = uvicorn.calls[0]
    assert args == ("fastapi_stellody.app:app",)
    assert kwargs["host"] == "0.0.0.0"
    assert kwargs["port"] == 1234
    assert kwargs["reload"] is True


def test_running_as_script_exits_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    uvicorn = UvicornStub()
    monkeypatch.setitem(sys.modules, "uvicorn", uvicorn)

    monkeypatch.setattr(sys, "argv", ["site.py"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(SITE_PY), run_name="__main__")

    assert excinfo.value.code == 0
    assert len(uvicorn.calls) == 1
