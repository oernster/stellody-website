from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from fastapi_stellody.app_factory import create_app


class _FakeEmailSender:
    async def send_contact_email(self, *, name: str, email: str, message: str) -> None:
        _ = (name, email, message)
        return None


@pytest.fixture()
def client() -> TestClient:
    # Ensure app startup can build email sender config in tests (values are
    # placeholders).
    os.environ.setdefault("RESEND_API_KEY", "test")
    os.environ.setdefault("CONTACT_RECIPIENT", "recipient@example.com")
    os.environ.setdefault("SESSION_SECRET", "test-session-secret")

    app = create_app()

    # Avoid network access in tests.
    app.state.email_sender = _FakeEmailSender()
    return TestClient(app)
