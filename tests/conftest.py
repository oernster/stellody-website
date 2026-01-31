from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from fastapi_stellody.mail import Mailer
from fastapi_stellody.app_factory import create_app


class _FakeFastMail:
    async def send_message(self, *_args, **_kwargs) -> None:
        return None


@pytest.fixture()
def client() -> TestClient:
    # Ensure app startup can build mail config in tests (values are placeholders).
    os.environ.setdefault("MAIL_USERNAME", "test")
    os.environ.setdefault("MAIL_PASSWORD", "test")
    os.environ.setdefault("MAIL_FROM", "no-reply@example.com")
    os.environ.setdefault("MAIL_SERVER", "smtp.example.com")
    os.environ.setdefault("MAIL_PORT", "587")
    os.environ.setdefault("MAIL_TLS", "true")
    os.environ.setdefault("MAIL_SSL", "false")
    os.environ.setdefault("CONTACT_RECIPIENT", "recipient@example.com")

    app = create_app()

    # Avoid network access in tests.
    app.state.mailer = Mailer(
        fastmail=_FakeFastMail(),
        contact_recipient=os.environ["CONTACT_RECIPIENT"],
    )
    return TestClient(app)
