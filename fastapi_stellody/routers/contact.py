from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi_stellody.dependencies import get_renderer
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="contact.html", request=request, title="Contact"
    )


@router.post("/contact")
async def contact_post(
    name: str = Form(...),
    email: str = Form(...),
    msg: str = Form(...),
):
    """Placeholder form handler.

    In a real site you would send an email, persist to a DB, or create a support ticket.
    """

    _ = (name, email, msg)
    return RedirectResponse(url="/", status_code=303)
