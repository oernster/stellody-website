from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from fastapi_stellody.dependencies import get_renderer
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()


@router.get("/cart", response_class=HTMLResponse)
async def cart(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="cart.html", request=request, title="Cart"
    )


@router.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="checkout.html",
        request=request,
        title="Checkout",
    )
