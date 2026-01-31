from __future__ import annotations

from fastapi import Request

from fastapi_stellody.email_delivery import ResendEmailSender
from fastapi_stellody.rendering import PageRenderer


def get_renderer(request: Request) -> PageRenderer:
    return request.app.state.renderer


def get_email_sender(request: Request) -> ResendEmailSender:
    sender = getattr(request.app.state, "email_sender", None)
    if sender is None:
        raise RuntimeError("Email sender is not configured.")
    return sender
