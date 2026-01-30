from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_stellody.paths import AppPaths, default_paths
from fastapi_stellody.rendering import JinjaPageRenderer
from fastapi_stellody.routers import contact, home, pages, store


def create_app(paths: AppPaths | None = None) -> FastAPI:
    resolved_paths = default_paths() if paths is None else paths

    app = FastAPI(title="Stellody Reimagined Multi-Page")

    app.mount(
        "/static",
        StaticFiles(directory=str(resolved_paths.static_dir)),
        name="static",
    )

    templates = Jinja2Templates(directory=str(resolved_paths.templates_dir))
    app.state.renderer = JinjaPageRenderer(templates=templates)

    app.include_router(home.router)
    app.include_router(pages.router)
    app.include_router(contact.router)
    app.include_router(store.router)

    return app
