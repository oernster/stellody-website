from __future__ import annotations

from fastapi import Request

from fastapi_stellody.mail import Mailer
from fastapi_stellody.rendering import PageRenderer


def get_renderer(request: Request) -> PageRenderer:
    return request.app.state.renderer


def get_mailer(request: Request) -> Mailer:
    mailer = getattr(request.app.state, "mailer", None)
    if mailer is None:
        raise RuntimeError(
            "Mailer is not configured. Ensure MAIL_* and CONTACT_RECIPIENT environment variables are set."
        )
    return mailer
