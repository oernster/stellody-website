from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from fastapi_stellody.app_factory import create_app
from fastapi_stellody.dependencies import get_email_sender
import fastapi_stellody.email_delivery as email_delivery
from fastapi_stellody.email_delivery import _get_env_required, build_resend_sender_from_env


def test_app_module_exports_asgi_app() -> None:
    # Cover [`fastapi_stellody/app.py`](fastapi_stellody/app.py:1).
    module = importlib.import_module("fastapi_stellody.app")
    assert getattr(module, "app") is not None


def test_required_env_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("X_REQUIRED", raising=False)
    with pytest.raises(RuntimeError):
        _get_env_required("X_REQUIRED")

    monkeypatch.setenv("X_REQUIRED", "")
    with pytest.raises(RuntimeError):
        _get_env_required("X_REQUIRED")

    monkeypatch.setenv("X_REQUIRED", "  ok  ")
    assert _get_env_required("X_REQUIRED") == "  ok  "


def test_build_resend_sender_from_env_success(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESEND_API_KEY", "key")
    monkeypatch.setenv("CONTACT_RECIPIENT", "recipient@example.com")

    sender = build_resend_sender_from_env()
    assert sender.contact_recipient == "recipient@example.com"


def test_send_contact_email_runs_sync_client_in_threadpool(monkeypatch: pytest.MonkeyPatch) -> None:
    # Exercise the non-async code path in [`ResendEmailSender.send_contact_email()`](fastapi_stellody/email_delivery.py:24).
    monkeypatch.setattr(email_delivery.resend, "api_key", None)

    calls: list[dict[str, object]] = []

    class _Emails:
        @staticmethod
        def send(payload: dict[str, object]) -> dict[str, object]:
            calls.append(payload)
            return {"id": "test"}

    monkeypatch.setattr(email_delivery.resend, "Emails", _Emails)

    sender = email_delivery.ResendEmailSender(
        api_key="k",
        contact_recipient="recipient@example.com",
        from_address="Stellody Contact <no-reply@stellody.com>",
    )

    # Includes characters that must be escaped.
    name = "A&B"
    email = "user@example.com"
    message = "Line1\nLine2 <tag>"

    import asyncio

    asyncio.run(sender.send_contact_email(name=name, email=email, message=message))

    assert len(calls) == 1
    payload = calls[0]
    assert payload["from"] == "Stellody Contact <no-reply@stellody.com>"
    assert payload["to"] == "recipient@example.com"
    assert payload["reply_to"] == email
    assert "A&amp;B" in str(payload["html"])
    assert "Line2 &lt;tag&gt;" in str(payload["html"])


def test_send_contact_email_awaits_async_client(monkeypatch: pytest.MonkeyPatch) -> None:
    # Exercise the coroutine path in [`ResendEmailSender.send_contact_email()`](fastapi_stellody/email_delivery.py:49).
    calls: list[dict[str, object]] = []

    class _Emails:
        @staticmethod
        async def send(payload: dict[str, object]) -> dict[str, object]:
            calls.append(payload)
            return {"id": "async"}

    monkeypatch.setattr(email_delivery.resend, "Emails", _Emails)

    sender = email_delivery.ResendEmailSender(
        api_key="k",
        contact_recipient="recipient@example.com",
        from_address="Stellody Contact <no-reply@stellody.com>",
    )

    import asyncio

    asyncio.run(sender.send_contact_email(name="N", email="e@example.com", message="M"))
    assert len(calls) == 1


def test_startup_initializes_email_sender_when_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RESEND_API_KEY", "key")
    monkeypatch.setenv("CONTACT_RECIPIENT", "recipient@example.com")

    app = create_app()
    assert getattr(app.state, "email_sender") is None

    with TestClient(app) as client:
        # Trigger at least one request to ensure lifespan is active.
        response = client.get("/")
        assert response.status_code == 200

    assert getattr(app.state, "email_sender") is not None


def test_startup_does_not_override_existing_email_sender(monkeypatch: pytest.MonkeyPatch) -> None:
    # If tests or other code set app.state.email_sender before startup, startup should not override it.
    monkeypatch.setenv("RESEND_API_KEY", "key")
    monkeypatch.setenv("CONTACT_RECIPIENT", "recipient@example.com")

    app = create_app()
    sentinel = object()
    app.state.email_sender = sentinel

    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200

    assert app.state.email_sender is sentinel


def test_get_email_sender_raises_when_not_configured() -> None:
    class _State:
        email_sender = None

    class _App:
        state = _State()

    class _Request:
        app = _App()

    with pytest.raises(RuntimeError):
        get_email_sender(_Request())

