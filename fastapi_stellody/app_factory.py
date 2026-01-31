from __future__ import annotations

from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from fastapi_stellody.email_delivery import build_resend_sender_from_env
from fastapi_stellody.paths import AppPaths, default_paths
from fastapi_stellody.rendering import JinjaPageRenderer
from fastapi_stellody.routers import contact, downloads, home, pages, store
from fastapi_stellody.routers import seo_assets


def create_app(paths: AppPaths | None = None) -> FastAPI:
    resolved_paths = default_paths() if paths is None else paths

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Shared email sender (Resend) configured via Render environment variables.
        # Initialized on startup to avoid import-time failures (tests can override
        # app.state.email_sender).
        if getattr(app.state, "email_sender", None) is None:
            app.state.email_sender = build_resend_sender_from_env()
        yield

    app = FastAPI(title="Stellody Reimagined Multi-Page", lifespan=lifespan)

    # Cookie-backed session support (used for the simple cart flow).
    # Required: set SESSION_SECRET to a long random value.
    session_secret = os.environ.get("SESSION_SECRET")
    if not session_secret:
        raise RuntimeError("SESSION_SECRET must be set (used to sign session cookies).")
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        same_site="lax",
    )

    app.mount(
        "/static",
        StaticFiles(directory=str(resolved_paths.static_dir)),
        name="static",
    )

    templates = Jinja2Templates(directory=str(resolved_paths.templates_dir))
    app.state.renderer = JinjaPageRenderer(templates=templates)

    # Allow tests to set this before lifespan runs.
    app.state.email_sender = None

    app.include_router(home.router)
    app.include_router(pages.router)
    app.include_router(contact.router)
    app.include_router(store.router)
    app.include_router(seo_assets.router)
    app.include_router(downloads.router)

    return app
