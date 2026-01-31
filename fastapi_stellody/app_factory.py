from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from fastapi_stellody.mail import build_mailer_from_env
from fastapi_stellody.paths import AppPaths, default_paths
from fastapi_stellody.rendering import JinjaPageRenderer
from fastapi_stellody.routers import contact, home, pages, store


def create_app(paths: AppPaths | None = None) -> FastAPI:
    resolved_paths = default_paths() if paths is None else paths

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Shared mail sender (SMTP) configured via Render environment variables.
        # Initialized on startup to avoid import-time failures (tests can override app.state.mailer).
        if getattr(app.state, "mailer", None) is None:
            app.state.mailer = build_mailer_from_env()
        yield

    app = FastAPI(title="Stellody Reimagined Multi-Page", lifespan=lifespan)

    app.mount(
        "/static",
        StaticFiles(directory=str(resolved_paths.static_dir)),
        name="static",
    )

    app.mount(
        "/downloads",
        StaticFiles(directory=str(resolved_paths.downloads_dir)),
        name="downloads",
    )

    templates = Jinja2Templates(directory=str(resolved_paths.templates_dir))
    app.state.renderer = JinjaPageRenderer(templates=templates)

    # Allow tests to set this before lifespan runs.
    app.state.mailer = None

    app.include_router(home.router)
    app.include_router(pages.router)
    app.include_router(contact.router)
    app.include_router(store.router)

    return app
