from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> RedirectResponse:
    """Serve the favicon at the conventional root path.

    Browsers commonly request /favicon.ico automatically even if the HTML points
    at a different icon URL.
    """

    return RedirectResponse(url="/static/favicon.ico", status_code=308)


@router.get("/product/stellody", include_in_schema=False)
@router.get("/product/stellody/", include_in_schema=False)
async def legacy_product_stellody() -> RedirectResponse:
    """Legacy product URL kept for backwards compatibility.

    Older links (and potential external references) may point to this path.
    """

    return RedirectResponse(url="/pricing", status_code=308)

