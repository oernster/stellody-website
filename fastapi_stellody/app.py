"""App module exporting the ASGI application used by Uvicorn."""

from __future__ import annotations

from fastapi_stellody.app_factory import create_app

app = create_app()
