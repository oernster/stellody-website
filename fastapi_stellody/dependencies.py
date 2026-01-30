from __future__ import annotations

from fastapi import Request

from fastapi_stellody.rendering import PageRenderer


def get_renderer(request: Request) -> PageRenderer:
    return request.app.state.renderer
