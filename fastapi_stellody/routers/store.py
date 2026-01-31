from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi_stellody.dependencies import get_renderer
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()


LicenseType = Literal["standard", "pro"]


@dataclass(frozen=True)
class LicenseOption:
    key: LicenseType
    name: str
    price_gbp: int
    paypal_url: str


LICENSE_OPTIONS: dict[LicenseType, LicenseOption] = {
    "standard": LicenseOption(
        key="standard",
        name="Standard License",
        price_gbp=25,
        paypal_url="https://www.paypal.com/ncp/payment/EXJ35PLE2CTF2",
    ),
    "pro": LicenseOption(
        key="pro",
        name="Pro License",
        price_gbp=50,
        paypal_url="https://www.paypal.com/ncp/payment/AQRY5CDP4Z344",
    ),
}


CART_SESSION_KEY = "cart_license"


@router.get("/cart", response_class=HTMLResponse)
async def cart(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    selected_key = request.session.get(CART_SESSION_KEY)
    selected: LicenseOption | None = None
    if selected_key in LICENSE_OPTIONS:
        selected = LICENSE_OPTIONS[selected_key]

    return renderer.render_page(
        template_name="cart.html",
        request=request,
        title="Cart",
        selected=selected,
    )


@router.post("/add-to-cart")
async def add_to_cart(
    request: Request, license_type: str = Form(...)
) -> RedirectResponse:
    # Only one license allowed at a time: replace existing selection.
    if license_type in LICENSE_OPTIONS:
        request.session[CART_SESSION_KEY] = license_type

    return RedirectResponse(url="/cart", status_code=303)


@router.post("/cart/clear")
async def clear_cart(request: Request) -> RedirectResponse:
    request.session.pop(CART_SESSION_KEY, None)
    return RedirectResponse(url="/cart", status_code=303)


@router.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="checkout.html",
        request=request,
        title="Checkout",
    )
