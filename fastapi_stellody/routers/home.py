from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from fastapi_stellody.dependencies import get_renderer
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="home.html", request=request, title="Home"
    )
