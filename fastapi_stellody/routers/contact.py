from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import EmailStr

from fastapi_stellody.dependencies import get_email_sender, get_renderer
from fastapi_stellody.email_delivery import ResendEmailSender
from fastapi_stellody.rendering import PageRenderer

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request, renderer: PageRenderer = Depends(get_renderer)):
    return renderer.render_page(
        template_name="contact.html", request=request, title="Contact"
    )


@router.post("/contact")
async def contact_post(
    name: str = Form(...),
    email: EmailStr = Form(...),
    message: str = Form(...),
    email_sender: ResendEmailSender = Depends(get_email_sender),
):
    """Send contact form submission via Resend.

    - Recipient is configured via CONTACT_RECIPIENT env var (never shown on frontend).
    - Reply-To is set to the submitter's email.
    """

    try:
        await email_sender.send_contact_email(
            name=name,
            email=str(email),
            message=message,
        )
    except Exception as exc:
        # Do not log message contents.
        logger.error(
            "Contact email send failed (%s)",
            type(exc).__name__,
            exc_info=True,
        )
        return RedirectResponse(url="/contact?error=1", status_code=303)

    return RedirectResponse(url="/contact?sent=1", status_code=303)
