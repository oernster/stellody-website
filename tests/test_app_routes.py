from __future__ import annotations

from fastapi.testclient import TestClient

from fastapi_stellody.app_factory import create_app
from fastapi_stellody.paths import default_paths


def test_placeholder_page_renders(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

    html = response.text
    assert "<title>Stellody</title>" in html
    assert "<h1>Stellody</h1>" in html
    assert "on its way" in html
    # The sunny scene (fields and trees) is rendered inline as SVG.
    assert "<svg" in html and 'class="scene"' in html


def test_create_app_accepts_explicit_paths() -> None:
    # Covers the branch where paths are supplied rather than defaulted.
    app = create_app(paths=default_paths())
    client = TestClient(app)

    response = client.get("/")
    assert response.status_code == 200
    assert "<h1>Stellody</h1>" in response.text


def test_favicon_is_served(client: TestClient) -> None:
    response = client.get("/static/favicon.ico")

    assert response.status_code == 200
    assert response.content  # non-empty asset


def test_asgi_entrypoint_exposes_app() -> None:
    # Guards the module Render/Uvicorn imports: fastapi_stellody.app:app.
    from fastapi import FastAPI

    from fastapi_stellody import app as app_module

    assert isinstance(app_module.app, FastAPI)
