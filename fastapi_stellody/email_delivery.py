from __future__ import annotations

import html
import inspect
import os
from dataclasses import dataclass

import resend
from starlette.concurrency import run_in_threadpool


def _get_env_required(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not value.strip():
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Configure it in Render (Environment) before deploying."
        )
    return value


@dataclass(frozen=True)
class ResendEmailSender:
    api_key: str
    contact_recipient: str
    # Use a verified sender when available (configurable via RESEND_FROM).
    from_address: str = "Stellody Contact <no-reply@stellody.com>"

    async def send_contact_email(self, *, name: str, email: str, message: str) -> None:
        resend.api_key = self.api_key

        safe_name = html.escape(name)
        safe_email = html.escape(email)
        safe_message = html.escape(message).replace("\n", "<br>")

        payload = {
            "from": self.from_address,
            "to": self.contact_recipient,
            "subject": f"New Contact from {name}",
            "reply_to": email,
            "html": (
                f"<p><strong>Name:</strong> {safe_name}</p>"
                f"<p><strong>Email:</strong> {safe_email}</p>"
                f"<p>{safe_message}</p>"
            ),
        }

        # The resend Python client may be sync; run it in a threadpool unless it
        # becomes async in future versions.
        if inspect.iscoroutinefunction(resend.Emails.send):
            await resend.Emails.send(payload)
        else:
            await run_in_threadpool(resend.Emails.send, payload)


def build_resend_sender_from_env() -> ResendEmailSender:
    return ResendEmailSender(
        api_key=_get_env_required("RESEND_API_KEY"),
        contact_recipient=_get_env_required("CONTACT_RECIPIENT"),
        from_address=os.environ.get(
            "RESEND_FROM",
            "Stellody Contact <no-reply@stellody.com>",
        ),
    )
