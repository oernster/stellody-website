from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_mail import MessageSchema

from fastapi_stellody.dependencies import get_mailer, get_renderer
from fastapi_stellody.mail import Mailer
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
    email: str = Form(...),
    msg: str = Form(...),
    mailer: Mailer = Depends(get_mailer),
):
    """Send contact form submission via SMTP.

    - Recipient is configured via CONTACT_RECIPIENT env var (never shown on frontend).
    - Reply-To is set to the submitter's email.
    """

    body = (
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        "Message:\n"
        f"{msg}\n"
    )

    message = MessageSchema(
        subject="New message from stellody.com",
        recipients=[mailer.contact_recipient],
        body=body,
        subtype="plain",
        headers={"Reply-To": email},
    )

    try:
        await mailer.fastmail.send_message(message)
    except Exception as exc:
        # Do not log message contents.
        logger.error(
            "Contact email send failed (%s)",
            type(exc).__name__,
            exc_info=True,
        )
        return RedirectResponse(url="/contact?error=1", status_code=303)

    return RedirectResponse(url="/contact?sent=1", status_code=303)
