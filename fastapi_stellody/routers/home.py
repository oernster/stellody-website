from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from fastapi_stellody.dependencies import get_renderer
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="home.html",
        request=request,
        # Homepage SEO title should be explicit and keyword-rich.
        title="Home",
        # NOTE: base.html uses og_title for the document <title>.
        og_title="Stellody | Spotify Playlist Generator for Local and Streaming Music",
        meta_description=(
            "Generate genre-sorted Spotify and local music playlists effortlessly. "
            "Stellody works with Spotify Free and Premium and local music files."
        ),
    )
