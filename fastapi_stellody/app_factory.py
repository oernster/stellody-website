from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_stellody.paths import AppPaths, default_paths

APP_TITLE = "Stellody"
PLACEHOLDER_TEMPLATE = "index.html"


def create_app(paths: AppPaths | None = None) -> FastAPI:
    resolved_paths = default_paths() if paths is None else paths

    app = FastAPI(title=APP_TITLE)

    app.mount(
        "/static",
        StaticFiles(directory=str(resolved_paths.static_dir)),
        name="static",
    )

    templates = Jinja2Templates(directory=str(resolved_paths.templates_dir))

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse(
            request,
            PLACEHOLDER_TEMPLATE,
            {"title": APP_TITLE},
        )

    return app
